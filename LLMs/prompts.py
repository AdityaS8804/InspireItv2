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
        self.context=[]

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
        links = []
        for i in results:
            doc = i["document"]["derivedStructData"]
            titles.append(doc["title"])
            links.append(doc["link"])
            for j in doc["snippets"]:
                if j["snippet_status"] == "SUCCESS":
                    snippets.append(self.clean_text(j["snippet"]))
        lst = []
        for i, j in enumerate(zip(snippets, titles, links)):
            lst.append(f"title {i}: {j[1]} snippet {i}: {j[0]} link {i}: {j[2]}")
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
            "pageSize": 20,
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
                                "summary": "Very lengthy description",
                                "opportunities": ["opp1", "opp2", ...],
                                "drawbacks": ["drawback1", "drawback2", ...],
                                "references": {{
                                        1:{{
                                            title: ref1 title,
                                            link: google storage link of ref1
                                        }},
                                        2:{{
                                            title: ref2 title,
                                            link: google storage link of ref2
                                        }},
                                        {{
                                        3:{{
                                            title: ref3 title,
                                            link: google storage link of ref3
                                        }},...
                                    }}
                                }}
                            }}
                        ]
                    }}

                    Generate 3 innovative research ideas that combine elements from the specified domains. The ref1, ref2, ref3 and so on
                    are the referenced paper for that idea and link is their corresponding google storage link (the link has a format of gs://link)
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
        
    def recommend_ideas(self, data: dict):
        title = data["title"]
        summary = data["summary"]
        drawbacks = data["drawbacks"]
        opportunities = data["opportunities"]
        
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
                "raw_response": response.choices[0].message.content
            }

    def research_chat(self, user_message: str):
        """
        A conversational interface for the research bot.
        
        Args:
            user_message (str): The user's input message
            context (list, optional): List of previous messages for maintaining conversation context
        """
        #if context is None:
        #    context = []
        
        # Add user's message to context
        self.context.append({"role": "user", "content": user_message})
        
        # System message to define bot's behavior
        system_message = {
            "role": "system",
            "content": """You are a helpful research assistant with expertise in analyzing and suggesting research ideas. 
            You can help with:
            1. Understanding research concepts
            2. Suggesting improvements to research ideas
            3. Recommending related papers and methodologies
            4. Explaining technical concepts
            5. Discussing research implications and potential directions
            you are not allowed to give any special commands like /generate domains | specifications, /improve {json_data}
            and /recommend {json_data}.
            Keep responses conversational but informative."""
        }
        
        # Prepare messages for chat
        messages = [system_message] + self.context
        
        try:
            # Get response from Mistral
            response = self.client.chat.complete(
                model=self.model,
                messages=messages
            )
            
            # Add assistant's response to context
            assistant_message = response.choices[0].message.content
            self.context.append({"role": "assistant", "content": assistant_message})
            
            return {
                "response": assistant_message,
                "context": self.context
            }
        except Exception as e:
            return {
                "error": f"Error in chat: {str(e)}",
                "context": self.context
            }

# def test_mistral_chat():
#     # Initialize the MistralChat class
#     mistral = MistralChat()

#     # Define test domains and specifications
#     test_domains = [
#         "Machine Learning",
#         "Computer Vision",
#         "Generative AI"
#     ]

#     test_specifications = "Looking for novel approaches in GAN architectures for image synthesis with focus on medical imaging applications"

#     # Call generate_ideas
#     try:
#         ideas = mistral.generate_ideas(
#             domains=test_domains,
#             specifications=test_specifications
#         )

#         # Pretty print the results
#         print("Generated Ideas:")
#         print(json.dumps(ideas, indent=2))

#     except Exception as e:
#         print(f"Error occurred: {str(e)}")


# # Run the test
# if __name__ == "__main__":
#     test_mistral_chat()

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


# def test_research_chat():
#     mistral = MistralChat()
    
#     # Initialize conversation context
#     context = []
    
#     while True:
#         # Get user input
#         user_input = input("\nYou: ")
        
#         # Check for exit command
#         if user_input.lower() in ['exit', 'quit', 'bye']:
#             print("\nAssistant: Goodbye! Feel free to return if you have more research questions.")
#             break
            
#         # Process commands for specific functions
#         if user_input.lower().startswith('/generate'):
#             # Extract domains and specifications
#             parts = user_input[9:].split('|')
#             if len(parts) >= 2:
#                 domains = [d.strip() for d in parts[0].split(',')]
#                 specifications = parts[1].strip()
#                 result = mistral.generate_ideas(domains, specifications)
#                 print("\nAssistant: Here are some generated ideas:")
#                 print(json.dumps(result, indent=2))
#                 continue
                
#         elif user_input.lower().startswith('/improve'):
#             # Parse the improvement request
#             try:
#                 data = json.loads(user_input[8:])
#                 result = mistral.suggestion_improvement_idea_prompt(data)
#                 print("\nAssistant: Here's the improved idea:")
#                 print(json.dumps(result, indent=2))
#                 continue
#             except json.JSONDecodeError:
#                 print("\nAssistant: Please provide the idea details in valid JSON format.")
#                 continue
                
#         elif user_input.lower().startswith('/recommend'):
#             try:
#                 data = json.loads(user_input[10:])
#                 result = mistral.recommend_ideas(data)
#                 print("\nAssistant: Here are the recommendations:")
#                 print(json.dumps(result, indent=2))
#                 continue
#             except json.JSONDecodeError:
#                 print("\nAssistant: Please provide the idea details in valid JSON format.")
#                 continue
        
#         # Normal chat processing
#         result = mistral.research_chat(user_input, context)
        
#         if "error" in result:
#             print(f"\nAssistant: Sorry, an error occurred: {result['error']}")
#         else:
#             print(f"\nAssistant: {result['response']}")
#             context = result['context']

# if __name__ == "__main__":
#     test_research_chat()