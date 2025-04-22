from dotenv import load_dotenv
from datetime import datetime, timedelta
import logging
import requests
# from config import LOG_FILE

load_dotenv()

log_file = "myapp.log"

class APIClient42:
    def __init__(self, client_id, client_secret):
        """Init the APIClient42 class"""
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://api.intra.42.fr"
        self.token = None
        self.token_expiry = None

    def get_token(self):
        """Get a new access token from the 42 API"""
        url = f"{self.base_url}/oauth/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        response = requests.post(url, data=data)
        if response.status_code == 200:
            token_data = response.json()
            self.token = token_data["access_token"]
            # Set expiry time (subtract 5 minutes to be safe)
            self.token_expiry = datetime.now() + timedelta(seconds=token_data["expires_in"] - 300)
            return self.token
        # else:
        #     raise Exception
