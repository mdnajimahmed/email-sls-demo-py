import json

from src.email.m65_sender import send_email_with_m65
from src.email.ses_sender import send_email_with_ses


def extract_message(event):
    print("event", event)
    records = event["Records"]
    if records is None or len(records) != 1:
        raise Exception(f"Expected exactly one record,found {len(records)}")
    email_context = json.loads(records[0]['body'])
    attributes = records[0]['attributes']
    attributes['messageId'] = records[0]['messageId']
    print("email_context === ", email_context, "attributes", attributes)
    return email_context, attributes


def email_handler(event, context):
    email_context, attributes = extract_message(event)
    send_email_with_m65(email_context, attributes)
    return


def email_handler_fallback(event, context):
    email_context, attributes = extract_message(event)
    send_email_with_ses(email_context, attributes)
    return


if __name__ == '__main__':
    email_handler(None)
