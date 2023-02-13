from database.models import Group, User, Post
from bson import ObjectId


def group_exists(group_name):
    group_list = list()
    for group in Group.objects():
        group_list.append(group.name)
    if group_name in group_list:
        return True
    else:
        return False


def user_exists(user_name):
    user_list = list()
    all_users = User.objects()
    for user in all_users:
        user_list.append(user.username)
    if user_name in user_list:
        return True
    else:
        return False


def user_exists_in_group(user_name, group_name):
    user_list = list()
    all_users = User.objects()
    for user in all_users:
        user_list.append(user.username)
    for roles in ['admins', 'moderators', 'members']:
        if user_name in user_list:
            if group_exists(group_name):
                get_group = Group.objects.get(name=group_name)
                print(len(get_group[roles]))
                for index in range(len(get_group[roles])):
                    if user_name in get_group[roles][index]:
                        return True
            else:
                return False
        else:
            return False


def post_exists(post_id, group_name):
    post_list = list()
    object_id = ObjectId(post_id)
    for post in Post.objects:
        post_list.append(post.id)
    if group_exists(group_name):
        group_by_name = Group.objects.get(name=group_name)
        if object_id in post_list:
            get_post = Post.objects.get(id=post_id)
            group_by_id = get_post.group.id
            if group_by_id == group_by_name.id:
                return True
            else:
                return False
        else:
            return False
    else:
        return False
