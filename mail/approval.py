import smtplib
import ssl
from email.message import EmailMessage
from database.models import Group, User


def send_mail(group_name, post_passed):
    email_id = 'sendmails1006@gmail.com'
    password = 'lcvroedsdgbxbeju'
    recipient_list = list()
    group = Group.objects.get(name=group_name)
    for role in ['admins', 'moderators']:
        for user in group[role]:
            print(user)
            get_admin = User.objects.get(username=user)
            recipient_list.append(get_admin['email'])
    message = EmailMessage()
    message['Subject'] = 'Post approval'
    message['From'] = email_id
    message['To'] = recipient_list
    _id = post_passed.id
    author = post_passed['author']
    content = post_passed['content']
    body = " Approve the post for details:\n post id : {}\n author: {}\n content:{}\n ".format(_id, author, content)
    message.set_content(body)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_id, password)
        print(f"Sending email to - {recipient_list}")
        smtp.send_message(message)
        print(f"Email successfully sent to - {recipient_list}")
