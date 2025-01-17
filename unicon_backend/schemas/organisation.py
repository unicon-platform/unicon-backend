from unicon_backend.models.organisation import (
    InvitationKeyBase,
    OrganisationBase,
    ProjectBase,
    RoleBase,
)
from unicon_backend.models.problem import ProblemBase


class OrganisationCreate(OrganisationBase):
    pass


class OrganisationUpdate(OrganisationBase):
    pass


class OrganisationPublic(OrganisationBase):
    id: int


class OrganisationPublicWithProjects(OrganisationPublic):
    projects: list["ProjectPublic"]


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(ProjectBase):
    pass


class ProjectPublic(ProjectBase):
    id: int
    roles: list["RolePublic"]


class ProjectPublicWithProblems(ProjectPublic):
    problems: list[ProblemBase]


class RolePublic(RoleBase):
    id: int
    project_id: int


class RoleCreate(RoleBase):
    name: str


class RolePublicWithInvitationKeys(RolePublic):
    invitation_keys: list["InvitationKeyPublic"]


class InvitationKeyPublic(InvitationKeyBase):
    pass
