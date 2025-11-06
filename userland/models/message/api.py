"""Shared userland messages API"""

# stdlib
from typing import Sequence, Tuple

# 3rd party
from sqlmodel import and_, col, select

# api
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

    query = select(Message.id, Message.title)

    return (
        query
        if not tags or len(tags) == 0
        else query.select_from(Message)
        .join(MessageTags)
        .where(
            and_(
                MessageTags.message_id == Message.id,
                col(MessageTags.tag_name).in_(tags),
            )
        )
    )


async def get_latest_messages(
    tags: list[str] | None = None, limit=100
) -> Sequence[Tuple[int, str]]:
    """
    Get the latest messages (in descending order).

    Args:
        tags: A list of tags to filter by, if any
        limit: The number of messages to return

    Returns:
        A list of messages matching the provided criteria
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
) -> Sequence[Tuple[int, str]]:
    """
    Get messages newer than the provided ID (in ascending order).

    Args:
        id: The message ID used as an exclusive lower bound
        tags: A list of tags to filter by, if any
        limit: The number of messages to return

    Returns:
        A list of messages matching the provided criteria
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
) -> Sequence[Tuple[int, str]]:
    """
    Get messages older than the provided ID (in descending order).

    Args:
        id: The message ID used as an exclusive upper bound
        tags: A list of tags to filter by, if any
        limit: The number of messages to return

    Returns:
        A list of messages matching the provided criteria
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
