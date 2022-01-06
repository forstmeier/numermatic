import numerapi
import boto3


tournament_file_name = 'training.parquet'

def handler(event, context):
	print('event:', event)

    api = numerapi.NumerAPI(
        public_id=config_data[os.getenv('PUBLIC_ID')],
        secret_key=config_data[os.getenv('SECRET_KEY')],
    )

    if not api.check_new_round():
        return None

    try:
        api.download_dataset(
            filename=tournament_file_name,
            dest_path=filepath,
        )
    except Exception as e:
        return e

    s3 = boto3.client('s3')
    try:
        upload_file_response = s3.upload_file(
            tournament_file_name,
            os.getenv('DATA_BUCKET_NAME'),
            'data/'+tournament_file_name,
        )
    except Exception as e:
        return e

    return None