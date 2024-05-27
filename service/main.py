import asyncio
from fastapi import FastAPI, HTTPException
from services import MessageService
from schemas import Message as MessageSchema
from utils import Database, get_env, Env
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    await Database.get_db().connect()
    yield
    await Database.get_db().disconnect()

app = FastAPI(lifespan=lifespan)


@app.get("/api/message")
async def get_last_unprocessed_message(processor_id: str) -> MessageSchema:
    message = await MessageService.get_next_unprocessed_message(processor_id)
    if message is None:
        raise HTTPException(status_code=404, detail="Not exist")
    return message


@app.post("/api/message")
async def create_message(msg: MessageSchema) -> MessageSchema:
    return await MessageService.create_message(msg)


async def event_stream(processor_id: str):
    try:
        while True:
            next_message = await MessageService.get_next_unprocessed_message(processor_id)
            if next_message is not None:
                data = MessageSchema.from_orm(next_message).json()
                yield f"data: {data}\n\n"
            # await asyncio.sleep(0.5)
    except GeneratorExit:
        print("client disconnect")
        return


@app.get("/api/message-stream")
async def get_events(processor_id: str):
    return StreamingResponse(event_stream(processor_id), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0" if get_env() ==
                Env.PROD else "127.0.0.1", port=8000)
