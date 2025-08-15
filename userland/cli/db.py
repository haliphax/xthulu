"""Command line database module"""

# stdlib
from asyncio import get_event_loop

# 3rd party
from click import echo, group, option
from sqlmodel import SQLModel

# api
from xthulu.resources import get_session, Resources


@group("db")
def cli():
    """Database commands"""


@cli.command()
@option(
    "-s/--seed",
    "seed_data",
    default=False,
    flag_value=True,
    help="Seed the database with default data.",
)
def create(seed_data=False):
    """Create database tables."""

    async def f():
        from .. import models  # noqa: F401
        from xthulu import models as server_models  # noqa: F401

        async with Resources().db.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

    get_event_loop().run_until_complete(f())

    if seed_data:
        _seed()


def _seed():
    from ..models import Message, MessageTag, MessageTags

    async def f():
        echo("Posting initial messages")

        async with get_session() as db:
            tags = (
                MessageTag(name="demo"),
                MessageTag(name="introduction"),
            )

            for tag in tags:
                db.add(tag)
                await db.commit()

            for i in range(100):
                message = Message(
                    author_id=1,
                    title=f"Hello, world! #{i}",
                    content=(
                        "# Hello\n\nHello, world! ✌️\n\n"
                        "## Demo\n\nThis is a demonstration message.\n\n"
                    )
                    * 20,
                )
                db.add(message)
                await db.commit()

                for tag in tags:
                    await db.refresh(message)
                    await db.refresh(tag)
                    db.add(
                        MessageTags(
                            message_id=message.id,  # type: ignore
                            tag_name=tag.name,  # type: ignore
                        )
                    )
                    await db.commit()

    get_event_loop().run_until_complete(f())


@cli.command()
def seed():
    """Initialize database with seed data."""

    _seed()
