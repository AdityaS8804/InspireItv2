import json
import logging
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from LLM.new_prompts import DiscoveryEngineClient

class PaperFormat(BaseModel):
    title: str = Field(..., description="Title of the paper")
    Abstract: str = Field(..., description="Abstract of the paper")
    Methodology_recommended: str = Field(..., description="Recommended methodology")

class UserDetailsFormat(BaseModel):
    domains: List[str] = Field(..., min_items=1, description="List of domains")
    specifications: str = Field(..., min_length=1, description="Detailed specifications")

def generateSubmitButton(data: UserDetailsFormat) -> Dict[str, Any]:
    logger = logging.getLogger(__name__)
    logger.debug(f"Received data in generateSubmitButton: {data}")
    
    try:
        client = DiscoveryEngineClient()
        
        # Create a more structured search query
        query_parts = []
        for domain in data.domains:
            query_parts.append(f'"{domain}"')
        
        if data.specifications:
            query_parts.append(f'"{data.specifications}"')
            
        query = " AND ".join(query_parts)
        logger.debug(f"Constructed search query: {query}")
        
        results = client.search(query)
        logger.debug(f"Search results: {json.dumps(results, indent=2)}")
        
        if not results or "error" in results:
            logger.warning(f"Search failed or returned no results: {results}")
            return results
            
        formatted_response = {}
        documents = results.get("results", [])
        
        if not documents:
            logger.warning("No documents found in results")
            return {
                "message": "No results found",
                "results": []
            }
            
        for i, doc in enumerate(documents[:3], 1):
            document_data = doc.get("document", {})
            snippets = document_data.get("snippets", ["No summary available"])
            summary = snippets[0] if snippets else "No summary available"
            
            formatted_response[str(i)] = {
                "title": document_data.get("title", "No title"),
                "summary": summary,
                "drawbacks": [
                    "Further validation required",
                    "Implementation complexity",
                    "Resource requirements"
                ],
                "opportunities": [
                    "Innovation potential",
                    "Market applications",
                    "Research impact"
                ]
            }
            
        logger.debug(f"Formatted response: {json.dumps(formatted_response, indent=2)}")
        return formatted_response
        
    except Exception as e:
        logger.error(f"Error in generateSubmitButton: {str(e)}", exc_info=True)
        return {
            "error": str(e),
            "message": "An error occurred while processing your request"
        }

def generateButton() -> Dict[str, Any]:
    return {
        "fields": ["field1", "field2"],
        "specifications": "More details",
    }