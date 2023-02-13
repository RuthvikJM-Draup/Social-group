from flask import Response, request
from database.models import Group, User, Post
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource
from resources.errors import *
from resources.exists import group_exists, user_exists_in_group, user_exists
from mongoengine.errors import FieldDoesNotExist, NotUniqueError, ValidationError


class GroupApi(Resource):
    @jwt_required()
    def post(self):
        try:
            identity = get_jwt_identity()
            user = User.objects.get(id=identity)
            name = request.json.get("group_name")
            _type = request.json.get("type")
            creator = request.json.get("creator")
            if user.username == creator:
                group = Group(name=name, type=_type, members=[], moderators=[], admins=[creator], created_by=creator)
                group.save()
                roles = {"group_id": group.id, "role": "ADMIN"}
                user.update(push__roles=roles)
                print(user.to_json())
                return {"message": "Group created successfully"}, 200
            else:
                return {"Creator name not matching username": str(user.username)}
        except (FieldDoesNotExist, ValidationError):
            raise SchemaValidationError
        except NotUniqueError:
            raise DetailsAlreadyExistsError
        except Exception:
            raise InternalServerError


class AddUsers(Resource):
    @jwt_required()
    def post(self, group_name):
        try:
            identity = get_jwt_identity()
            user = User.objects.get(id=identity)
            new_user = request.json.get("user")
            user_role = request.json.get("role")
            if group_exists(group_name):
                group = Group.objects.get(name=group_name)
                if user_exists(new_user):
                    get_user = User.objects.get(username=new_user)
                    for role in ['admins', 'moderators', 'members']:
                        if new_user in group[role]:
                            return "User already exists in the group, Duplicates are not allowed"
                else:
                    return "User doesnot exist, Enter valid new user"
            else:
                return "Group doesnot exist"
            if user['username'] in group['admins'] or group['moderators']:
                if user_role == 'MEMBER':
                    group.update(push__members=new_user)
                    roles = {"group_id": group.id, "role": user_role}
                    get_user.update(push__roles=roles)
                    return "A new member, {} has been added to the group ,{}".format(new_user, group_name)
            if user['username'] in group['admins']:
                if user_role == 'MODERATOR':
                    group.update(push__moderators=new_user)
                    roles = {"group_id": group.id, "role": user_role}
                    get_user.update(push__roles=roles)
                    return "A new moderator, {} has been added to the group ,{}".format(new_user, group_name)
                elif user_role == 'ADMIN':
                    group.update(push__admins=new_user)
                    roles = {"group_id": group.id, "role": user_role}
                    get_user.update(push__roles=roles)
                    return "A new admin, {} has been added to the group ,{}".format(new_user, group_name)
                else:
                    return "Enter a valid role, choices being ['ADMIN', 'MODERATOR', 'MEMBER']"
            else:
                return "Only admin can add new admins and moderators to the group"
        except (FieldDoesNotExist, ValidationError):
            raise SchemaValidationError
        except Exception:
            raise InternalServerError


class RemoveUsers(Resource):
    @jwt_required()
    def delete(self, group_name):
        try:
            identity = get_jwt_identity()
            user = User.objects.get(id=identity)
            remove_user = request.json.get("remove_user")
            if group_exists(group_name):
                group = Group.objects.get(name=group_name)
                if user_exists_in_group(remove_user, group_name):
                    get_user = User.objects.get(username=remove_user)
                    if remove_user == group.created_by:
                        return "Cannot remove the creator of the group"
                else:
                    return "User doesnot exist in this group"
            else:
                return "Group doesnot exist"
            if user['username'] in group['moderators']:
                for member in range(len(group['members'])):
                    if group['members'][member] == remove_user:
                        del group['members'][member]
                        group.save()
                        for role_index in range(len(get_user['roles'])):
                            if get_user['roles'][role_index]['group_id'] == group.id:
                                del get_user['roles'][role_index]
                                get_user.save()
                                return "Member, {} has been deleted from the group".format(remove_user)
                return "Moderator can only remove members"
            elif user['username'] in group['admins']:
                for role in ['admins', 'moderators', 'members']:
                    for one_user in range(len(group[role])):
                        if group[role][one_user] == remove_user:
                            del group[role][one_user]
                            group.save()
                            for role_index in range(len(get_user['roles'])):
                                if get_user['roles'][role_index]['group_id'] == group.id:
                                    del get_user['roles'][role_index]
                                    get_user.save()
                                    return "User, {} has been deleted from the group".format(remove_user)
            else:
                return "Members cannot delete any user from the group"
        except (FieldDoesNotExist, ValidationError):
            raise SchemaValidationError


class DeleteGroup(Resource):
    @jwt_required()
    def delete(self, group_name):
        try:
            identity = get_jwt_identity()
            user = User.objects.get(id=identity)
            if group_exists(group_name):
                group = Group.objects.get(name=group_name)
                if user_exists_in_group(user.username, group_name):
                    pass
                else:
                    return "User doesnot exist in the group"
            else:
                return "Group doesnot exist"
            if user.username == group.created_by:
                for roles in ['admins', 'moderators', 'members']:
                    for users in group[roles]:
                        get_user = User.objects.get(username=users)
                        for del_role in range(len(get_user['roles'])):
                            if get_user['roles'][del_role]['group_id'] == group.id:
                                del get_user['roles'][del_role]
                                get_user.save()
                            else:
                                continue
                group.delete()
                post = Post.objects.get(group=group.id)
                post.delete()
                return "Group deleted successfully, All posts in the group deleted"
            else:
                "Only creator can delete the group"
        except Exception:
            raise InternalServerError


class ViewGroups(Resource):
    @jwt_required()
    def get(self):
        try:
            identity = get_jwt_identity()
            user = User.objects.get(id=identity)
            if user_exists(user.username):
                group = Group.objects().to_json()
                return Response(group, mimetype="application/json", status=200)
            else:
                return "User doesnot exist"
        except Exception:
            raise InternalServerError
