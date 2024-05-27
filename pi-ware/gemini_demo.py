import requests
import json
import subprocess


def get_access_token():
    result = subprocess.run(
        ["gcloud", "auth", "application-default", "print-access-token"], stdout=subprocess.PIPE)
    return result.stdout.decode('utf-8').strip()


def generate_content(project_id, model_id):
    url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{
        project_id}/locations/us-central1/publishers/google/models/{model_id}:streamGenerateContent"
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
                        "fileUri": "gs://ghack2024/yosemite.mp4"
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
