import requests
import logging

logger = logging.getLogger(__name__)

def get_ml_request_header(xsuaa_base_url, client_id, client_secret):
    response = requests.get(url= xsuaa_base_url + "/oauth/token",
                            params= {"grant_type": "client_credentials"},
                            auth= (client_id, client_secret))
    if response.status_code == 200:
        access_token = response.json()["access_token"]
        return {"Authorization": "Bearer {}".format(access_token), "Accept": "application/json"}
    else:
        return {"message": "Something went wrong"}
