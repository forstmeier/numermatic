import datetime
import time
import boto3


def handler(event, context):
	print('event:', event)

	user_id = event['user_id']
	execution_id = event['execution_id']

	presigned_url = ''

	expiration = datetime.datetime.now() + datetime.timedelta(hours=24)
	expiration = int(expiration.timestamp())

	subject = ''
	body = ''

	if event['status'] == 'success':

		# outline:
		# [ ] create presigned url
		# [ ] set message

	else if event['status'] == 'failure':

		# outline:
		# [ ] set message

	dynamodb = boto3.client('dynamodb')

	put_item_response = dynamodb.put_item(
		TableName=os.getenv('OUTPUTS_TABLE_NAME'),
		Item={
			'user_id': {
				'S': user_id,
			},
			'execution_id': {
				'S': execution_id,
			},
			'message': {
				'S': message,
			}
			'presigned_url': {
				'S': presigned_url,
			},
			'timestamp': {
				'N': str(time.time()),
			}
			'expiration': {
				'N': str(expiration),
			}
		}
	)


def get_presigned_url(s3, key):
	return s3.generate_presigned_url(
		'get_object',
		Params={
			Bucket: os.getenv('DATA_BUCKET_NAME'),
			Key: key,
		},
		ExpiresIn=3600,
	)
