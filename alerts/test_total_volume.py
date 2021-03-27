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
        # have executed the SQL query (we don't test that here).  However,
        # we've had three events in two minutes, which is much less than 1 per
        # second, and so the trigger status of the alert (False) has not
        # changed, so we do not yet expect a notice.
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
        self.assertEqual(notices[-1].unix_time, 120) # most recent event

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
        self.assertEqual(notices[-1].unix_time, 120) # most recent event

        # The average request rate is exactly equal to the threshold, so if the
        # next event occurs more than a second later, the rate will drop
        # below the threshold and we'll recover.
        handle_event(event_at(122))
        self.assertEqual(len(notices), 2)
        self.assertFalse(notices[-1].is_triggered)
        self.assertEqual(notices[-1].unix_time, 122) # most recent event


    def test_triggered_out_of_order(self):
        # Note that the threshold is now two requests per second (on average
        # over 120 seconds).
        notices, handle_event = self.setup_boilerplate(volume_threshold_per_second=2)

        handle_event(event_at(0))
        # No notice yet, there haven't been enough events.
        self.assertEqual(notices, [])

        # Now a burst of events the bring us up to the two minute window, but
        # still nowhere near the "two requests per second" threshold.
        # quite.
        for _ in range(119):
            handle_event(event_at(120))
        self.assertEqual(notices, [])

        # Create events "from the past" that retroactively bring us to the
        # brink of an alert.
        for _ in range(120):
            handle_event(event_at(60))
        self.assertEqual(notices, [])

        # Tip us over the edge, retroactively.
        handle_event(event_at(60))
        self.assertEqual(len(notices), 1)
        self.assertTrue(notices[-1].is_triggered)
        self.assertEqual(notices[-1].unix_time, 60) # event in the PAST


    def test_recovered_out_of_order(self):
        # This is a weird one.  Because of the way that the windowing works,
        # we can receive events "from the past" (lagged unix timestamps) that
        # cause the alert to _recover_.  This is because the introduction of the
        # past event might cause the window to "leave behind" some old events
        # that might have contributed to the alert triggering.

        notices, handle_event = self.setup_boilerplate(volume_threshold_per_second=1)

        # These oldest events are the ones that will be removed from the window
        # when the "late" event comes in.  It's their omission that will cause
        # the triggered alert to recover.
        # We use three events so that the average in the window just exceeds
        # one per second.
        for _ in range(3):
            handle_event(event_at(0))
        self.assertEqual(notices, [])

        for _ in range(118):
            handle_event(event_at(121))
        self.assertEqual(notices, [])

        # trigger
        handle_event(event_at(121))
        self.assertEqual(len(notices), 1)
        self.assertTrue(notices[-1].is_triggered)
        self.assertEqual(notices[-1].unix_time, 121) # most recent event

        # recover
        handle_event(event_at(1))
        self.assertEqual(len(notices), 2)
        self.assertFalse(notices[-1].is_triggered)
        self.assertEqual(notices[-1].unix_time, 1) # PAST event


def event_at(unix_time: float):
    return event.Event(
        remote_host='127.0.0.1',
        unix_time=unix_time,
        request='OPTIONS * HTTP/1.1',
        response_status=200,
        response_bytes=1024)
