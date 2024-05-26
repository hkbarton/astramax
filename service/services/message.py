from models import Message
from utils import Database, generate_unique_id
from sqlalchemy import select, insert, update
from schemas import Message as MessageSchema


class MessageService:
    @staticmethod
    async def get_next_unprocessed_message(processor_id: str) -> Message | None:
        query = select(Message).where(
            Message.processed_by.is_(None)
        ).order_by(Message.created_at.desc())
        result = await Database.get_db().fetch_one(query)
        if result:
            message = Message(**result)
            # TODO transaction
            update_statement = update(Message).where(
                Message.id == message.id).values(processed_by=processor_id)
            await Database.get_db().execute(update_statement)
            message.processed_by = processor_id
            return message
        return None

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
