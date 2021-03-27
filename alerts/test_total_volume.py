import event
import monitor
from alerts.total_volume import TotalVolume

import unittest


class TestTotalVolume(unittest.TestCase):

    def setup_boilerplate(self, volume_threshold_per_second):
        alert = TotalVolume(volume_threshold_per_second)
        alerts = {'total_volume': alert}
        stats = {}
        notices = []
        def on_notice(notice):
            notices.append(notice)
        handle_event = monitor.Monitor(alerts, stats, on_notice).handle_event

        # These tests assume the window size.
        self.assertEqual(alert.window_seconds(), 120)

        return notices, handle_event

    def test_triggered_in_order(self):
        notices, handle_event = self.setup_boilerplate(volume_threshold_per_second=1)

        handle_event(event_at(0))
        # No notice yet, there haven't been enough events.
        self.assertEqual(notices, [])

        handle_event(event_at(60))
        # No notice yet, there haven't been enough events.
        self.assertEqual(notices, [])

        handle_event(event_at(120))
        # The horizon is now greater than or equal to the window, so we will
        # have executed the SQL query. However, we've had three events in two
        # minutes, which is much less than 1 per second, and so the trigger
        # status of the alert (False) has not changed, so we do not yet expect
        # a notice.
        self.assertEqual(notices, [])

        # Now a burst of events the bring us to the cusp of an alert, but not
        # quite.
        for _ in range(117):
            handle_event(event_at(120))
        self.assertEqual(notices, [])

        # Tip us over the edge.
        handle_event(event_at(120))
        self.assertEqual(len(notices), 1)
        self.assertTrue(notices[-1].is_triggered)

    def test_recovered_in_order(self):
        notices, handle_event = self.setup_boilerplate(volume_threshold_per_second=1)

        handle_event(event_at(0))
        # No notice yet, there haven't been enough events.
        self.assertEqual(notices, [])

        # Now a burst of events the bring us to the cusp of an alert, but not
        # quite.
        for _ in range(119):
            handle_event(event_at(120))
        self.assertEqual(notices, [])

        # Tip us over the edge.
        handle_event(event_at(120))
        self.assertEqual(len(notices), 1)
        self.assertTrue(notices[-1].is_triggered)

        # The average request rate is exactly equal to the threshold, so if the
        # next event occurs more than a second later, the rate will drop
        # below the threshold and we'll recover.
        handle_event(event_at(122))
        self.assertEqual(len(notices), 2)
        self.assertFalse(notices[-1].is_triggered)


    def test_triggered_out_of_order(self):
        # Note that the threshold is now two requests per second (on average
        # over 120 seconds).
        notices, handle_event = self.setup_boilerplate(volume_threshold_per_second=2)

        pass # TODO


    def test_triggered_out_of_order(self):
        pass # TODO


def event_at(unix_time: float):
    return event.Event(
        remote_host='127.0.0.1',
        unix_time=unix_time,
        request='OPTIONS * HTTP/1.1',
        response_status=200,
        response_bytes=1024)


if __name__ == '__main__':
    unittest.main()
