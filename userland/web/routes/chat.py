"""Web chat"""

# typing
from typing import Annotated

# stdlib
from asyncio import sleep
import base64
from datetime import datetime
import json
from math import floor
from uuid import uuid4

# 3rd party
from fastapi import Depends, HTTPException, Request, status
from sse_starlette.sse import EventSourceResponse

# api
from xthulu.models.user import User
from xthulu.resources import Resources
from xthulu.web.auth import login_user

# local
from ...scripts.chat import ChatMessage, MAX_LENGTH
from ..schema.chat import ChatPost, ChatToken
from .. import api

TOKEN_EXPIRY = 30
"""Number of seconds for CSRF token expiration"""

redis = Resources().cache


def refresh_token(username: str) -> str:
    """
    Refresh a CSRF token. The token is persisted to redis cache.

    Args:
        username: The username to generate a token for.

    Returns:
        The CSRF token that was generated.
    """

    token = (
        base64.encodebytes(bytearray.fromhex(str(uuid4()).replace("-", "")))
        .decode("utf-8")
        .rstrip()
    )

    if not redis.setex(f"{username}.chat_csrf", TOKEN_EXPIRY, token):
        raise Exception(f"Error caching CSRF token for {username}")

    return token


@api.get("/chat/")
def chat(
    user: Annotated[User, Depends(login_user)], request: Request
) -> EventSourceResponse:
    """Server-sent events for chat EventSource."""

    async def generate():
        pubsub = redis.pubsub()
        pubsub.subscribe("chat")
        redis.publish(
            "chat",
            ChatMessage(
                user=None, message=f"{user.name} has joined"
            ).model_dump_json(),
        )
        token = refresh_token(user.name)
        then = datetime.utcnow()
        yield ChatToken(token=token).model_dump_json()

        try:
            while not await request.is_disconnected():
                now = datetime.utcnow()

                if (now - then).total_seconds() > floor(TOKEN_EXPIRY * 0.8):
                    token = refresh_token(user.name)
                    then = now
                    yield ChatToken(token=token).model_dump_json()

                message = pubsub.get_message(True)
                data: bytes

                if not message:
                    await sleep(0.1)
                    continue

                data = message["data"]
                yield data.decode("utf-8")
        finally:
            redis.delete(f"{user.name}.chat_csrf")
            redis.publish(
                "chat",
                ChatMessage(
                    user=None, message=f"{user.name} has left"
                ).model_dump_json(),
            )
            pubsub.close()

    return EventSourceResponse(generate())


@api.post("/chat/")
async def post_chat(
    message: ChatPost,
    user: Annotated[User, Depends(login_user)],
) -> None:
    """
    Post a chat message.

    Args:
        message: The message object being posted.
    """

    token_bytes: bytes = redis.get(f"{user.name}.chat_csrf")  # type: ignore
    token = token_bytes.decode("utf-8")

    if token is None or token != message.token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing or invalid CSRF token",
        )

    if len(message.message) > MAX_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Too long; message must be <= {MAX_LENGTH}",
        )

    redis.publish(
        "chat",
        json.dumps(
            ChatMessage(user=user.name, message=message.message).model_dump()
        ),
    )
