import boto3


def handler(event, context):
	print('event:', event)

	dynamodb = boto3.client('dynamodb')
	s3 = boto3.client('s3')

	try:
		query_response = dynamodb.query(
			TableName=os.getenv('USERS_TABLE_NAME'),
			KeyConditionExpression='api_key = :api_key',
			ExpressionAttributeValues={
				':api_key': {
					'S': event['body']['api_key'],
				},
			},
		)
		print('query_response:', query_response)

		user_id = query_response['Items'][0]['id']['S']

		generate_presigned_post_response = s3.generate_presigned_post(
			Bucket=os.getenv('MODELS_BUCKET_NAME'),
			Key=user_id+'/models/model.zip',
			Expiration=900,
		)
		print('generate_presigned_post_response:', generate_presigned_post_response)

	except Exception as e:
		return {
			Body: str(e),
			StatusCode: 500,
			IsBase64Encoded: False,
		}

	return {
		Body: json.dump({
			'message': 'success',
			'url': generate_presigned_post_response['url'],
		})
		StatusCode: 500,
		IsBase64Encoded: False,
	}