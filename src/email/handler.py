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
    # str_value = byte_value.decode()  # python3, default decoding is utf-8
    return byte_value


def email_handler(event, context):
    # Replace sender@example.com with your "From" address.
    # This address must be verified with Amazon SES.
    SENDER = "Sender Name <no-reply@timelyship.com>"

    # Replace recipients@example.com with a "To" address. If your account
    # is still in the sandbox, this address must be verified.
    recipients = ['najim.ju@gmail.com', 'ahmedmdnajim@gmail.com']

    # If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
    AWS_REGION = "ap-southeast-1"

    # The subject line for the email.
    SUBJECT = "Customer service contact info"

    # The full path to the file that will be attached to the email.
    # ATTACHMENT = "C:\\personal\\email-sls-demo-py-v2\\resources\\Sample-Spreadsheet-10000-rows.xls"

    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = "Hello,\r\nPlease see the attached file for a list of customers to contact."

    # The HTML body of the email.
    BODY_HTML = """\
    <html>
    <head></head>
    <body>
    <h1>Hello!</h1>
    <p>Please see the attached file for a list of customers to contact.</p>
    </body>
    </html>
    """

    # The character encoding for the email.
    CHARSET = "utf-8"

    # Create a new SES resource and specify a region.
    client = boto3.client('ses', region_name=AWS_REGION)

    # Create a multipart/mixed parent container.
    msg = MIMEMultipart('mixed')
    # Add subject, from and to lines.
    msg['Subject'] = SUBJECT
    msg['From'] = SENDER
    msg['To'] = ', '.join(recipients)

    # Create a multipart/alternative child container.
    msg_body = MIMEMultipart('alternative')

    # Encode the text and HTML content and set the character encoding. This step is
    # necessary if you're sending a message with characters outside the ASCII range.
    textpart = MIMEText(BODY_TEXT.encode(CHARSET), 'plain', CHARSET)
    htmlpart = MIMEText(BODY_HTML.encode(CHARSET), 'html', CHARSET)

    # Add the text and HTML parts to the child container.
    msg_body.attach(textpart)
    msg_body.attach(htmlpart)

    # Define the attachment part and encode it using MIMEApplication.
    # att = MIMEApplication(open(ATTACHMENT, 'rb').read())
    objectKey = "Sample-Spreadsheet-10000-rows.xls"
    att = MIMEApplication(downloadFromS3(objectKey))

    # Add a header to tell the email client to treat this part as an attachment,
    # and to give the attachment a name.
    att.add_header('Content-Disposition', 'attachment', filename=objectKey)

    # Attach the multipart/alternative child container to the multipart/mixed
    # parent container.
    msg.attach(msg_body)

    # Add the attachment to the parent container.
    msg.attach(att)
    # print(msg)
    try:
        # Provide the contents of the email.
        response = client.send_raw_email(
            Source=SENDER,
            Destinations=recipients,
            RawMessage={
                'Data': msg.as_string(),
            },
        )
    # Display an error if something goes wrong.
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])


if __name__ == '__main__':
    email_handler(None)
