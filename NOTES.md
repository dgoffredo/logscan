"... _on average_ over the last X seconds"

We want to get the greatest timestamp less than or equal to (max - X), count
the metric for those events, and then scale the value based on the time period.

There are guaranteed to be events at least as old as (max - X).  The program
will not invoke an alert otherwise.

For example,

time    message
3       foo
4       bar
4       baz
7       fibsh
7       l'egg
8       naarrrgghh
8       murph

(max) is 8. If X were 3, then (max - X) is 5. We pick the "baz" event at
time=4 as the horizon. Say our alert is just counting events in the window.
There's a total of 5 events in that window, but we scale down by X / (8 - 4)
= 3 / 4. So, rather can considering there to have been 5 events, we consider
there to have been (3 / 4)*5 = 3.75 events.
