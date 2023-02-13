from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource
from resources.errors import *
from resources.exists import group_exists, user_exists_in_group
import datetime
from mail.mail_daily_feed import send_notification
from database.models import Group, Post, User


class DailyFeed(Resource):
    @jwt_required()
    def post(self, group_name):
        try:
            identity = get_jwt_identity()
            user = User.objects.get(id=identity)
            if group_exists(group_name):
                group = Group.objects.get(name=group_name)
                if user_exists_in_group(user.username, group_name):
                    if user.username in group.admins or group.moderators:
                        feed(group_name)
                    else:
                        return "Only admin or moderator can send daily feed"
                else:
                    return "User doesnot exist in the group"
            else:
                return "Group doesnot exist"
            return "Email sent successfully to admins and moderators", 200
        except Exception:
            raise InternalServerError


def feed(group_name):
    yesterday = datetime.datetime.utcnow() - datetime.timedelta(days=1)
    new_posts = Post.objects(time__gt=yesterday)
    content = list()
    data = dict()
    get_group = Group.objects.get(name=group_name)
    for post in new_posts:
        if post.group.id == get_group.id:
            data["author"] = post.author
            data["content"] = post.content
            content.append(data)
    print(content)
    send_notification(content, group_name)
