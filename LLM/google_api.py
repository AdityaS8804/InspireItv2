import requests
import google.auth
from google.auth.transport.requests import Request
import json

def query_cortex_search_service(query, columns=None, filter=None):
    """
    Query the Google Discovery Engine API
    
    Args:
        query (str): Search query
        columns (list): List of columns to return
        filter (dict): Filter criteria
        
    Returns:
        tuple: (context_string, results)
    """
    try:
        # Get credentials
        credentials, project = google.auth.default()
        credentials.refresh(Request())
        
        # Debug print
        print(f"[DEBUG] Using project: {project}")
        print(f"[DEBUG] Query: {query}")
        
        # API endpoint
        url = "https://discoveryengine.googleapis.com/v1alpha/projects/592141439586/locations/global/collections/default_collection/engines/inspireitv2_1739261898335/servingConfigs/default_search:search"
        
        # Request headers
        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Content-Type": "application/json"
        }
        
        # Request body
        payload = {
            "query": query,
            "pageSize": 10,
            "queryExpansionSpec": {"condition": "AUTO"},
            "spellCorrectionSpec": {"mode": "AUTO"},
            "contentSearchSpec": {"snippetSpec": {"returnSnippet": True}}
        }
        
        # Debug print
        print(f"[DEBUG] Making API request to: {url}")
        
        # Make the request
        response = requests.post(url, headers=headers, json=payload)
        
        # Debug print
        print(f"[DEBUG] Response status code: {response.status_code}")
        
        if response.status_code == 200:
            results = response.json()
            
            # Debug print
            print(f"[DEBUG] Number of results: {len(results.get('results', []))}")
            
            # Process results to create context string
            context_str = ""
            raw_results = []
            
            for result in results.get("results", []):
                if columns:
                    result_data = {col: result.get(col, "") for col in columns}
                    raw_results.append(result_data)
                    context_str += f"\nDocument: {result_data.get('chunk', '')}\n"
                    context_str += f"URL: {result_data.get('file_url', '')}\n"
                    context_str += f"Path: {result_data.get('relative_path', '')}\n"
            
            return context_str, raw_results
            
        else:
            print(f"[ERROR] API request failed with status code: {response.status_code}")
            print(f"[ERROR] Response: {response.text}")
            return "", []
            
    except Exception as e:
        print(f"[ERROR] Exception occurred: {str(e)}")
        return "", []