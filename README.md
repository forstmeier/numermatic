# numermatic

> Numerai model training in the cloud :robot:  

## About :sunglasses:

`numermatic` is a platform for training Numerai models in the cloud. It is a simple, easy to use, and free to use API hosted in your own AWS account.

## Setup :nerd_face:

### Prerequisites

In order to work with the scripts in `bin`, you'll need to have the following installed:  

- [jq](https://stedolan.github.io/jq/) - version `jq-1.6`  
- [AWS CLI](https://aws.amazon.com/cli/) - version `aws-cli/1.19.53 Python/3.8.10 Linux/5.11.0-36-generic botocore/1.20.53`  
- [SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install-linux.html)- version `SAM CLI, version 1.22.0`  

:warning: This code has been developed locally on an Ubuntu machine and has not been tested on other systems.  

### Installation

Ensure that you have already created both a "data" and "artifacts" bucket created before you run the following commands. The "data" bucket should have the following structure and Numerai data files.  

```
bucket/
|_ training/
|  |_ numerai_training_data.csv
|_ transform/
   |_ numerai_tournament_data.csv
```

Clone this repository and add a `samconfig.toml` file to the repository root directory. See `etc/examples/samconfig.toml` for an example.  

After that, run the helper scripts below to setup the resources in your AWS account.  

```
./bin/build_stack
./bin/launch_stack
```

## Usage :partying_face:

Add a user to the application and get a user ID token.  

```
./bin/add_user <email>
```

Upload a ZIPed model file to the application and begin a training execution. The ZIP file should contain both a `model.py` file and a `requirements.txt`.  

```
./bin/upload_model <user_id_token> <model_file_path>
```

### Notes

#### Current Status

> :warning: This application is still in development.  

The "transform" step of the training flow is currently failing and is a help wanted issue. The `models` and `end` Lambda functions still need to be wrapped up. Not all of the Lambdas have been comprehensively tested yet either.  

#### Future Work

1. An email notification with the presigned URLs for the trained model when it's completed.  
2. Replace the hard-coded XGBoost with a custom image to accept more frameworks.  
3. TBD

These are likely dependent on Numerai community support and/or code contributions.  

## Contribute :zany_face:

Fork this repository and send a pull request. Follow Python best practices for structure and formatting! :tada:  