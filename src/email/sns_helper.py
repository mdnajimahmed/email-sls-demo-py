import boto3


def send_sns_message(topic_arn, message):
    try:
        print("send_sns_message::sending message to topic", topic_arn, message)
        sns = boto3.client('sns')
        print("topic_arn", topic_arn)
        response = sns.publish(
            TopicArn=topic_arn,
            Message=message,
        )
        print("sns response", response)
        return response
    except Exception as e:
        print("Error while sending sre notification to sns", e)
