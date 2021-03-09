import json
import os
from datetime import datetime

from src.email.m65_sender import send_email_with_m65
from src.email.ses_sender import send_email_with_ses
from dateutil import parser, tz

from src.email.sns_helper import send_sns_message


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


def pass_expiration_check(email_context, attributes):
    try:
        exp_at_utc_str = email_context['expAtUtc']
        parsing_format = "%Y-%m-%dT%H:%M:%S.%fZ"
        exp_at_utc = parser.isoparse(exp_at_utc_str)
        now = datetime.now(tz.UTC)
        exp_log = f"{parsing_format}, {exp_at_utc}, {now}, {exp_at_utc},exp_at_utc < now = {exp_at_utc < now}"
        print("expiration log", exp_log)

        if exp_at_utc < now:  # Expiration check failed, message expired , no need to try with ses, silently discard leaving a msg in sns and return false
            topic_arn = os.getenv("SRE_ALERT_TOPIC_ARN")
            message = f"warn - silently discarding message because of expiration!!!" \
                      f"expiration log = ${exp_log}" \
                      f"attributes:{json.dumps(attributes)}\n" \
                      f"email_context={json.dumps(email_context)}"
            send_sns_message(topic_arn, message)
            return False
    except Exception as e:
        print("Error parsing dates", e)
    return True


def email_handler_fallback(event, context):
    email_context, attributes = extract_message(event)
    if pass_expiration_check(email_context, attributes):
        send_email_with_ses(email_context, attributes)
    return


if __name__ == '__main__':
    email_handler(None)
