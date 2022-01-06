import email.parser
import os
import time
import boto3
import docker
from step_function import get_definition


docker_file_content = '''
ARG REGION=us-east-1

FROM 683313688378.dkr.ecr.us-east-1.amazonaws.com/sagemaker-scikit-learn:0.23-1-cpu-py3

ENV PATH="/opt/ml/code:${PATH}"

COPY /requirements.txt /opt/ml/code
COPY /model.py /opt/ml/code

RUN pip install -r /opt/ml/code/requirements.txt /opt/ml/code/model.py

ENV SAGEMAKER_PROGRAM model.py
'''


def handler(event, context):
	print('event:', event)

    body = email.parser.BytesParser().parsebytes(event['Body'])

    for part in body.get_payload():
        part_key = part.get_param('name', header='content-disposition')
        if part_key == 'api_key':
            api_key = part.get_payload(decode=True)
        elif part_key == 'model_file':
            model_file_content = part.get_payload(decode=True)
        elif part_key == 'requirements_file':
            requirements_file_content = part.get_payload(decode=True)

    dynamodb = boto3.client('dynamodb')
    get_item_response = dynamodb.get_item(
        TableName=os.getenv('USERS_TABLE_NAME'),
        Key={
            'api_key': {
                'S': api_key
            }
        }
    )

    email = get_item_response['Item']['email']['S']
    user_id = get_item_response['Item']['user_id']['S']
    stripe_customer_id = get_item_response['Item']['stripe_customer_id']['S']

    model_file = open('model.py', 'a')
    model_file.write(model_file_content.decode('utf-8'))
    model_file.close()

    requirements_file = open('requirements.txt', 'a')
    requirements_file.write(requirements_file_content.decode('utf-8'))
    requirements_file.close()

    docker_file = open('Dockerfile', 'w')
    docker_file.write(docker_file_content)
    docker_file.close()

    image_name = '{0}-{1}'.format(user_id, str(time.time()))

    image = docker.build(
        path='.',
        dockerfile='Dockerfile',
        tag=image_name+':latest',
        buildargs={
            'REGION': os.environ['AWS_REGION'],
        }
    )

    docker.push(
        repository='{0}.dkr.ecr.{1}.amazonaws.com/{2}'.format(
            os.environ['AWS_ACCOUNT_ID'], 
            os.environ['AWS_REGION'], 
            image_name,
        ),
        tag='latest',
    )

    step_functions = boto3.client('stepfunctions')

	timestamp = str(int(time.time()))

	definition = get_definition(
		os.environ['SAGEMAKER_ROLE_ARN'],
		image_name,
		os.environ['DATA_BUCKET_NAME'] + '/data/training.parquet',
		os.environ['DATA_BUCKET_NAME'] + '/' + user_id + '/' + timestamp,
		os.environ['DATA_BUCKET_NAME'] + '/data/predicting.parquet',
		os.environ['DATA_BUCKET_NAME'] + '/' + user_id + '/' + timestamp,
	)

	try:
		state_machine = step_functions.create_state_machine(
			name=user_id + '_' + timestamp,
			definition=definition,
			roleArn=os.environ['STEP_FUNCTION_ROLE_ARN'],
		)
	except Exception as e:
        return {
            Body: str(e),
            StatusCode: 500,
            IsBase64Encoded: False,
        }

    try:
        state_machine.start_execution(
            stateMachineArn=state_machine['stateMachineArn']],
            input=json.dumps({
                'email': email,
                'user_id': user_id,
                'stripe_customer_id': stripe_customer_id,
                'image_name': image_name,
            }),
        )
    except Exception as e:
        return {
            Body: str(e),
            StatusCode: 500,
            IsBase64Encoded: False,
        }

    return {
        Body: json.dumps({
            message: 'successfully started pipeline',
        }),
        StatusCode: 200,
        IsBase64Encoded: False,
    }