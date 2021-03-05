import json

from src.email.sesSender import send_email_with_ses




def email_handler(event, context):
    print("event",event)
    records = event["Records"]

    if records is None or len(records) != 1:
        raise Exception(f"Expected exactly one record,found {len(records)}")
    body = json.loads(records[0]['body'])
    print("body === ", body)
    send_email_with_ses(body)
    return

if __name__ == '__main__':
    email_handler(None)
