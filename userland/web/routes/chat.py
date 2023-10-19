"""Web chat"""

# typing
from typing import Annotated

# stdlib
from asyncio import sleep
import json

# 3rd party
from fastapi import Depends, HTTPException, Request, status
from sse_starlette.sse import EventSourceResponse

# api
from xthulu.models.user import User
from xthulu.resources import Resources
from xthulu.web.auth import login_user

# local
from ...scripts.chat import ChatMessage, MAX_LENGTH
from ..schema.chat import ChatPost
from .. import api

redis = Resources().cache


@api.get("/chat/")
def chat(
    user: Annotated[User, Depends(login_user)], request: Request
) -> EventSourceResponse:
    async def generate():
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

    return EventSourceResponse(generate())


@api.post("/chat/")
async def post_chat(
    message: ChatPost,
    user: Annotated[User, Depends(login_user)],
) -> None:
    if len(message.message) > MAX_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Too long; message must be <= {MAX_LENGTH}",
        )

    redis.publish(
        "chat",
        json.dumps(
            ChatMessage(user=user.name, message=message.message).__dict__
        ),
    )
