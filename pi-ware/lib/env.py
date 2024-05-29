import os
from dotenv import Dotenv
from enum import Enum


class Env(Enum):
    DEV = "dev"
    PROD = "prod"


def get_env() -> Env:
    for e in Env:
        if e.value == env:
            return e
    return Env.DEV


def get_var(key):
    return dotenv[key]


env = os.environ.get("ENV")
# local dev only
if not env:
    env = "dev"
    env_path = os.path.abspath(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "../../deployment/dev/.env"
    ))
dotenv = Dotenv(env_path)
# for prod or other envoriment
# environment variables are set through docker compose file
