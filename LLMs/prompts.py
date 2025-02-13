import os
import re
import json
import requests
from mistralai import Mistral
from google.oauth2 import service_account
import google.auth.transport.requests


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
            "locations/global/collections/default_collection/engines/inspireit-v2-2_1739294394126/"
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

        print("RESPONSE: \n")

        print(json.dumps(response_json, indent=True))

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
                                "summary": "Very lengthy description",
                                "opportunities": ["opp1", "opp2", ...],
                                "drawbacks": ["drawback1", "drawback2", ...],
                                "references": ["ref1", "ref2", ...]
                            }}
                        ]
                    }}

                    Generate 3 innovative research ideas that combine elements from the specified domains.
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

    def suggestion_improvement_idea_prompt(self, data:dict):
        
        title = data["origDetails"]["title"]
        summary = data["origDetails"]["summary"]
        drawbacks = data["origDetails"]["drawbacks"]
        opportunities = data["origDetails"]["opportunities"]
        specifications = data["specifications"]

        payload = {
            "query": f"Title of idea: {title}. Idea summary: \n{summary}. Specifications: \n{specifications}",
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
                    As an AI research consultant, you are given a research idea with the following details below:

                    Title: {title}
                    Summary of idea: {summary}
                    Drawbacks: {drawbacks}
                    Opportunities: {opportunities}
                    Specifications: {specifications}

                    Consider the given paper title and with the summary of what is written in the summary section. And according to the user given
                    changes in specifications part, make those changes and use the snippets of paper given below as a reference for those changes.
                    The title and snippets are numbered accordingly below:

                    {', '.join(final_lst)}

                    Provide your response in JSON format with the following structure:
                    {{
                        "improved_idea": [
                            {{
                                "title": "new title to the improved idea",
                                "description": "explain the improved idea in very detailed around 100 words",
                                "opportunities": ["opp1", "opp2", ...],
                                "drawbacks": ["drawback1", "drawback2", ...],
                                "references": ["ref1", "ref2", ...]
                            }}
                        ]
                    }}
                    Under references give the title of the research paper which the research idea is referred to.
                    Generate the improced idea that uses the changes specified by user given under the specifications section in the start.
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
        
    def recommend_ideas(self, data: json):
        title = data.title
        summary = data.summary
        drawbacks = data.drawbacks
        opportunities = data.opportunities
        
        payload = {
            "query": f"Title of idea: {title}. Idea summary: \n{summary}",
            "pageSize": 10,
            "queryExpansionSpec": {"condition": "AUTO"},
            "spellCorrectionSpec": {"mode": "AUTO"},
            "contentSearchSpec": {"snippetSpec": {"returnSnippet": True}}
        }
        
        response = requests.post(self.endpoint_url, headers=self.headers, json=payload)
        response_json = response.json()
        final_lst = self.get_clean_snippets(response_json)
        
        message = [
            {
                "role": "user",
                "content": (f'''
                [INST]
                As an AI research consultant, you are given a research idea with the following details below:
                
                Title: {title}
                Summary of idea: {summary}
                Drawbacks: {drawbacks}
                Opportunities: {opportunities}
                
                Consider the given paper title and with the summary of what is written in the summary section.
                The title and snippets are numbered accordingly below:
                {', '.join(final_lst)}
                
                Provide your response in JSON format with the following structure:
                {{
                    "improved_idea": [
                        {{
                            "title": "{title}",
                            "Abstract": "take reference of the summary and make it the most detailed in around 300 - 400 words",
                            "Methodology_recommended": "Suggest method which the user can use to implement the idea",
                            "Existing_work": ["ref1", "ref2", ...]
                        }}
                    ]
                }}
                
                Under existing work section give the title of the research paper which the research idea is referred to.
                [/INST]
                ''')
            }
        ]
        
        # Get response from Mistral
        response = self.client.chat.complete(
            model=self.model,
            messages=message
        )
        
        # Parse and return the response
        try:
            return json.loads(re.sub(r'^```json\n|\n```$', '', response.choices[0].message.content.strip()))
        except json.JSONDecodeError:
            return {
                "error": "Failed to parse response as JSON",
                "raw_response": response.messages[0].content
            }

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

# def test_improvement_prompt():
#     # Initialize the MistralChat class
#     mistral = MistralChat()
    
#     # Create test data
#     class TestData:
#         def __init__(self):
#             self.title = "Multi-Scale Hierarchical GANs for Medical Image Synthesis"
#             self.summary = "A novel GAN architecture that leverages multi-scale hierarchical representations to synthesize high-fidelity medical images. The model focuses on different levels of detail during the synthesis process."
#             self.drawbacks = [
#                 "Complexity in training multi-scale hierarchical models",
#                 "Potential computational overhead",
#                 "Challenges in ensuring clinical validity"
#             ]
#             self.opportunities = [
#                 "Enhanced image reconstruction quality",
#                 "Potential to improve diagnostic accuracy",
#                 "Ability to generate diverse realistic images"
#             ]
#             self.specifications = "Improve the architecture by incorporating attention mechanisms and focusing on computational efficiency"
    
#     test_data = TestData()
    
#     # Call the improvement prompt
#     try:
#         response = mistral.suggestion_improvement_idea_prompt(test_data)
        
#         # Clean the response if needed
#         if "raw_response" in response:
#             print("Cleaned Response:")
#             print(json.dumps(response, indent=2))
#         else:
#             print("Original Response:")
#             print(json.dumps(response, indent=2))
            
#     except Exception as e:
#         print(f"Error occurred: {str(e)}")

# if __name__ == "__main__":
#     test_improvement_prompt()

# def test_recommend_ideas():
#     # Initialize the MistralChat class
#     mistral = MistralChat()
    
#     # Create test data
#     class TestData:
#         def __init__(self):
#             self.title = "Transformer-Enhanced GANs for Medical Image Segmentation"
#             self.summary = "A novel approach combining transformer networks with GANs for enhanced medical image segmentation. The model leverages transformer's ability to capture global context while using GANs for generating realistic segmentation masks."
#             self.drawbacks = [
#                 "High computational complexity",
#                 "Need for large training datasets",
#                 "Potential instability in training"
#             ]
#             self.opportunities = [
#                 "Improved segmentation accuracy",
#                 "Better handling of complex anatomical structures",
#                 "Potential for real-time applications"
#             ]
    
#     test_data = TestData()
    
#     # Call the recommend ideas method
#     try:
#         response = mistral.recommend_ideas(test_data)
        
#         # Clean the response if needed
#         if "raw_response" in response:
#             cleaned_response = clean_mistral_response(response["raw_response"])
#             print("Cleaned Response:")
#             print(json.dumps(cleaned_response, indent=2))
#         else:
#             print("Original Response:")
#             print(json.dumps(response, indent=2))
            
#     except Exception as e:
#         print(f"Error occurred: {str(e)}")

# if __name__ == "__main__":
#     test_recommend_ideas()