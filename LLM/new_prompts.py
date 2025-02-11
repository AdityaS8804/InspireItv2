# new_prompts.py
import os
from typing import Dict, Any, Optional
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession
import json
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DiscoveryEngineClient:
    def __init__(self):
        self.base_url = "https://discoveryengine.googleapis.com/v1alpha"
        self.project_id = "592141439586"
        self.engine_id = "inspireitv2_1739261898335"
        self.location = "global"
        try:
            self.credentials = self._get_credentials()
            logger.debug("Successfully initialized credentials")
        except Exception as e:
            logger.error(f"Failed to initialize credentials: {str(e)}")
            raise

    def _get_credentials(self):
        key_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        logger.debug(f"Looking for credentials at: {key_path}")
        
        if not key_path:
            raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable not set")
        
        if not os.path.exists(key_path):
            raise FileNotFoundError(f"Credentials file not found at {key_path}")
            
        return service_account.Credentials.from_service_account_file(
            key_path,
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )

    def search(self, query: str) -> Dict[str, Any]:
        try:
            logger.debug(f"Starting search with query: {query}")
            authed_session = AuthorizedSession(self.credentials)
            
            endpoint = f"{self.base_url}/projects/{self.project_id}/locations/{self.location}/collections/default_collection/engines/{self.engine_id}/servingConfigs/default_search:search"
            logger.debug(f"Using endpoint: {endpoint}")
            
            payload = {
                "query": query,
                "pageSize": 10,
                "queryExpansionSpec": {"condition": "AUTO"},
                "spellCorrectionSpec": {"mode": "AUTO"},
                "contentSearchSpec": {
                    "snippetSpec": {"returnSnippet": True},
                    "extractiveContentSpec": {
                        "maxExtractiveAnswerCount": 1,
                        "maxExtractiveSegmentCount": 1
                    }
                }
            }
            
            logger.debug(f"Sending request with payload: {json.dumps(payload, indent=2)}")
            
            response = authed_session.post(endpoint, json=payload)
            response.raise_for_status()
            
            result = response.json()
            logger.debug(f"Received raw response: {json.dumps(result, indent=2)}")
            
            if not result.get('results'):
                logger.warning("No results found in the response")
                return {
                    "message": "No results found",
                    "results": []
                }
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            return {
                "error": f"API request failed: {str(e)}",
                "results": []
            }
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON response: {str(e)}")
            return {
                "error": f"Failed to decode JSON response: {str(e)}",
                "results": []
            }
        except Exception as e:
            logger.error(f"Unexpected error in search: {str(e)}")
            return {
                "error": f"Unexpected error: {str(e)}",
                "results": []
            }
