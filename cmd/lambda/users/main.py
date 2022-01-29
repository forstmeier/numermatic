import json
import os
import time
import uuid
import boto3


def handler(event, context):
	print('event:', event)

	user_id = str(uuid.uuid4().hex)

	body = event['body']

	dynamodb = boto3.client('dynamodb')

	try:
		put_item_response = dynamodb.put_item(
			TableName=os.getenv('USERS_TABLE_NAME'),
			Item={
				'id': {
					'S': user_id,
				},
				'email': {
					'S': body['email'],
				},
				'timestamp': {
					'S': time.time(),
				}
			}
		)

		return {
			'body': json.dumps({
				message: 'successfully created user',
				user_id: user_id,
			}),
			'statusCode': 200,
			'isBase64Encoded': False,
		}

	except Exception as e:
		print('exception:', e)
		return {
			'body': str(e),
			'statusCode': 500,
			'isBase64Encoded': False,
		}
