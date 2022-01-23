import json
import os
import uuid
import boto3


def handler(event, context):
	print('event:', event)

	dynamodb = boto3.client('dynamodb')
	s3 = boto3.client('s3')

	try:
		get_item_response = dynamodb.get_item(
			TableName=os.getenv('USERS_TABLE_NAME'),
			Key={
				'id': {
					'S': event['headers']['numermatic-user-id'],
				},
			},
		)
		print('get_item_response:', get_item_response)

		user_id = get_item_response['Item']['id']['S']
		execution_id = str(uuid.uuid4())

		generate_presigned_url_response = s3.generate_presigned_url(
			ClientMethod='put_object',
			Params={
				'Bucket':os.getenv('UPLOADS_BUCKET_NAME'),
				'Key': user_id+'/'+execution_id+'/models/model.zip',
			},
			ExpiresIn=900,
		)
		print('generate_presigned_url_response:', generate_presigned_url_response)

		return {
			'body': json.dumps({
				'message': 'success',
				'url': generate_presigned_url_response,
				'execution_id': execution_id,
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
