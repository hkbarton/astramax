from models import Message
from utils import Database, generate_unique_id
from sqlalchemy import select, insert
from schemas import Message as MessageSchema


class MessageService:
    @staticmethod
    async def get_message_by_id(msg_id: str) -> Message | None:
        query = select(Message).where(
            Message.id == msg_id
        )
        result = await Database.get_db().fetch_one(query)
        if result:
            return Message(**result)
        return None

    @staticmethod
    async def create_message(msg: MessageSchema) -> Message:
        message_id = generate_unique_id()
        insert_statement = insert(Message).values(
            id=message_id, payload=msg.payload)
        await Database.get_db().execute(insert_statement)
        return await MessageService.get_message_by_id(message_id)
