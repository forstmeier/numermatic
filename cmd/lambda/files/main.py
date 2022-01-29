import os
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
		zip_ref.extractall('/tmp/')
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

		return True

	except Exception as e:
		print('exception:', e)
