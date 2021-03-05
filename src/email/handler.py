import json

from src.email.sesSender import send_email_with_ses


def extract_email_context(event):
    print("event", event)
    records = event["Records"]
    if records is None or len(records) != 1:
        raise Exception(f"Expected exactly one record,found {len(records)}")
    email_context = json.loads(records[0]['body'])
    print("email_context === ", email_context)
    return email_context


def email_handler(event, context):
    send_email_with_ses(extract_email_context(event))
    return


def email_handler_fallback(event, context):
    send_email_with_ses(extract_email_context(event))
    return


if __name__ == '__main__':
    email_handler(None)
