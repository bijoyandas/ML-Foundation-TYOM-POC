import logging
import os
import json

logger=logging.getLogger(__name__)

# Defining the Constants
JOB_SUBMISSION_URL = "JOB_SUBMISSION_API_URL"
CLIENT_ID = "clientid"
CLIENT_SECRET = "clientsecret"
AUTHENTICATION_URL = "url"
CREDENTIALS = "credentials"
SERVICE_URLS = "serviceurls"
MLF_NAME = "ml-foundation-trial-beta"
API_VERSION = "v2"

def get_mlf_env_variables():
    vcap_services = json.loads(str(os.getenv("VCAP_SERVICES", {})))
    if MLF_NAME in vcap_services.keys():
        client_id = vcap_services.get(MLF_NAME)[0].get(CREDENTIALS).get(CLIENT_ID)
        client_secret = vcap_services.get(MLF_NAME)[0].get(CREDENTIALS).get(CLIENT_SECRET)
        authentication_url = vcap_services.get(MLF_NAME)[0].get(CREDENTIALS).get(AUTHENTICATION_URL)
        job_url = vcap_services.get(MLF_NAME)[0].get(CREDENTIALS).get(SERVICE_URLS).get(JOB_SUBMISSION_URL)
        return client_id, client_secret, authentication_url, job_url, API_VERSION
    else:
        return None, None, None, None, None
