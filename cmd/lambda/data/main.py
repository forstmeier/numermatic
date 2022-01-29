import os
import boto3
import numerapi


tournament_file_name = 'tournament.parquet'

def handler(event, context):
	print('event:', event)

	api = numerapi.NumerAPI(
		public_id=config_data[os.getenv('PUBLIC_ID')],
		secret_key=config_data[os.getenv('SECRET_KEY')],
	)

	if not api.check_new_round():
		return True

	s3 = boto3.client('s3')

	try:
		api.download_dataset(
			filename=tournament_file_name,
			dest_path=filepath,
		)

		upload_file_response = s3.upload_file(
			tournament_file_name,
			os.getenv('DATA_BUCKET_NAME'),
			'tournament/'+tournament_file_name,
		)
		print('upload_file_response:', upload_file_response)

		return True
	
	except Exception as e:
		print('exception:', e)
		raise e
