# Notes

- sliding window is tricky
    - alernative: linear interpolation of concurrent events?
- one-second precision makes for a lot of "concurrent" events
    - millisecond/microsecond precision would help, even if it's just noise
- distributed clocks
    - when do I use the "received" time, and when do I use the "stamped" time?
        - does "received" time even mean anything? (e.g. post-facto analysis)
- alerts can flicker if request rates hover around the threshold
    - add hysteresis?
        - yes, in a production tool I would probably do this.
    - process in non-overlapping time buckets?
        - what if they become large?
- processing per event is (at worst) linear in window size
    - dedicated data structures could improve this, possibly even within SQL
        - e.g. improve to logarithmic using heaps and/or trees
    - manual profile-guided optimization could make this manageable
        - for example, a lot of time is spent in `min_max_unix_times`. That
          could be optimized with a couple of heaps (might be better, might not).
    - batching can improve throughput.  Right now we do all our processing _for each event_
        - you can reconcile low latency with high throughput by using a
          two-pronged batching strategy. See, for example, [my Go batcher][1].
- the idea of "everything is in a sqlite database" might not be the best design.
    - PROS:
        - let the SQL engine write your algorithms; you add indices or optimize
          queries as necessary (it will even analyze queries for you).
        - easy to express complex data transformations without any coding
          boilerplate.
        - maintainers are likely already familiar with SQL, as opposed to your
          application-specific data structure combination.
    - CONS:
        - when SQL is slow, it's hard to know why.
        - the "power" of SQL may allow costs to add up unnoticed
        - optimized though it is, it's probably "heavier" than dedicated data
          structures
        - some people hate working with SQL.
    - overall, I like it
- this program is too slow. It takes over a second on my computer to chew
  through the example log.
    - See notes about performance above.
    - if it's not an algorithmic complexity problem, then one way to trim
      time is to rewrite in a language that produces optimized native code,
      e.g. Go, C++, Rust.  It's almost always the data structures, though.

[1]: https://pkg.go.dev/github.com/dgoffredo/go-batch
