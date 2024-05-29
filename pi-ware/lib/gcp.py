import requests
import json
import os
from google.cloud import storage
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from lib import get_var

credential_file = os.path.join(
    os.path.dirname(os.path.abspath(
        __file__)),
    "../../deployment/dev/credentials/ghack-service-account.json"
)


class CloudService:
    @staticmethod
    def upload_to_gcs(source_file_name, dest_file_name):
        """Uploads a file to the bucket."""
        storage_client = storage.Client()
        bucket = storage_client.bucket(get_var('GCS_BUCKET_NAME'))
        blob = bucket.blob(dest_file_name)
        blob.upload_from_filename(source_file_name)

    @staticmethod
    def get_access_token():
        SCOPES = ['https://www.googleapis.com/auth/cloud-platform']
        credentials = service_account.Credentials.from_service_account_file(
            credential_file, scopes=SCOPES)
        credentials.refresh(Request())
        return credentials.token

    @staticmethod
    def generate_content(prompt: str, video_file_name: str):
        url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{get_var('PROJECT_ID')}/locations/us-central1/publishers/google/models/gemini-1.5-flash-001:streamGenerateContent"
        token = CloudService.get_access_token()
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
                            "fileUri": f"gs://{get_var('GCS_BUCKET_NAME')}/{video_file_name}"
                        }
                    },
                    {
                        "text": prompt
                    }
                ]
            }
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        return response.text
