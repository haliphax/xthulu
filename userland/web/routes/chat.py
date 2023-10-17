"""Web chat"""

# typing
from typing import Annotated

# stdlib
from asyncio import sleep
import json

# 3rd party
from fastapi import Depends, Request
from sse_starlette.sse import EventSourceResponse

# api
from xthulu.models.user import User
from xthulu.resources import Resources
from xthulu.web.auth import login_user

# local
from ...scripts.chat import ChatMessage
from .. import api


@api.get("/chat/")
def chat(user: Annotated[User, Depends(login_user)], request: Request):
    async def generate():
        redis = Resources().cache
        pubsub = redis.pubsub()
        pubsub.subscribe("chat")
        redis.publish(
            "chat",
            json.dumps(
                ChatMessage(
                    user=None, message=f"{user.name} has joined"
                ).__dict__
            ),
        )

        try:
            while not await request.is_disconnected():
                message = pubsub.get_message(True)
                data: bytes

                if not message:
                    await sleep(0.1)
                    continue

                data = message["data"]
                yield data.decode("utf-8")
        finally:
            redis.publish(
                "chat",
                json.dumps(
                    ChatMessage(
                        user=None, message=f"{user.name} has left"
                    ).__dict__
                ),
            )
            pubsub.close()
            redis.close()

    return EventSourceResponse(generate())
