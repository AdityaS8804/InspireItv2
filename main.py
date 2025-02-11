<<<<<<< Updated upstream
from fastapi import FastAPI
=======
from fastapi import FastAPI, HTTPException
>>>>>>> Stashed changes
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from GenerateIdeas.generate import *
from Recommended.recommend import *
from typing import Dict, Any


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.get("/generate")
async def generate() -> Dict[str, Any]:
    return generateButton()

@app.post("/generate/submit")
async def generateSubmit(userDetails: UserDetailsFormat) -> Dict[str, Any]:
    print(f"[DEBUG] Received request with user details: {userDetails}")
    try:
        result = generateSubmitButton(userDetails)
        if isinstance(result, dict):
            return result
        else:
            # If result is not a dict, convert it to one
            return {"result": result}
    except Exception as e:
        print(f"[ERROR] Failed to generate submission: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/recommend/suggested/")
async def recommendPaperChosen(paperChosen: PaperFormat) -> Dict[str, Any]:
    print(f"[DEBUG] Received paper: {paperChosen}")
    try:
        result = recommendAcceptButton(paperChosen)
        if isinstance(result, dict):
            return result
        else:
            # If result is not a dict, convert it to one
            return {"result": result}
    except Exception as e:
        print(f"[ERROR] Failed to generate recommendation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))