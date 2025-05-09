from .roles import UserRoles


class PublicAccess:
    pass


class Group:
    members: frozenset[UserRoles]

    def __init__(self, *members: UserRoles):
        self.members = frozenset(members)


PermissionAcl = UserRoles | Group | PublicAccess


class Permissions:
    __PRIVILEGED = Group(UserRoles.Organizer, UserRoles.Admin)

    UpdateSelf = PublicAccess()
    GetUserMinimalInfo = PublicAccess()
    SearchUserMinimalInfo = PublicAccess()

    GetUserFullInfo = __PRIVILEGED
    UpdateAnyUser = __PRIVILEGED
    BanUser = __PRIVILEGED
    DeleteUser = UserRoles.Admin
    UpdateRole = UserRoles.Admin


def perform_check(acl: PermissionAcl, role: UserRoles) -> bool:
    if isinstance(acl, PublicAccess):
        return True
    elif isinstance(acl, UserRoles):
        return role is acl

    return role in acl.members
