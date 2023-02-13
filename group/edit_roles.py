from flask import request
from database.models import Group, User
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource
from resources.errors import *
from resources.exists import group_exists, user_exists_in_group
from mongoengine.errors import InvalidQueryError


class EditRoles(Resource):
    @jwt_required()
    def put(self, group_name):
        try:
            identity = get_jwt_identity()
            user = User.objects.get(id=identity)
            edit_user = request.json.get("user")
            edit_role = request.json.get("edit_role")
            if group_exists(group_name):
                group = Group.objects.get(name=group_name)
                if user_exists_in_group(edit_user, group_name):
                    get_user = User.objects.get(username=edit_user)
                    if edit_user == group.created_by:
                        return "Cannot edit the role of group creator"
                else:
                    return "User doesnot exist in the group"
            else:
                return "Group doesnot exist"
            if user['username'] in group['admins']:
                for role in ['admins', 'moderators', 'members']:
                    for index in range(len(group[role])):
                        if group[role][index] == edit_user:
                            print(group[role][index])
                            del group[role][index]
                            group.save()
                            if edit_role == 'MEMBER':
                                group.update(push__members=edit_user)
                            elif edit_role == 'MODERATOR':
                                group.update(push__moderators=edit_user)
                            elif edit_role == 'ADMIN':
                                group.update(push__admins=edit_user)
                            else:
                                return "Invalid role given"
                            for role_index in range(len(get_user['roles'])):
                                if get_user['roles'][role_index]['group_id'] == group.id:
                                    get_user['roles'][role_index].update(role=edit_role)
                                    get_user.save()
                                    return "User {}'s role has been updated to {}".format(edit_user, edit_role)
            else:
                return "Only admins have permission to edit the roles"
        except InvalidQueryError:
            raise SchemaValidationError
