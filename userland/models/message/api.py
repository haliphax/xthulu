"""Shared userland messages API"""

# 3rd party
from sqlalchemy.orm import Query

# api
from xthulu.resources import Resources

# local
from . import Message
from .message_tags import MessageTags


def get_messages_query(tags: list[str] | None = None) -> Query:
    """
    Query for pulling messages, optionally filtered by tag(s).

    Args:
        tags: A list of tags to filter by (if any)

    Returns:
        A query object
    """

    db = Resources().db
    select = Message.select("id", "title")

    return (
        select
        if not tags or len(tags) == 0
        else select.select_from(
            Message.join(
                MessageTags,
                db.and_(
                    MessageTags.message_id == Message.id,
                    MessageTags.tag_name.in_(tags),
                ),
            )
        )
    )


async def get_latest_messages(tags: list[str] | None = None, limit=100) -> dict:
    """
    Get the latest messages (in descending order).

    Args:
        tags: A list of tags to filter by, if any
        limit: The number of messages to return

    Returns:
        A list of messages matching the provided criteria
    """

    return (
        await get_messages_query(tags)
        .order_by(Message.id.desc())
        .limit(limit)  # type: ignore
        .gino.all()
    )


async def get_newer_messages(
    id: int, tags: list[str] | None = None, limit=100
) -> dict:
    """
    Get messages newer than the provided ID (in ascending order).

    Args:
        id: The message ID used as an exclusive lower bound
        tags: A list of tags to filter by, if any
        limit: The number of messages to return

    Returns:
        A list of messages matching the provided criteria
    """

    return (
        await get_messages_query(tags)
        .where(Message.id > id)  # type: ignore
        .order_by(Message.id.asc())
        .limit(limit)
        .gino.all()
    )


async def get_older_messages(
    id: int, tags: list[str] | None = None, limit=100
) -> dict:
    """
    Get messages older than the provided ID (in descending order).

    Args:
        id: The message ID used as an exclusive upper bound
        tags: A list of tags to filter by, if any
        limit: The number of messages to return

    Returns:
        A list of messages matching the provided criteria
    """

    return (
        await get_messages_query(tags)
        .where(Message.id < id)  # type: ignore
        .order_by(Message.id.desc())
        .limit(limit)
        .gino.all()
    )
