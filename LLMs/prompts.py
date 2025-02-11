import os
from mistralai import Mistral
import json


class MistralChat:
    def __init__(self):
        api = os.environ.get("MISTRAL_API_KEY")
        self.model = "mistral-large-latest"
        self.client = Mistral(api_key=api)

    def get_idea_prompt(self,data:json):
        domains = data.domains
        specifications = data.specification
        
        context_str, results = query_cortex_search_service(
            " ".join(domains + [specifications]),
            columns=["chunk", "file_url", "relative_path"],
            filter={"@and": [{"@eq": {"language": "English"}}]}
        )

        message = [
            {
                "role":"user",
                "content":(f'''
                [INST]
                    As an AI research consultant, generate creative research ideas based on the following:
                    
                    Domains: {', '.join(domains)}
                    User Specifications: {specifications}
                    
                    Consider this relevant context:
                    {context_str}
                    
                    Provide your response in JSON format with the following structure:
                    {{
                        "ideas": [
                            {{
                                "title": "Idea title",
                                "description": "Very lengthy description",
                                "opportunities": ["opp1", "opp2", ...],
                                "drawbacks": ["drawback1", "drawback2", ...],
                                "references": ["ref1", "ref2", ...],
                                ""
                            }}
                        ]
                    }}
                    
                    Generate 3 innovative ideas that combine elements from the specified domains.
                    Include URLs for reference papers where available from the context.
                [/INST]
                ''')
            }
        ]
    
