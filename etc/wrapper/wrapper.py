import os
import pickle
from model import model



if __name__ == '__main__':
	model_directory = os.getenv('SM_MODEL_DIR')
	output_directory = os.getenv('SM_OUTPUT_DIR')
	training_data_directory = os.getenv('SM_CHANNEL_TRAINING')

	print('model_directory: {}'.format(model_directory)) # TEMP
	print('output_directory: {}'.format(output_directory)) # TEMP
	print('training_data_directory: {}'.format(training_data_directory)) # TEMP

	trained_model = model.train(training_data_directory)

	model_location = model_directory + '/xgboost-model'
	pickle.dump(trained_model, open(model_location, 'wb'))


def model_fn(model_directory):
	model_file = 'xgboost-model'
	trained_model = pickle.load(open(os.path.join(model_directory, model_file), 'rb'))
	return trained_model