import smtplib
import ssl
from email.message import EmailMessage
from database.models import Group, User


def send_info(choice, group_name, post_id):
    email_id = 'sendmails1006@gmail.com'
    password = 'lcvroedsdgbxbeju'
    recipient_list = list()
    group = Group.objects.get(name=group_name)
    for role in ['admins', 'moderators']:
        for user in group[role]:
            get_admin = User.objects.get(username=user)
            recipient_list.append(get_admin['email'])
    message = EmailMessage()
    if choice == 'postApproved':
        message['Subject'] = 'Post approved:True'
        body = "Post has been approved for post : {}".format(post_id)
    elif choice == 'postDeleted':
        message['Subject'] = 'Post deleted'
        body = "Post deleted : {}".format(post_id)
    elif choice == 'postUpdated':
        message['Subject'] = 'Post updated'
        body = "Post has been updated for : {}".format(post_id)
    elif choice == 'comment':
        message['Subject'] = 'Comment added'
        body = "A comment has been added to post : {}".format(post_id)
    elif choice == 'deleteComment':
        message['Subject'] = 'Comment deleted'
        body = "A comment has been deleted from post : {}".format(post_id)
    else:
        return "Invalid choice"
    message['From'] = email_id
    message['To'] = recipient_list
    message.set_content(body)
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_id, password)
        print(f"Sending email to - {recipient_list}")
        smtp.send_message(message)
        print(f"Email successfully sent to - {recipient_list}")
