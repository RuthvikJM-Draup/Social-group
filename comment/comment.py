from flask import Response, request
from database.models import Group, User, Post, Comment
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource
from resources.exists import group_exists, user_exists_in_group, post_exists
import json
from mongoengine.errors import FieldDoesNotExist, ValidationError
from resources.errors import *
from mail.notifications import send_info


class AddComment(Resource):
    @jwt_required()
    def post(self, group_name, post_id):
        try:
            identity = get_jwt_identity()
            user = User.objects.get(id=identity)
            if group_exists(group_name):
                group = Group.objects.get(name=group_name)
                if user_exists_in_group(user.username, group_name):
                    if post_exists(post_id, group_name):
                        body = request.get_json()
                        comment = Comment(**body, author=user.username)
                        comment.save()
                        post = Post.objects.get(id=post_id, group=group.id)
                        post.update(push__comments=comment)
                        post.save()
                        send_info('comment', group_name, post_id)
                        return {"Comment added": str(comment.id)}
                    else:
                        return "Post doesnot exist in the group"
                else:
                    return "User doesnot exist in the group"
            else:
                return "Group doesnot exist"
        except (FieldDoesNotExist, ValidationError):
            raise SchemaValidationError
        except Exception:
            raise InternalServerError


class DeleteComment(Resource):
    @jwt_required()
    def delete(self, group_name, post_id, comment_id):
        try:
            identity = get_jwt_identity()
            user = User.objects.get(id=identity)
            if group_exists(group_name):
                if user_exists_in_group(user.username, group_name):
                    if post_exists(post_id, group_name):
                        post = Post.objects.get(id=post_id)
                        comment = Comment.objects.get(id=comment_id)
                        comment.delete()
                        for index in range(len(post.comments)):
                            if post['comments'][index].id == comment_id:
                                del post['comments'][index]
                                post.save()
                                send_info('deleteComment', group_name, post_id)
                        return "Comment deleted successfully"
                    else:
                        return "Post doesnot exist in the group"
                else:
                    return "User doesnot exist in the group"
            else:
                return "Group doesnot exist"
        except Exception:
            raise InternalServerError


class ViewComments(Resource):
    @jwt_required()
    def get(self, group_name, post_id):
        identity = get_jwt_identity()
        user = User.objects.get(id=identity)
        if group_exists(group_name):
            group = Group.objects.get(name=group_name)
            if post_exists(post_id, group_name):
                posts = Post.objects(id=post_id).only('comments').to_json()
                list1 = json.loads(posts)
                list2 = list()
                post = Post.objects.get(id=post_id)
                for index in range(len(post.comments)):
                    list2.append(list1[0]['comments'][index]['$oid'])
                comment = Comment.objects(id__in=list2).to_json()
                if group.type == 'PRIVATE':
                    if user_exists_in_group(user.username, group_name):
                        return Response(comment, mimetype="application/json", status=200)
                    else:
                        return "User doesnot exist in the group"
                elif group.type == 'PUBLIC':
                    return Response(comment, mimetype="application/json", status=200)
                else:
                    return "Invalid group type"
            else:
                return "Post doesnot exist"
        else:
            return "Group doesnot exist"
