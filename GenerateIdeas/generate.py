from pydantic import BaseModel


class PaperFormat(BaseModel):
    title: str
    summary: str
    drawbacks: list
    opportunities: list


class UserDetailsFormat(BaseModel):
    domains: list
    specifications: str


def generateButton():
    sample_data = {
        "fields": [
            "field1", "field2"
        ],
        "specifications": "More details",
    }
    return sample_data


def generateSubmitButton(data):
    sample_data = {
        1: {
            "title": "This is the paper title",
            "summary": "This is the summary",
            "drawbacks": ["defect1", "defect2", "defect3"],
            "opportunities": ["opportunity1", "opportunity2"],
        },
        2: {
            "title": "This is the paper title",
            "summary": "This is the summary",
            "drawbacks": ["defect1", "defect2", "defect3"],
            "opportunities": ["opportunity1", "opportunity2"],
        },
        3: {
            "title": "This is the paper title",
            "summary": "This is the summary",
            "drawbacks": ["defect1", "defect2", "defect3"],
            "opportunities": ["opportunity1", "opportunity2"],
        }
    }
    return sample_data
