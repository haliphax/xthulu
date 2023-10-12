"""EventQueue tests"""

# stdlib
from unittest.async_case import IsolatedAsyncioTestCase

# local
from xthulu.events import EventData, EventQueue, EventQueues, put_global


class TestEventQueues(IsolatedAsyncioTestCase):

    """EventQueues tests"""

    def setUp(self):
        EventQueues.q.clear()

    def tearDown(self):
        EventQueues.q.clear()

    def test_new_eventqueue_gets_added(self):
        """Spinning up a new EventQueue should append to the singleton."""

        # act
        q1 = EventQueue("1")

        # assert
        self.assertIn("1", EventQueues.q)
        self.assertEqual(EventQueues.q["1"], q1)

    async def test_put_global_count(self):
        """put_global should return an accurate count of deliveries."""

        # arrange
        EventQueue("1")
        EventQueue("2")

        # act
        count = await put_global(EventData("test", "test"))

        # assert
        self.assertEqual(count, 2)

    async def test_put_global_exclude(self):
        """put_global should exclude specified EventQueue sids."""

        # arrange
        q1 = EventQueue("1")
        test_data = EventData("test", "test")

        # act
        await put_global(test_data, exclude={"1"})
        q1_events = q1.get("test")

        # assert
        self.assertEqual(len(q1_events), 0)

    async def test_put_global_exclude_count(self):
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
        self.assertEqual(count, 1)

    async def test_put_global_is_global(self):
        """put_global should add an event to all EventQueues."""

        # arrange
        q1 = EventQueue("1")
        q2 = EventQueue("2")

        # act
        await put_global(EventData("test", "test"))
        q1_events = q1.get("test")
        q2_events = q2.get("test")

        # assert
        self.assertCountEqual(q1_events, q2_events)
        self.assertEqual(len(q1_events), 1)

    async def test_put_global_passes_data(self):
        """put_global should pass the EventData correctly."""

        # arrange
        q1 = EventQueue("1")
        test_data = EventData("test", "test")

        # act
        await put_global(test_data)
        q1_events = q1.get("test")
        ev = q1_events[0]

        # assert
        self.assertEqual(ev, test_data)


class TestEventQueue(IsolatedAsyncioTestCase):

    """EventQueue tests"""

    def setUp(self):
        EventQueues.q.clear()

    def tearDown(self):
        EventQueues.q.clear()

    def test_add_pushes_eventdata(self):
        """add should push EventData into the queue."""

        # arrange
        q1 = EventQueue("1")
        test_data = EventData("test", "test")

        # act
        q1.add(test_data)
        q1_events = q1.get()

        # assert
        self.assertEqual(q1_events[0], test_data)

    def test_flush_all(self):
        """flush should clear the EventQueue if no event name is given."""

        # arrange
        q1 = EventQueue("1")
        q1.add(EventData("test", "test"))

        # act
        q1.flush()
        q1_events = q1.get("test")

        # assert
        self.assertEqual(len(q1_events), 0)

    def test_flush_name(self):
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
        self.assertEqual(len(q1_events), 1)
        self.assertEqual(q1_events[0], test_data)

    def test_get_by_name_returns_eventdata(self):
        """get should return specific EventData from the queue."""

        # arrange
        q1 = EventQueue("1")
        test_data = EventData("test", "test")

        # act
        q1.add(EventData("nope", "nope"))
        q1.add(test_data)
        q1_events = q1.get("test")

        # assert
        self.assertEqual(len(q1_events), 1)
        self.assertEqual(q1_events[0], test_data)
