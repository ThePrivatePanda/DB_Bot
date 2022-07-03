from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

class Vote(BaseModel):
    guild: int
    user: int
    type: str
    query: Optional[str] = None


app = FastAPI()


@app.post("/")
async def receieve_new_vote(info: Vote):
    print(info)
    return 200
