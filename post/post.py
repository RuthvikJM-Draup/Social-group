from flask import Response, request
from database.models import Group, User, Post
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource
from mail.notifications import send_info
from mail.approval import send_mail
from resources.exists import group_exists, user_exists_in_group, post_exists, user_exists
from mongoengine.errors import FieldDoesNotExist, ValidationError, InvalidQueryError
from resources.errors import *


class AddPost(Resource):
    @jwt_required()
    def post(self, group_name):
        try:
            identity = get_jwt_identity()
            user = User.objects.get(id=identity)
            author = request.json.get("author")
            content = request.json.get("content")
            if group_exists(group_name):
                if user_exists_in_group(author, group_name):
                    group = Group.objects.get(name=group_name)
                    if author == user['username']:
                        if user['username'] in group['members']:
                            post = Post(group=group, group_name=group_name, author=author, content=content)
                            post.save()
                            group_name_pass = group['name']
                            send_mail(group_name_pass, post)
                            return {"Post created successfully, post id": str(post.id)}
                        elif user['username'] in group['admins'] or group['moderators']:
                            post = Post(group=group, group_name=group_name, author=author, content=content,
                                        approved=True)
                            post.save()
                            send_info('postApproved', group_name, post.id)
                            return {"Post created successfully and approved, post id": str(post.id)}
                    else:
                        return {"Author name not matching username": str(user.username)}
                else:
                    return "User does not exists in the group"
            else:
                return "Group does not exists, Enter correct group name"
        except (FieldDoesNotExist, ValidationError):
            raise SchemaValidationError
        except Exception:
            raise InternalServerError


class ApprovePost(Resource):
    @jwt_required()
    def put(self, group_name, post_id, approved):
        try:
            identity = get_jwt_identity()
            user = User.objects.get(id=identity)
            if not post_exists(post_id, group_name):
                return "Post ID is invalid or post doesnot exist in this group"
            post = Post.objects.get(id=post_id)
            group_id = post.group.id
            get_group = Group.objects.get(id=group_id)
            for role in ['admins', 'moderators']:
                if user['username'] in get_group[role]:
                    if approved == "True":
                        approve_value = True
                        Post.objects.get(id=post_id).update(approved=approve_value)
                        send_info('postApproved', group_name, post_id)
                        return {"Post approved successfully, post id": post_id}, 200
                    elif approved == "False":
                        post.delete()
                        return "Disapproved the post and deleted the post", 200
                    else:
                        return "Enter the correct approval value, choices: [True, False]"
            return "Authenticated user is not an admin or moderator in the group, approving post forbidden", 403
        except InvalidQueryError:
            raise SchemaValidationError


class UpdatePost(Resource):
    @jwt_required()
    def put(self, group_name, post_id):
        try:
            identity = get_jwt_identity()
            user = User.objects.get(id=identity)
            if post_exists(post_id, group_name):
                post = Post.objects.get(id=post_id)
                group = Group.objects.get(name=group_name)
                if group_exists(group_name):
                    if post.approved:
                        pass
                    else:
                        return "Unapproved post cannot be updated"
                else:
                    return "Group doesnot exist"
                if user_exists_in_group(user.username, group.name):
                    author = request.json.get("author")
                    content = request.json.get("content")
                    user_name = user.username
                    if post.author == user_name or (user_name in group['admins'] or group['moderators']):
                        print(author)
                        print(post.author)
                        if author == user.username:
                            post.content = content
                            post.save()
                            send_info('postUpdated', group_name, post_id)
                            return {"Post updated successfully, post id ": post_id}
                        else:
                            return {"Author name not matching username": str(user_name)}
                    else:
                        return "Only admin, moderator or the member who has posted can update the post"
                else:
                    return "User does not exists in the group"
            else:
                return "Post ID is invalid or post doesnot exists in this group"
        except InvalidQueryError:
            raise SchemaValidationError


class DeletePost(Resource):
    @jwt_required()
    def delete(self, group_name, post_id):
        try:
            identity = get_jwt_identity()
            user = User.objects.get(id=identity)
            if group_exists(group_name):
                group = Group.objects.get(name=group_name)
                if post_exists(post_id, group_name):
                    post = Post.objects.get(id=post_id)
                    user_name = user.username
                    if user_exists_in_group(user_name, group_name):
                        if post.author == user_name or (user_name in group['admins'] or group['moderators']):
                            post.delete()
                            send_info('postDeleted', group_name, post_id)
                            return "Post deleted successfully"
                        else:
                            return "Only admin, moderator or the member who has posted can delete the post"
                    else:
                        return "User doesnot exist in the group"
                else:
                    return "Post ID not valid or post doesnot exist in this group"
            else:
                return "Group doesnot exist"
        except Exception:
            raise InternalServerError


class ViewPost(Resource):
    @jwt_required()
    def get(self, group_name, user_name):
        identity = get_jwt_identity()
        get_user = User.objects.get(id=identity)
        if group_exists(group_name) and user_exists_in_group(user_name, group_name):
            group = Group.objects.get(name=group_name)
            if group['type'] == 'PRIVATE':
                for roles in ['admins', 'moderators', 'members']:
                    for users in group[roles]:
                        if user_name == users:
                            if get_user['username'] == users:
                                post = Post.objects(group=group.id, approved=True).only("author", "content",
                                                                                        "comments").to_json()
                                return Response(post, mimetype="application/json", status=200)
                            else:
                                return "Authentication not successful as user is invalid"
                        else:
                            continue
            elif group['type'] == 'PUBLIC':
                post = Post.objects(group=group.id, approved=True).only("author", "content", "comments").to_json()
                return Response(post, mimetype="application/json", status=200)
            else:
                return "Invalid group type"
        return "Group name or user is invalid, enter the correct group name and valid user name"


class ViewUserRoles(Resource):
    @jwt_required()
    def get(self):
        identity = get_jwt_identity()
        user = User.objects.get(id=identity)
        if user_exists(user.username):
            roles = user['roles']
            return "{}".format(roles)
        else:
            return "User doesnot exist"
