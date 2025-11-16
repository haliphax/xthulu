"""Shared userland messages API"""

# stdlib
from typing import Sequence, Tuple

# 3rd party
from sqlmodel import col, select

# api
from xthulu.models import User
from xthulu.resources import db_session

# local
from . import Message
from .message_tags import MessageTags


def get_messages_query(tags: list[str] | None = None):
    """
    Query for pulling messages, optionally filtered by tag(s).

    Args:
        tags: A list of tags to filter by (if any)

    Returns:
        A query object
    """

    query = (
        select(
            Message.id,
            Message.title,
            User.name,
        )
        .select_from(Message)
        .join(MessageTags)
        .where(
            MessageTags.message_id == Message.id,
            Message.author_id == User.id,
        )
    )

    if tags:
        query = query.where(col(MessageTags.tag_name).in_(tags))

    return query.group_by(
        col(Message.id),
        col(Message.title),
        col(User.name),
    )


async def get_latest_messages(
    tags: list[str] | None = None, limit=100
) -> Sequence[Tuple[int, str, str]]:
    """
    Get the latest messages (in descending order).

    Args:
        tags: A list of tags to filter by, if any
        limit: The number of messages to return

    Returns:
        A list of (id, title, author) matching the provided criteria
    """

    async with db_session() as db:
        return (
            await db.exec(
                get_messages_query(tags)
                .order_by(col(Message.id).desc())
                .limit(limit)
            )
        ).all()  # type: ignore


async def get_newer_messages(
    id: int, tags: list[str] | None = None, limit=100
) -> Sequence[Tuple[int, str, str]]:
    """
    Get messages newer than the provided ID (in ascending order).

    Args:
        id: The message ID used as an exclusive lower bound
        tags: A list of tags to filter by, if any
        limit: The number of messages to return

    Returns:
        A list of (id, title, author) matching the provided criteria
    """

    async with db_session() as db:
        return (
            await db.exec(
                get_messages_query(tags)
                .where(Message.id > id)  # type: ignore
                .order_by(col(Message.id).asc())
                .limit(limit)
            )
        ).all()  # type: ignore


async def get_older_messages(
    id: int, tags: list[str] | None = None, limit=100
) -> Sequence[Tuple[int, str, str]]:
    """
    Get messages older than the provided ID (in descending order).

    Args:
        id: The message ID used as an exclusive upper bound
        tags: A list of tags to filter by, if any
        limit: The number of messages to return

    Returns:
        A list of (id, title, author) matching the provided criteria
    """

    async with db_session() as db:
        return (
            await db.exec(
                get_messages_query(tags)
                .where(Message.id < id)  # type: ignore
                .order_by(col(Message.id).desc())
                .limit(limit)
            )
        ).all()
