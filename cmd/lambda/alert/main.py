import os
import boto3


def handler(event, context):
	print('event:', event)

    ses = boto3.client('ses')
    ecr = boto3.client('ecr')

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
		print('send_email_response:', send_email_response)

        delete_repository_response = ecr.delete_repository(
            repositoryName=event['repository_name'],
        )
		print('delete_repository_response:', delete_repository_response)

		return {
			'status': 'success',
		}

    except Exception as e:
		print('exception:', e)
        return {
            'error': str(e),
            'status': 'error',
        }
