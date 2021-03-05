import io
import os
import boto3
from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication


def downloadFromS3(objectKey):
    # s3 = boto3.resource('s3')
    # obj = s3.Object('email-attachment-mediator', objectKey)
    # return obj.get()['Body'].read()

    client = boto3.client('s3')
    bytes_buffer = io.BytesIO()
    client.download_fileobj(Bucket='email-attachment-mediator', Key=objectKey, Fileobj=bytes_buffer)
    byte_value = bytes_buffer.getvalue()
    return byte_value


def send_email_with_ses(data):
    print("sending email using ses with data = ", data)
    sender = "Timelyship Team <no-reply@timelyship.com>"
    print("bodyText",data["bodyText"])
    recipients = data['recipients']
    print("recipients",recipients)
    aws_region = "ap-southeast-1"

    client = boto3.client('ses', region_name=aws_region)

    msg = MIMEMultipart('mixed')
    msg['Subject'] = data["subject"]
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)

    msg_body = MIMEMultipart('alternative')

    text_part = MIMEText(data['bodyText'].encode("utf-8"), 'plain', "utf-8")
    html_part = MIMEText(downloadFromS3(data['bodyHtml']).decode(), 'html', "utf-8")

    msg_body.attach(text_part)
    msg_body.attach(html_part)

    object_key = data['attachment']
    att = MIMEApplication(downloadFromS3(object_key))

    att.add_header('Content-Disposition', 'attachment', filename=object_key)
    msg.attach(msg_body)
    msg.attach(att)
    try:
        response = client.send_raw_email(
            Source=sender,
            Destinations=recipients,
            RawMessage={
                'Data': msg.as_string(),
            },
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
