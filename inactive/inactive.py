import datetime
from database.models import Group, Post, User


def inactive_members(group_name):
    inactive = datetime.datetime.utcnow() - datetime.timedelta(days=2)
    get_group = Group.objects.get(name=group_name)
    posts = Post.objects(time__gt=inactive)
    members_posted = list()
    members_list = list()
    for post in posts:
        if post.group.id == get_group.id:
            members_posted.append(post.author)
    for member in get_group['members']:
        members_list.append(member)
    members_inactive = list(set(members_list) - set(members_posted))
    for one_member in members_inactive:
        for index in range(len(get_group.members)):
            if get_group['members'][index] == one_member:
                del get_group['members'][index]
                get_group.save()
                user = User.objects.get(username=one_member)
                for role in range(len(user['roles'])):
                    if user['roles'][role]['group_id'] == get_group.id:
                        del user['roles'][role]
                        user.save()
                        print("Deleted inactive members")
