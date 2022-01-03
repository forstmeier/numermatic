import boto3


def handler(event, context):
    ses = boto3.client('ses')
    try:
        body = '''
        Error: {0}
        '''.format(event['error'])

        send_email_response = ses.send_email(
            Source=os.getenv["SOURCE_EMAIL"], # NOTE: this will need to be verified with SES
            Destination=event['email'],
            Message={
                Subject: {
                    Data: 'Your model encountered an error!',
                },
                Body: {
                    Text: {
                        Data: body,
                    }
                }
            },
        )

        return {
            status: 'error',
        }

    except Exception as e:
        return {
            error: str(e),
            status: 'error',
        }
