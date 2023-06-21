from sqs_service import sqs_service

def send_email(username, coffee):
    message = {
        'email_address': f"{username}@gmail.com",
        'subject': "Favourite cofee change",
        'content': f"You favourite coffees have been successfully changed to {coffee}"
    }

    message_id = sqs_service.send_message(message)
    print(f"Message sent to SQS, message ID: {message_id}")
