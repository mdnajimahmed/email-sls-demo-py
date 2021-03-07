import io
import json
import os
import boto3
from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication


def download_from_s3(object_key):
    print(f"downloading {object_key} from S3")
    client = boto3.client('s3')
    bytes_buffer = io.BytesIO()
    client.download_fileobj(Bucket='email-attachment-mediator', Key=object_key, Fileobj=bytes_buffer)
    byte_value = bytes_buffer.getvalue()
    print(f"finished downloading {object_key} from S3")
    return byte_value


def notify_sre_team(email_context, attributes):
    print("notifying sre team, email_context = ", email_context, "attributes", attributes)
    approximate_receive_count = int(attributes['ApproximateReceiveCount'])
    print("approximate_receive_count", approximate_receive_count)
    sns = boto3.client('sns')
    topic_arn = os.getenv("SRE_ALERT_TOPIC_ARN")
    print("topic_arn", topic_arn)

    if approximate_receive_count > 1:
        response = sns.publish(
            TopicArn=topic_arn,
            Message=f"warn - ses doing retry!!! pls check log and investigate further\nhint:{json.dumps(attributes)}"
                    f"details={json.dumps(email_context)}",
        )
        print("sns response", response)
    else:
        response = sns.publish(
            TopicArn=topic_arn,
            Message=f"warn - main email handler failed!!! using sns for fallback! pls take action\nhint:{json.dumps(attributes)}\n"
                    f"details={json.dumps(email_context)}",
        )
        print("sns response", response)


def send_email_with_ses(email_context, attributes):
    print("sending email using ses with email_context = ", email_context, "attributes", attributes)
    notify_sre_team(email_context, attributes)
    sender = "Timelyship SES Team <no-reply@timelyship.com>"
    print("bodyText", email_context["bodyText"])
    recipients = email_context['recipients']
    print("recipients", recipients)
    aws_region = "ap-southeast-1"

    client = boto3.client('ses', region_name=aws_region)

    msg = MIMEMultipart('mixed')
    msg['Subject'] = email_context["subject"]
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)

    msg_body = MIMEMultipart('alternative')

    text_part = MIMEText(email_context['bodyText'].encode("utf-8"), 'plain', "utf-8")
    html_part = MIMEText(download_from_s3(email_context['htmlKey']).decode(), 'html', "utf-8")

    msg_body.attach(text_part)
    msg_body.attach(html_part)
    msg.attach(msg_body)
    if email_context['hasAttachment']:
        object_key = email_context['attachmentKey']
        att = MIMEApplication(download_from_s3(object_key))
        att.add_header('Content-Disposition', 'attachment', filename=email_context['attachmentName'])
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
