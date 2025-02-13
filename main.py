from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from GenerateIdeas.generate import *
from Recommended.recommend import *
from LLMs.prompts import *
chat = MistralChat()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"Status": "Works"}


@app.get("/generate/")
async def generate():
    return generateButton()


@app.post("/generate/submit/")
async def generateSubmit(userDetails: UserDetailsFormat):
    return generateSubmitButton(dict(userDetails), chat)


@app.post("/generate/submit/extra-suggestions/")
async def generateWithSuggestions(userDetails: ExtraSpecifications):
    return recommendSuggestionsButton(userDetails,chat)


@app.post("/recommend/suggested/")
async def recommendPaperChosen(paperChosen: PaperFormat):
    return recommendAcceptButton(paperChosen,chat)
