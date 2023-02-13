from resources.auth import SignupApi, LoginApi
from comment.comment import AddComment, DeleteComment, ViewComments
from group.group import GroupApi, AddUsers, RemoveUsers, DeleteGroup, ViewGroups
from post.post import AddPost, UpdatePost, DeletePost, ApprovePost, ViewPost, ViewUserRoles
from inactive.inactive_members import InactiveMembers
from daily_feed.daily_feed import DailyFeed
from group.edit_roles import EditRoles


def initialize_routes(api):
    api.add_resource(GroupApi, '/group')
    api.add_resource(AddPost, '/addPost/<group_name>')
    api.add_resource(UpdatePost, '/updatePost/<group_name>/<post_id>')
    api.add_resource(DeletePost, '/deletePost/<group_name>/<post_id>')
    api.add_resource(SignupApi, '/signup')
    api.add_resource(LoginApi, '/login')
    api.add_resource(ApprovePost, '/approve_post/<group_name>/<post_id>/<approved>')
    api.add_resource(AddComment, '/group/<group_name>/<post_id>/comment')
    api.add_resource(AddUsers, '/add/<group_name>')
    api.add_resource(RemoveUsers, '/remove/<group_name>')
    api.add_resource(EditRoles, '/edit_role/<group_name>')
    api.add_resource(DeleteGroup, '/delete_group/<group_name>')
    api.add_resource(ViewPost, '/viewPost/<group_name>/<user_name>')
    api.add_resource(DailyFeed, '/feed/<group_name>')
    api.add_resource(InactiveMembers, '/inactive/<group_name>')
    api.add_resource(DeleteComment, '/<group_name>/<post_id>/<comment_id>')
    api.add_resource(ViewComments, '/<group_name>/<post_id>')
    api.add_resource(ViewUserRoles, '/roles')
    api.add_resource(ViewGroups, '/groups')
