from sqs_service import sqs_service

def send_email(email_address, subject, content):
    message = {
        'email_address': email_address,
        'subject': subject,
        'content': content
    }

    message_id = sqs_service.send_message(message)
    print(f"Message sent to SQS, message ID: {message_id}")
