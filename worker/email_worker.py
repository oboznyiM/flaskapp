from sqs_service import sqs_service
import time
import threading

def process_message(message):
    print(f"Processing message: {message}")
    print(f"Preparing to send email to {message['email_address']}...")
    time.sleep(2)
    print(f"Subject: {message['subject']}")
    print(f"Content: {message['content']}")
    print("Sending email...")
    time.sleep(3)
    print("Email sent!")

def poll_sqs():
    while True:
        message, receipt_handle = sqs_service.receive_message()

        if message is not None:
            process_message(message)
            sqs_service.delete_message(receipt_handle)
        else:
            print("No messages to process. Sleeping...")
            time.sleep(10)

if __name__ == "__main__":
    print("Started email worker")
    poll_sqs()
    #threading.Thread(target=poll_sqs).start()
