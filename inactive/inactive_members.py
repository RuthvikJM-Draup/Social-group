from database.models import Group, User
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource
from resources.errors import *
from resources.exists import group_exists, user_exists_in_group
from inactive.inactive import inactive_members


class InactiveMembers(Resource):
    @jwt_required()
    def delete(self, group_name):
        try:
            identity = get_jwt_identity()
            user = User.objects.get(id=identity)
            if group_exists(group_name):
                group = Group.objects.get(name=group_name)
                if user_exists_in_group(user.username, group_name):
                    if user.username in group.admins or group.moderators:
                        inactive_members(group_name)
                        return "Inactive members deleted successfully"
                    else:
                        return "Only admins and moderators can delete inactive members"
                else:
                    return "Authenticated user doesnot exist in the group"
            else:
                return "Group doesnot exist"
        except Exception:
            raise InternalServerError
