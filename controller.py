from flask import Flask, request
import os
import random
import logging
import uuid
import yaml
import json
from utils.minio_helper import get_minio_credentials, upload_file_to_minio, get_file_from_minio
from utils.vcap_helper import get_mlf_env_variables
from utils.job_helper import submit_job

app = Flask(__name__)

port = int(os.getenv("PORT"))

logger=logging.getLogger(__name__)

current_job_id = None
class_def = {0: "Don't advertise", 1: "Do Advertise"}

@app.route('/health', methods=['GET'])
def getHelloWorld():
	logger.info("Inside /health")
	return "Up"

@app.route('/train', methods=['GET'])
def train_model():
	global current_job_id
	logger.info("Inside /train")
	client_id, client_secret, authentication_url, job_url, API_VERSION = get_mlf_env_variables()
	end_point, access_key, secret_key = get_minio_credentials(job_url, API_VERSION, authentication_url, client_id, client_secret)
	job_id = uuid.uuid4()
	job_name = "Training"
	remote_data_dir = "jobs/{}-{}".format(job_name, str(job_id))
	# Upload the dataset to Minio
	upload_file_to_minio("datasets/SocialMediaAdv.csv", "{}/SocialMediaAdv.csv".format(remote_data_dir), end_point, access_key, secret_key, csv = True)

	# Upload Job code files to Minio
	upload_file_to_minio("utils/code/model_training.py", "{}/model_training.py".format(remote_data_dir), end_point, access_key, secret_key, csv = False)
	upload_file_to_minio("utils/code/requirements.txt", "{}/requirements.txt".format(remote_data_dir), end_point, access_key, secret_key, csv = False)

	# Defining the Job Configuration
	job_config = {
    	'job': {
        	'name': job_name,
            'env': [
				{
					"name" : "job_name",
                	"value" : job_name
				},
				{
					"name": "job_id",
					"value": str(job_id)
				}
			],
            'execution': {
                'command': 'pip3 install -r requirements.txt && python3 model_training.py',
                'completionTime': 10000,
                'image': 'ml-foundation/sklearn:0.19.1-py3',
				'resourcePlanId': 'basic',
                'retries': 0
            }
        }
    }
	job_description = yaml.dump(yaml.load(json.dumps(job_config), Loader=yaml.FullLoader))
	job_status = submit_job(job_url, API_VERSION, authentication_url, client_id, client_secret, job_id, job_description)

	logger.error(job_status)
	if job_status["status"] in ["RUNNING", "PENDING"]:
		logger.info("Job submitted with id {} and status {}".format(str(job_id), job_status["status"]))
		current_job_id = job_id
		return app.response_class(
			response=json.dumps({"message": "Job submitted with id {} and status {}".format(str(job_id), job_status["status"])}),
	        status=200,
	        mimetype='application/json'
		)
	else:
		return app.response_class(
			response=json.dumps({"message": "Job couldn't be submitted"}),
	        status=200,
	        mimetype='application/json'
		)

@app.route('/predict', methods=['POST'])
def predict():
	global current_job_id
	global class_def
	logger.info("Inside /predict")
	client_id, client_secret, authentication_url, job_url, API_VERSION = get_mlf_env_variables()
	end_point, access_key, secret_key = get_minio_credentials(job_url, API_VERSION, authentication_url, client_id, client_secret)
	payload = request.json
	if "age" not in payload.keys() or "salary" not in payload.keys():
		return app.response_class(
			response=json.dumps({"message": "Insufficient number of parameters sent"}),
			status=200,
			mimetype="application/json"
		)
	age = payload.get("age")
	salary = payload.get("salary")
	model_path = "jobs/Training-{}/model.pkl".format(str(current_job_id))
	scaler_path = "jobs/Training-{}/scaler.pkl".format(str(current_job_id))
	model = get_file_from_minio(model_path, end_point, access_key, secret_key)
	sc = get_file_from_minio(scaler_path, end_point, access_key, secret_key)
	if model is None or sc is None:
		return app.response_class(
			response=json.dumps({"message": "Cannot provide prediction now for model {}".format(model_path)}),
			status=200,
			mimetype='application/json'
		)
	prediction = model.predict(sc.transform([[age, salary]]))[0]
	return app.response_class(
		response=json.dumps({"prediction": class_def[prediction]}),
		status=200,
		mimetype="application/json"
	)

app.run(host='0.0.0.0', port=port)
