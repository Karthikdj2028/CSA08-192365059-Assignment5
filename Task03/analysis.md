# A3 – Analysis and visualisation design

## Chart choices

| Board question | Chart | Reason |
|---|---|---|
| PM2.5 trend over a month | Line chart | Date is ordered; the line shows rises, falls and repeated patterns. |
| Compare stations | Bar chart | Station names are categories; bar height compares their mean PM2.5. |
| Temperature vs PM2.5 | Scatter plot | Each point is one paired observation; a pattern may show correlation. |
| Hours with worst air | Bar chart by hour or box plot | Mean PM2.5 by hour ranks the worst time; box plots show spread and outliers. |

All charts should have a clear title, x/y labels, units and a legend when multiple stations appear. A chart should not hide missing readings.

## Daily summary table

Columns: station, day, PM2.5 minimum, PM2.5 maximum, PM2.5 mean and valid reading count. It is produced by grouping readings by station and day, then applying MIN, MAX, AVG and COUNT. SQL GROUP BY is suitable when the readings already reside in SQLite.

## Alternative: Python loops

A loop reads n rows and updates a dictionary keyed by (station, day), storing sum, minimum, maximum and count. This is O(n) time and O(g) space, where g is the number of station/day groups. SQL GROUP BY also scans n rows, O(n) without an index, and stores grouping state in the database engine. Python keeps the group dictionary in application memory. SQL avoids transferring every record to Python and is convenient when the database is already the source.
