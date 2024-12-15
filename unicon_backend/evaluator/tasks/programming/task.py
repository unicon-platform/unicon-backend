from collections import Counter
from functools import cached_property
from logging import getLogger
from typing import Any, Literal, Self

from pydantic import BaseModel, RootModel, model_validator

from unicon_backend.evaluator.tasks import Task, TaskEvalResult, TaskEvalStatus, TaskType
from unicon_backend.evaluator.tasks.programming.artifact import File, PrimitiveData
from unicon_backend.evaluator.tasks.programming.runner import (
    RunnerEnvironment,
    RunnerPackage,
    RunnerRequest,
    SubmissionId,
)
from unicon_backend.evaluator.tasks.programming.security import mpi_sandbox
from unicon_backend.evaluator.tasks.programming.steps import (
    ComputeGraph,
    InputStep,
    StepSocket,
    StepType,
)
from unicon_backend.workers.publisher import task_publisher

logger = getLogger(__name__)

USER_INPUT_STEP_ID: int = 0


class Testcase(ComputeGraph):
    id: int

    @cached_property
    def socket_type_counts(self) -> Counter[str]:
        return Counter(socket.type for socket in self.nodes)

    @model_validator(mode="after")
    def check_exactly_one_output_step(self) -> Self:
        output_step_count = self.socket_type_counts[StepType.OUTPUT.value]
        if output_step_count != 1:
            raise ValueError(f"Expected exactly 1 output step, found {output_step_count}")
        return self


class RequiredInput(BaseModel):
    id: str
    data: PrimitiveData | File


class ProgrammingTask(Task[list[RequiredInput], SubmissionId]):
    type: Literal[TaskType.PROGRAMMING]
    question: str
    environment: RunnerEnvironment
    required_inputs: list[RequiredInput]
    testcases: list[Testcase]

    def create_input_step(self, user_inputs: list[RequiredInput]) -> InputStep:
        """
        Transform user input into InputStep
        This is so that we simply treat it as a node in the graph
        NOTE: We assume that the id of user inputs is always 0
        """
        return InputStep(
            id=USER_INPUT_STEP_ID,
            inputs=[],
            outputs=[
                StepSocket(id=str(user_input.id), data=user_input.data)
                for user_input in user_inputs
            ],
            type=StepType.INPUT,
        )

    def run(self, user_inputs: list[RequiredInput]) -> TaskEvalResult[SubmissionId]:
        # Check if all required inputs are provided
        for required_input in self.required_inputs:
            if not any(required_input.id == user_input.id for user_input in user_inputs):
                raise ValueError(f"Required input {required_input.id} not provided")

        user_input_files: list[File] = [
            user_input.data for user_input in user_inputs if isinstance(user_input.data, File)
        ]

        runner_packages: list[RunnerPackage] = []
        for testcase in self.testcases:
            assembled_program = mpi_sandbox(testcase.run(self.create_input_step(user_inputs)))

            logger.debug(f"Assembled Program:\n{assembled_program}")

            graph_files: list[File] = []

            for node in filter(lambda node: node.type == StepType.INPUT, testcase.nodes):
                graph_files.extend(
                    output.data for output in node.outputs if isinstance(output.data, File)
                )

            runner_package = RunnerPackage(
                id=testcase.id,
                entrypoint="__entrypoint.py",
                # TODO: instead of always passing in user_input, we can refactor in the future
                # to let ComputeGraph derive all the files needed to run the testcase
                files=[
                    *user_input_files,
                    *graph_files,
                    File(file_name="__entrypoint.py", content=assembled_program.code),
                ],
            )
            runner_packages.append(runner_package)

        runner_request = RunnerRequest.create(runner_packages, self.environment)
        task_publisher.publish(runner_request.model_dump_json(serialize_as_any=True))

        return TaskEvalResult(
            task_id=self.id, status=TaskEvalStatus.PENDING, result=runner_request.submission_id
        )

    def validate_user_input(self, user_input: Any) -> list[RequiredInput]:
        return RootModel[list[RequiredInput]].model_validate(user_input).root
