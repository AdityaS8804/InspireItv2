from pydantic import BaseModel
class UserChat(BaseModel):
    message:str
def chatbotButton(data,chat):
    return chat.research_chat(data['message'])