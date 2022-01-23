import json
import os
import time
import uuid
import boto3
import stripe


def handler(event, context):
    print('event:', event)

    user_id = str(uuid.uuid4())

    stripe.api_key = os.getenv('STRIPE_API_KEY')

    body = event['body']

    dynamodb = boto3.client('dynamodb')

    try:
        create_payment_method_response = stripe.PaymentMethod.create(
            type="card",
            card={
                "number": body['number'],
                "exp_month": body['exp_month'],
                "exp_year": body['exp_year'],
                "cvc": body['cvc'],
            },
        )

        create_customer_response = stripe.Customer.create(
            email=body['email'],
        )

        attach_method_response = stripe.PaymentMethod.attach(
            create_payment_method_response['id'],
            customer=create_customer_response['id'],
        )

        put_item_response = dynamodb.put_item(
            TableName=os.getenv('USERS_TABLE_NAME'),
            Item={
                'id': {
                    'S': user_id,
                },
                'email': {
                    'S': body['email'],
                },
                'stripe_customer_id': {
                    'S': create_customer_response['id'],
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
