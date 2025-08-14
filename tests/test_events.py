"""EventQueue tests"""

# 3rd party
import pytest

# local
from xthulu.events import EventData, EventQueue, EventQueues, put_global


@pytest.fixture(autouse=True)
def clear_queues():
    EventQueues.q.clear()
    yield
    EventQueues.q.clear()


def test_new_eventqueue_gets_added():
    """Spinning up a new EventQueue should append to the singleton."""

    # act
    q1 = EventQueue("1")

    # assert
    assert "1" in EventQueues.q
    assert EventQueues.q["1"] == q1


@pytest.mark.asyncio
async def test_put_global_count():
    """put_global should return an accurate count of deliveries."""

    # arrange
    EventQueue("1")
    EventQueue("2")

    # act
    count = await put_global(EventData("test", "test"))

    # assert
    assert count == 2


@pytest.mark.asyncio
async def test_put_global_exclude():
    """put_global should exclude specified EventQueue sids."""

    # arrange
    q1 = EventQueue("1")
    test_data = EventData("test", "test")

    # act
    await put_global(test_data, exclude={"1"})
    q1_events = q1.get("test")

    # assert
    assert len(q1_events) == 0


@pytest.mark.asyncio
async def test_put_global_exclude_count():
    """
    put_global should return an accurate count of deliveries when sids are
    excluded.
    """

    # arrange
    EventQueue("1")
    EventQueue("2")

    # act
    count = await put_global(EventData("test", "test"), exclude={"1"})

    # assert
    assert count == 1


@pytest.mark.asyncio
async def test_put_global_is_global():
    """put_global should add an event to all EventQueues."""

    # arrange
    q1 = EventQueue("1")
    q2 = EventQueue("2")

    # act
    await put_global(EventData("test", "test"))
    q1_events = q1.get("test")
    q2_events = q2.get("test")

    # assert
    assert len(q1_events) == len(q2_events)
    assert len(q1_events) == 1


@pytest.mark.asyncio
async def test_put_global_passes_data():
    """put_global should pass the EventData correctly."""

    # arrange
    q1 = EventQueue("1")
    test_data = EventData("test", "test")

    # act
    await put_global(test_data)
    q1_events = q1.get("test")
    ev = q1_events[0]

    # assert
    assert ev == test_data


def test_add_pushes_eventdata():
    """add should push EventData into the queue."""

    # arrange
    q1 = EventQueue("1")
    test_data = EventData("test", "test")

    # act
    q1.add(test_data)
    q1_events = q1.get()

    # assert
    assert q1_events[0] == test_data


def test_flush_all():
    """flush should clear the EventQueue if no event name is given."""

    # arrange
    q1 = EventQueue("1")
    q1.add(EventData("test", "test"))

    # act
    q1.flush()
    q1_events = q1.get("test")

    # assert
    assert len(q1_events) == 0


def test_flush_name():
    """flush should clear only specified items if name is given."""

    # arrange
    q1 = EventQueue("1")
    test_data = EventData("test", "test")
    q1.add(EventData("nope", "nope"))
    q1.add(test_data)

    # act
    q1.flush("nope")
    q1_events = q1.get()

    # assert
    assert len(q1_events) == 1
    assert q1_events[0] == test_data


def test_get_all_is_chronological():
    """
    get should return data in chronological order if no event name is given.
    """

    # arrange
    q1 = EventQueue("1")
    test_data = [
        EventData("one", "one"),
        EventData("two", "two"),
        EventData("three", "three"),
    ]

    for event in test_data:
        q1.add(event)

    # act
    q1_events = q1.get()

    # assert
    assert q1_events == test_data


def test_get_by_name_is_chronological():
    """
    get should return data in chronological order if event name is given.
    """

    # arrange
    q1 = EventQueue("1")
    test_data_one = [
        EventData("one", "one"),
        EventData("one", "two"),
        EventData("one", "three"),
    ]
    test_data_two = [
        EventData("two", "one"),
        EventData("two", "two"),
        EventData("two", "three"),
    ]
    test_data = test_data_one + test_data_two

    for event in test_data:
        q1.add(event)

    # act
    q1_events = q1.get("one")

    # assert
    assert q1_events == test_data_one


def test_get_by_name_returns_eventdata():
    """get should return specific EventData from the queue."""

    # arrange
    q1 = EventQueue("1")
    test_data = EventData("test", "test")
    q1.add(EventData("nope", "nope"))
    q1.add(test_data)

    # act
    q1_events = q1.get("test")

    # assert
    assert len(q1_events) == 1
    assert q1_events[0] == test_data
