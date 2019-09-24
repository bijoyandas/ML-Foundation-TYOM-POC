import logging
import requests
from utils.jwt_helper import get_ml_request_header

logger=logging.getLogger(__name__)

def submit_job(job_submission_url, api_version, authentication_url, client_id, client_secret, job_id, job_description):
    url = "{}/api/{}/jobs/{}".format(job_submission_url, api_version, job_id)
    response = requests.post(url=url, data=job_description, headers=get_ml_request_header(authentication_url, client_id, client_secret))
    if response.status_code in (200, 201, 202):
        logger.error("Training has been Invoked")
        return response.json()
    else:
        logger.error("Couldn't submit job with job-id {} ".format(job_id))
        return {}
