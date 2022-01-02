import json
import os
import boto3
import stripe
import uuid


def handler(event, context):
    print('event:', event)

    api_key = uuid.uuid4()
    user_id = uuid.uuid4()

    stripe.api_key = os.getenv('STRIPE_API_KEY')

    body = event['Body']

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
    except Exception as e:
        return {
            Body: str(e),
            StatusCode: 500,
            IsBase64Encoded: False,
        }

    try:
        create_customer_response = stripe.Customer.create(
            email=body['email'],
        )
    except Exception as e:
        return {
            Body: str(e),
            StatusCode: 500,
            IsBase64Encoded: False,
        }

    try:
        attach_method_response = stripe.PaymentMethod.attach(
            create_payment_method_response['id'],
            customer=create_customer_response['id'],
        )
    except Exception as e:
        return {
            Body: str(e),
            StatusCode: 500,
            IsBase64Encoded: False,
        }

    dynamodb = boto3.client('dynamodb')
    try:
        put_item_response = dynamodb.put_item(
            TableName=os.getenv('USERS_TABLE_NAME'),
            Item={
                'api_key': {
                    'S': api_key,
                },
                'email': {
                    'S': body['email'],
                },
                'user_id': {
                    'S': user_id,
                },
                'stripe_customer_id': {
                    'S': create_customer_response['id'],
                },
            }
        )
    except Exception as e:
        return {
            Body: str(e),
            StatusCode: 500,
            IsBase64Encoded: False,
        }

    return {
        Body: json.dumps({
            message: 'successfully created user',
            api_key: api_key,
        }),
        StatusCode: 200,
        IsBase64Encoded: False,
    }
