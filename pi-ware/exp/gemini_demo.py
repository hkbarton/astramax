import requests
import json
import os
from lib import get_var
from google.auth import default
from google.auth.transport.requests import Request
from google.oauth2 import service_account

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(
    os.path.dirname(os.path.abspath(
        __file__)),
    "../deployment/dev/credentials/ghack-service-account.json"
)


def get_access_token():
    SCOPES = ['https://www.googleapis.com/auth/cloud-platform']
    credentials = service_account.Credentials.from_service_account_file(
        '../../deployment/dev/credentials/ghack-service-account.json', scopes=SCOPES)
    credentials.refresh(Request())
    return credentials.token


def generate_content(project_id, model_id):
    url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{project_id}/locations/us-central1/publishers/google/models/{model_id}:streamGenerateContent"
    token = get_access_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    data = {
        "contents": {
            "role": "user",
            "parts": [
                {
                    "fileData": {
                        "mimeType": "video/mp4",
                        "fileUri": f"gs://{get_var('GCS_BUCKET_NAME')}/yosemite.mp4"
                    }
                },
                {
                    "text": "descript what you've seen here."
                }
            ]
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        print("Request successful")
        print(response.json())
    else:
        print(f"Request failed with status code {response.status_code}")
        print(response.text)


# Example usage
generate_content("alchemist-agent-test", "gemini-1.5-flash-001")
