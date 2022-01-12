import os
import boto3


def handler(event, context):
	print('event:', event)

    s3 = boto3.client('s3')
    ses = boto3.client('ses')
    ecr = boto3.client('ecr')

    try:
        presigned_urls = get_presigned_urls(
            s3,
            [
                event['model_file_key'],
                event['predictions_file_key'],
                event['validations_file_key'],                
            ],
        )

        body = '''
        Download your files from the presigned URLs below:

        Model: {0}
        Predictions: {1}
        Validations: {2}
        '''.format(presigned_urls[0], presigned_urls[1], presigned_urls[2])

        send_email_response = ses.send_email(
            Source=os.getenv["SOURCE_EMAIL"], # NOTE: this will need to be verified with SES
            Destination=event['email'],
            Message={
                Subject: {
                    Data: 'Your model has been successfully trained!',
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


def get_presigned_urls(s3, keys):
    presigned_urls = []
    try:
        for key in keys:
            presigned_urls.append(get_presigned_url(s3, key))

        return presigned_urls

    except Exception as e:
        return e


def get_presigned_url(s3, key):
    return s3.generate_presigned_url(
        'get_object',
        Params={
            Bucket: os.getenv('DATA_BUCKET_NAME'),
            Key: key,
        },
        ExpiresIn=3600,
    )
