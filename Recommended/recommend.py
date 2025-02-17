from GenerateIdeas.generate import *


class ExtraSpecifications(BaseModel):
    origDetails: PaperFormat
    specifications: str


def recommendAcceptButton(data,chat):
    sample_data = {
        "title": "This is the title",
        "Abstract": "This is the abstract",
        "Methodology recommended": "This is the recommended methodology",
        "Existing work": ["this is a list of existing works"]
    }
   
    return chat.recommend_ideas(data.model_dump())


def recommendSuggestionsButton(data,chat):
    sample_data = {
        1: {
            "title": "This is the paper title",
            "summary": "This is the summary",
            "drawbacks": ["defect1", "defect2", "defect3"],
            "opportunities": ["opportunity1", "opportunity2"],
            "related_works": {
                1: {
                    "title": "this is the title",
                    "summary": "this is the summary of the paper"
                },
                2: {
                    "title": "this is the title",
                    "summary": "this is the summary of the paper"
                }
            }
        },
        2: {
            "title": "This is the paper title",
            "summary": "This is the summary",
            "drawbacks": ["defect1", "defect2", "defect3"],
            "opportunities": ["opportunity1", "opportunity2"],
            "related_works": {
                1: {
                    "title": "this is the title",
                    "summary": "this is the summary of the paper"
                },
                2: {
                    "title": "this is the title",
                    "summary": "this is the summary of the paper"
                }
            }
        },
        3: {
            "title": "This is the paper title",
            "summary": "This is the summary",
            "drawbacks": ["defect1", "defect2", "defect3"],
            "opportunities": ["opportunity1", "opportunity2"],
            "related_works": {
                1: {
                    "title": "this is the title",
                    "summary": "this is the summary of the paper"
                },
                2: {
                    "title": "this is the title",
                    "summary": "this is the summary of the paper"
                }
            }
        }
    }
    print("Hello")
    #print(data.model_dump())
    #print(type(data.model_dump()))
    return chat.suggestion_improvement_idea_prompt(data.model_dump())
    #return data
    #return sample_data
