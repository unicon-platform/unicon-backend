from logging import getLogger
from typing import Any

from pydantic import BaseModel, ConfigDict, SerializeAsAny

from unicon_backend.evaluator.tasks.base import Task, TaskEvalResult

logger = getLogger(__name__)


class ExpectedAnswer(BaseModel):
    task_id: int
    expected_answer: Any


class UserInput(BaseModel):
    task_id: int
    user_input: Any


class Definition(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    description: str
    tasks: list[SerializeAsAny[Task]]

    def run(
        self,
        user_inputs: list[UserInput],
        expected_answers: list[ExpectedAnswer],
        task_id: int | None = None,
    ) -> list[TaskEvalResult]:
        user_input_index: dict[int, UserInput] = {
            user_input.task_id: user_input for user_input in user_inputs
        }
        expected_answer_index: dict[int, ExpectedAnswer] = {
            task_answer.task_id: task_answer for task_answer in expected_answers
        }

        tasks_to_run = (
            self.tasks if task_id is None else [task for task in self.tasks if task.id == task_id]
        )

        result: list[TaskEvalResult] = []

        for task in tasks_to_run:
            if (task_user_input := user_input_index.get(task.id)) is None:
                logger.warning(f"Task {task.id} has no user input")
                continue

            if (task_expected_answer := expected_answer_index.get(task.id)) is None:
                logger.warning(f"Task {task.id} has no answer")

            logger.info(f"Running task {task.id}")

            result.append(
                task.run(
                    task.validate_user_input(task_user_input.user_input),
                    None
                    if task_expected_answer is None
                    else task.validate_expected_answer(task_expected_answer.expected_answer),
                )
            )

        return result
