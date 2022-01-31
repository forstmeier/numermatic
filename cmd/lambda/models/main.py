import os
import boto3
from sagemaker.xgboost.estimator import XGBoost
from sagemaker.transformer import Transformer
from sagemaker.inputs import TrainingInput
from stepfunctions.steps.states import Chain
from stepfunctions.steps.sagemaker import TrainingStep, ModelStep, TransformStep
from stepfunctions.steps.compute import LambdaStep
from stepfunctions.workflow import Workflow


def handler(event, context):
	print('event:', event)

	bucket = event['Records'][0]['s3']['bucket']['name']
	key = event['Records'][0]['s3']['object']['key']

	if 'requirements.txt' not in key:
		return None # TEMP

	key_split = key.split('/')

	user_id = key_split[0]
	execution_id = key_split[1]

	try:
		s3 = boto3.client('s3')

		local_requirements_file = '/tmp/requirements.txt'
		get_requirements_object_response = s3.download_file(
			Bucket=bucket,
			Key=key,
			Filename=local_requirements_file,
		)

		local_model_file = '/tmp/model.py'
		model_key = key.replace('requirements.txt', 'model.py')
		get_model_object_response = s3.download_file(
			Bucket=bucket,
			Key=model_key,
			Filename=local_model_file,
		)

		local_wrapper_file = '/tmp/wrapper.py'
		get_wrapper_object_response = s3.download_file(
			Bucket=os.getenv('MODELS_BUCKET_NAME'),
			Key='numermatic/wrapper.py',
			Filename=local_wrapper_file,
		)

		outputs_bucket = os.getenv('OUTPUTS_BUCKET_NAME')

		output_path = 's3://{}/{}/{}/output'.format(outputs_bucket, user_id, execution_id)

		model_name = 'model-{}-{}'.format(user_id, execution_id)	

		estimator = XGBoost(
			entry_point=local_wrapper_file,
			source_dir='/tmp/',
			framework_version='1.3-1',
			py_version='py3',
			instance_count=1,
			instance_type='ml.m5.2xlarge',
			role=os.getenv('SAGEMAKER_ROLE_ARN'),
			output_path=output_path,
		)

		transformer = Transformer(
			model_name=model_name,
			instance_count=1,
			instance_type='ml.m5.2xlarge',
			output_path=output_path,
			strategy='MultiRecord',
		)

		data_bucket_uri = 's3://{}'.format(os.getenv('DATA_BUCKET_NAME'))

		training_input = TrainingInput(
			s3_data=data_bucket_uri + '/training',
			content_type='text/csv',
		)

		training_step = TrainingStep(
			state_id='training',
			estimator=estimator,
			job_name='training-{}-{}'.format(user_id, execution_id),
			data=training_input,
		)

		model_step = ModelStep(
			state_id='model',
			model=training_step.get_expected_model(),
			model_name=model_name,
		)

		# NOTE: eventually add in additional transform step for validation
		transform_step = TransformStep(
			state_id='transform', 
			transformer=transformer,
			job_name='transform-{}-{}'.format(user_id, execution_id),
			model_name=model_name,
			data=data_bucket_uri + '/transform',
			split_type='Line',
			content_type='text/csv',
		)

		ender_step = LambdaStep(
			state_id='ender',
			resource=os.getenv('ENDER_FUNCTION_ARN'),
			parameters={
				'FunctionName': 'enderFunction',
			},
		)

		workflow_definition = Chain([
			training_step,
			model_step,
			transform_step,
			ender_step,
		])

		workflow = Workflow(
			name='numermatic-{}-{}'.format(user_id, execution_id),
			definition=workflow_definition,
			role=os.getenv('STEP_FUNCTION_ROLE_ARN'),
		)

		workflow_arn = workflow.create()
		print('workflow_arn:', workflow_arn)

		execution = workflow.execute()
		print('execution:', execution)

		# outline:
		# [ ] generate presigned urls
		# [ ] send success email

	except Exception as e:
		print('exception:', e)

		# outline:
		# [ ] send error email

