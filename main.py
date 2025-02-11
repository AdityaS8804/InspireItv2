from fastapi import FastAPI
from pydantic import BaseModel
from GenerateIdeas.generate import *
from Recommended.recommend import *


app = FastAPI()


@app.get("/")
async def root():
    return {"Status": "Works"}


@app.get("/generate")
async def generate():
    return generateButton()


@app.post("/generate/submit")
async def generateSubmit(userDetails: UserDetailsFormat):
    return generateSubmitButton()


@app.post("/recommend/suggested/")
async def recommendPaperChosen(paperChosen: PaperFormat):
    return recommendAcceptButton(paperChosen)
