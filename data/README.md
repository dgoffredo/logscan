Data
====
This directory contains an example HTTP access log used when developing
logscan.

I broke the input data up by remote host and isolated the timestamp of each
input line (distributed clocks means that the timestamps reported by the lines
do not belong to the same sequence).

[access.log](access.log) is the complete log as CSV.

[timestamps](timestamps) is a text file containing columns "input line number"
and "unix timestamp."

Each of the files whose name is an IP address are the events specific to that
remote host, as CSV.

Each of the files whose name matches the glob `*.timestamps` is a text file
containing the columns "input line number from complete log" and "unix
timestamp," but containing only those events specific to that remote host.
