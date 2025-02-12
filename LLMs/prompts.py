import os
import re
import json
import requests
from mistralai import Mistral
from google.oauth2 import service_account
import google.auth.transport.requests
import time


class MistralChat:
    def __init__(self):
        api = os.environ.get("MISTRAL_API_KEY")
        self.model = "mistral-large-latest"
        self.client = Mistral(api_key=api)

        SERVICE_ACCOUNT_FILE = "SERVICE_ACCOUNT_DETAILS.json"
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE,
            scopes=[
                "https://www.googleapis.com/auth/cloud-platform"]
        )
        auth_req = google.auth.transport.requests.Request()
        credentials.refresh(auth_req)
        access_token = credentials.token
        self.endpoint_url = (
            "https://discoveryengine.googleapis.com/v1alpha/projects/592141439586/"
            "locations/global/collections/default_collection/engines/inspireit-v2-1_1739291064695/"
            "servingConfigs/default_search:search"
        )
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

    def clean_text(self, text):
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'&nbsp;', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    def get_clean_snippets(self, result):
        results = result["results"]
        titles = []
        snippets = []
        for i in results:
            doc = i["document"]["derivedStructData"]
            titles.append(doc["title"])
            for j in doc["snippets"]:
                if j["snippet_status"] == "SUCCESS":
                    snippets.append(self.clean_text(j["snippet"]))
        lst = []
        for i, j in enumerate(zip(snippets, titles)):
            lst.append(f"title {i}: {j[1]} snippet {i}: {j[0]}")
        return lst

    def clean_mistral_response(raw_response: str):
        # Remove the ```json\n and \n``` markers
        cleaned = raw_response.replace("```json\n", "").replace("\n```", "")

        # Remove escaped newlines and quotes
        cleaned = cleaned.replace("\\n", "").replace('\\"', '"')

        # Parse the string to JSON
        try:
            json_data = json.loads(cleaned)
            return json_data
        except json.JSONDecodeError as e:
            return {"error": f"Failed to parse JSON: {str(e)}"}

    def get_idea_prompt(self, data: json):
        domains = data.domains
        specifications = data.specifications

        payload = {
            "query": f"Keywords: {','.join(domains)}. Specifications: {specifications}",
            "pageSize": 10,
            "queryExpansionSpec": {"condition": "AUTO"},
            "spellCorrectionSpec": {"mode": "AUTO"},
            "contentSearchSpec": {"snippetSpec": {"returnSnippet": True}}
        }

        response = requests.post(
            self.endpoint_url, headers=self.headers, json=payload)
        response_json = response.json()

        final_lst = self.get_clean_snippets(response_json)

        message = [
            {
                "role": "user",
                "content": (f'''
                    As an AI research consultant, generate creative research ideas based on the following:

                    Domains: {', '.join(domains)}
                    User Specifications: {specifications}

                    Consider the given paper title and with the context of what is written in the paper under the snippet.
                    The snippet and title are numbered accordingly:
                    {', '.join(final_lst)}

                    Provide your response in JSON format with the following structure:
                    {{
                        "ideas": [
                            {{
                                "title": "Idea title",
                                "description": "Very lengthy description",
                                "opportunities": ["opp1", "opp2", ...],
                                "drawbacks": ["drawback1", "drawback2", ...],
                                "references": ["ref1", "ref2", ...]
                            }}
                        ]
                    }}

                    Generate 3 innovative ideas that combine elements from the specified domains.
                ''')
            }
        ]
        response = self.client.chat.complete(
            model=self.model,
            messages=message
        )

        try:
            return json.loads(re.sub(r'^```json\n|\n```$', '', response.choices[0].message.content.strip()))
        except json.JSONDecodeError:
            return {
                "error": "Failed to parse response as JSON",
                "raw_response": response.choices[0].message.content
            }

    def generate_ideas(self, domains: list, specifications: str):
        """
        Wrapper method to generate ideas with simpler parameters
        """
        data = type('Data', (), {'domains': domains,
                    'specifications': specifications})()
        return self.get_idea_prompt(data)


def test_mistral_chat():
    # Initialize the MistralChat class
    mistral = MistralChat()

    # Define test domains and specifications
    test_domains = [
        "Machine Learning",
        "Computer Vision",
        "Generative AI"
    ]

    test_specifications = "Looking for novel approaches in GAN architectures for image synthesis with focus on medical imaging applications"

    # Call generate_ideas
    try:
        ideas = mistral.generate_ideas(
            domains=test_domains,
            specifications=test_specifications
        )

        # Pretty print the results
        print("Generated Ideas:")
        print(json.dumps(ideas, indent=2))

    except Exception as e:
        print(f"Error occurred: {str(e)}")


# Run the test
if __name__ == "__main__":
    test_mistral_chat()
