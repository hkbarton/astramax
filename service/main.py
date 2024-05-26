from fastapi import FastAPI
from services import MessageService
from schemas import Message as MessageSchema
from utils import Database
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    await Database.get_db().connect()
    yield
    await Database.get_db().disconnect()

app = FastAPI(lifespan=lifespan)


@app.get("/api/message")
async def get_last_unprocessed_message(by: str) -> MessageSchema:
    return MessageService.get_message_by_id(by)


@app.post("/api/message")
async def create_message(msg: MessageSchema) -> MessageSchema:
    created_msg = await MessageService.create_message(msg)
    return created_msg

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
