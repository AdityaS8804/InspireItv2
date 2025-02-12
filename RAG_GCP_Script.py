import os
import json
import requests
from google.oauth2 import service_account
import google.auth.transport.requests

# Path to your service account JSON key file
SERVICE_ACCOUNT_FILE = "SERVICE_ACCOUNT_DETAILS.json"

# Create credentials from the service account file
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)

# Refresh credentials to get a valid access token
auth_req = google.auth.transport.requests.Request()
credentials.refresh(auth_req)
access_token = credentials.token

# Define the Vertex Search endpoint URL and headers
endpoint_url = (
    "https://discoveryengine.googleapis.com/v1alpha/projects/592141439586/"
    "locations/global/collections/default_collection/engines/inspireitv2_1739261898335/"
    "servingConfigs/default_search:search"
)
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

# Define the JSON payload for your search query
payload = {
    "query": "Digital attacks",
    "pageSize": 10,
    "queryExpansionSpec": {"condition": "AUTO"},
    "spellCorrectionSpec": {"mode": "AUTO"},
    "contentSearchSpec": {"snippetSpec": {"returnSnippet": True,

                                          }}
}

# Make the POST request to the Vertex Search endpoint
response = requests.post(endpoint_url, headers=headers, json=payload)

# Process the response
if response.ok:
    result = response.json()
    print(json.dumps(result, indent=2))
else:
    print(
        f"Request failed with status code {response.status_code}: {response.text}")
