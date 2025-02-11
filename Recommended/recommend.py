from GenerateIdeas.generate import *


class ExtraSpecifications(BaseModel):
    origDetails: PaperFormat
    specifications: str


def recommendAcceptButton(data):
    sample_data = {
        "title": "This is the title",
        "Abstract": "This is the abstract",
        "Methodology recommended": "This is the recommended methodology",
        "Existing work": ["this is a list of existing works"]
    }
    return sample_data


def recommendSuggestionsButton(data):
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
    return sample_data
