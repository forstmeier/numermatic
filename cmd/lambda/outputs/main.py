import json
import boto3


def handler(event, context):
	print('event:', event)

	user_id = event['headers']['numermatic-user-id']

	dynamodb = boto3.client('dynamodb')

	try:
		# NOTE: pagination can be added in later if needed
		scan_response = dynamodb.scan(
			TableName=os.getenv('OUTPUTS_TABLE_NAME'),
			FilterExpression=Attr('user_id').eq(user_id),
		)

		data = []
		for item in scan_response['Items']:
			data.append({
				'execution_id': item['execution_id']['S'],
				'message': item['message']['S'],
				'presigned_url': item['presigned_url']['S'],
				'timestamp': item['timestamp']['S'],
			})

		return {
			'body': json.dumps({
				'message': 'success',
				'data': data,
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