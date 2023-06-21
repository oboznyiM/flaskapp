import boto3
import json
import os

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class SQSService(metaclass=Singleton):

    def __init__(self, queue_url):
        if hasattr(self, '_initialized'):
            raise Exception("You can't create more than one instance of SQSService.")
        self.sqs = boto3.client(
            'sqs'
        )
        self.queue_url = queue_url
        self._initialized = True

    def send_message(self, message):
        response = self.sqs.send_message(
            QueueUrl=self.queue_url,
            MessageBody=json.dumps(message)
        )
        return response['MessageId']

    def receive_message(self):
        response = self.sqs.receive_message(
            QueueUrl=self.queue_url,
            AttributeNames=['All'],
            MaxNumberOfMessages=1,
            MessageAttributeNames=['All'],
            WaitTimeSeconds=10
        )

        if 'Messages' in response:
            message = json.loads(response['Messages'][0]['Body'])
            receipt_handle = response['Messages'][0]['ReceiptHandle']
            return message, receipt_handle

        return None, None

    def delete_message(self, receipt_handle):
        self.sqs.delete_message(
            QueueUrl=self.queue_url,
            ReceiptHandle=receipt_handle
        )

SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL")
sqs_service = SQSService(SQS_QUEUE_URL)
