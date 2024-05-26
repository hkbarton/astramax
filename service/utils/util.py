import uuid
import base64


def generate_unique_id():
    unique_id = uuid.uuid4()
    base64_id = base64.urlsafe_b64encode(unique_id.bytes)
    return base64_id.decode('utf-8').rstrip('=')


def generate_unique_uuid():
    unique_id = uuid.uuid4()
    return str(unique_id)
