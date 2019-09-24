import logging
import requests
from minio import Minio
import os
from utils.jwt_helper import get_ml_request_header
from sklearn.externals import joblib

logger = logging.getLogger(__name__)

def get_minio_response(job_submission_url, api_version, authentication_url, client_id, client_secret):
    url = "{}/api/{}/storage".format(job_submission_url, api_version)
    response = requests.get(url=url, headers=get_ml_request_header(authentication_url, client_id, client_secret))
    return response.json()

def get_minio_credentials(job_submission_url, api_version, authentication_url, client_id, client_secret):
    minio_credentials = get_minio_response(job_submission_url, api_version, authentication_url, client_id, client_secret)
    logger.error("Minio Credentials")
    logger.error(minio_credentials)
    end_point = minio_credentials['endpoint']
    access_key = minio_credentials['accessKey']
    secret_key = minio_credentials['secretKey']
    return end_point, access_key, secret_key

def upload_file_to_minio(local_file_path, remote_file_path, end_point, access_key, secret_key, csv = True):
    minioClient = Minio(end_point,
                    access_key= access_key,
                    secret_key= secret_key,
                    secure=True)
    if not minioClient.bucket_exists("data"):
        logger.error("Bucket 'data' doesn't exist. Creating it...")
        minioClient.make_bucket("data")
        logger.error("Bucket 'data' created")
    with open(local_file_path, "rb") as f:
        file_stat = os.stat(local_file_path)
        if csv:
            logger.error("Uploading File {}".format(remote_file_path))
            minioClient.put_object('data', remote_file_path, f, file_stat.st_size, content_type='application/csv')
            logger.error("Uploaded File {}".format(remote_file_path))
        else:
            logger.error("Uploading File {}".format(remote_file_path))
            minioClient.put_object('data', remote_file_path, f, file_stat.st_size)
            logger.error("Uploaded File {}".format(remote_file_path))

def get_file_from_minio(remote_file_path, end_point, access_key, secret_key):
    minioClient = Minio(end_point,
                    access_key= access_key,
                    secret_key= secret_key,
                    secure=True)
    try:
        logger.error("Fetching file {}".format(remote_file_path))
        minioClient.fget_object("data", remote_file_path, "file.pkl")
        logger.error("Fetched file {}".format(remote_file_path))
        logger.error("Saved file.pkl")
        file = joblib.load("file.pkl")
        os.remove("file.pkl")
        logger.error("Returning file")
        return file
    except Exception as e:
        logger.error(e)
        logger.error("Couldn't fetch the file")
        return None
