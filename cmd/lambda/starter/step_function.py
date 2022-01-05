import json


def get_definition(
	role_arn, 
	image_uri, 
	training_data_uri, 
	training_artifacts_path, 
	prediction_data_uri, 
	prediction_artifacts_path,
):
	definition_object = {
	'StartAt': 'trainState',
	'States': {
		'trainState': {
			'Type': 'Task',
			'Resource': 'arn:aws:states:::sagemaker:createTrainingJob.sync',
			'Parameters': {
				'AlgorithmSpecification': {
					'TrainingImage': image_uri,
					'TrainingInputMode': 'FastFile' # NOTE: may not be the exact option - https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_AlgorithmSpecification.html
				},
				# Environment: {}, # NOTE: this might not really be needed but worth noting
				'InputDataConfig': [{
					'ChannelName': 'train',
					'DataSource': {
						'S3DataSource': {
							# 'S3DataDistributionType': 'ShardedByS3Key', # NOTE: probably not needed
							'S3DataType': 'S3Prefix',
							'S3Uri': training_data_uri # NOTE: example - s3://bucketname/exampleprefix/data.parquet
						}
					},
					'InputMode': 'FastFile' # NOTE: may not be needed
				}],
				'OutputDataConfig': {
					'S3OutputPath': training_artifacts_path # NOTE: example - s3://bucketname/models
				},
				'ResourceConfig': {
					'InstanceCount': 1,
					'InstanceType': 'ml.m4.xlarge',
					'VolumeSizeInGB': 30
				},
				'RoleArn': role_arn,
				'StoppingCondition': {
					'MaxRuntimeInSeconds': 10800
				},
				'TrainingJobName.$': '$$.Execution.Name'
			},
			'Catch': [
				'ErrorEquals': [ 'States.ALL' ],
				'Next': 'alertState'
			],
			'Next': 'batchTransformState'
		},
		'createModelState': {
			'Type': 'Task',
			'Resource': 'arn:aws:states:::sagemaker:createModel',
			'Parameters': {
				'PrimaryContainer': {
					'Image': image_uri,
					'ModelDataUrl.$': '$.ModelArtifacts.S3ModelArtifacts'
				},
				'ExecutionRoleArn': role_arn,
				'ModelName.$': '$.TrainingJobName'
			},
			'Catch': [
				'ErrorEquals': [ 'States.ALL' ],
				'Next': 'alertState'
			],
			'Next': 'batchTransformState'
		},
		'batchTransformState': {
			'Type': 'Task',
			'Resource': 'arn:aws:states:::sagemaker:createTransformJob.sync',
			'Parameters': {
				# Environment: {}, # NOTE: this might not really be needed but worth noting
				'ModelName.$': '$$.Execution.Name',
				'TransformInput': {
					'DataSource': {
						'S3DataSource': {
							'S3DataType': 'S3Prefix',
							'S3Uri': prediction_data_uri
						}
					}
				},
				'TransformJobName.$': '$$.Execution.Name',
				'TransformOutput': {
					'S3OutputPath': prediction_artifacts_path
				},
				'TransformResources': {
					'InstanceCount': 1,
					'InstanceType': 'ml.m4.xlarge'
				}
			},
			'Catch': [
				'ErrorEquals': [ 'States.ALL' ],
				'Next': 'alertState'
			],
			'Next': 'messageState'
		},
		'messageState': {
			'Type': 'Task',
			'Resource': 'messageFunction',
			'Next': 'successState'
		},
		'successState': {
			'Type': 'Succeed'
		},
		'alertState': {
			'Type': 'Task',
			'Resource': 'alerterFunction',
			'Next': 'failState'
		},
		'failState': {
			'Type': 'Fail',
			'Error': 'State Machine Failed', # NOTE: replace w/ dynamic error message
			'Cause': 'State Machine Failed' # NOTE: replace w/ dynamic error message
		}
	}

	return json.dump(definition_object)
}