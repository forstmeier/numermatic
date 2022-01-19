import zipfile
import boto3


def handler(event, context):
	print('event:', event)

    uploads_bucket = event['Records'][0]['s3']['bucket']['name']
	key = event['Records'][0]['s3']['object']['key']

	key_split = key.split('/')

	user_id = key_split[0]
	execution_id = key_split[1]

	s3 = boto3.client('s3')

	local_file = '/tmp/model.zip'

	try:
		s3.download_file(
			Bucket=uploads_bucket,
			Key=key,
			Filename=local_file,
		)

		zip_ref = zipfile.ZipFile(local_file)
		zip_ref.extractall(dir_name)
		zip_ref.close()

		models_bucket = os.getenv('MODELS_BUCKET_NAME')

		s3.upload_file(
			Filename='/tmp/model.py',
			Bucket=models_bucket,
			Key='{}/{}/models/model.py'.format(user_id, execution_id),
		)

		s3.upload_file(
			Filename='/tmp/requirements.txt',
			Bucket=models_bucket,
			Key='{}/{}/models/requirements.txt'.format(user_id, execution_id),
		)

	except Exception as e:
		print('exception:', e)

		get_item_response = dynamodb.get_item(
			TableName=os.getenv('USERS_TABLE_NAME'),
			Key={
				'id': {
					'S': event['headers']['numermatic-user-id'],
				},
			},
		)
		print('get_item_response:', get_item_response)

		email = get_item_response['Item']['email']['S']

		ses = boto3.client('ses')

        send_email_response = ses.send_email(
            Source=os.getenv("SOURCE_EMAIL"),
            Destination=email,
            Message={
                Subject: {
                    Data: 'Your model has encountered an error!',
                },
                Body: {
                    Text: {
                        Data: 'Contact the project owner for more information. Execution ID: {}'.format(execution_id),
                    }
                }
            },
        )
		print('send_email_response:', send_email_response)

	return None