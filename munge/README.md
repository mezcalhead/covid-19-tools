<h2>Munge Purpose</h2>

Scripts for processing the JHU data to prepare for other forms of analysis.

<b>ts_merge.py</b> combines all the daily files in the JHU repo into one normalized file, but does not clean up the US data that was originally tracked.  Output is <b>ts_merged.csv</b><br>
<b>ts_clean.py</b> cleans the ts_merged.csv file to fix early US county entries and intertoplate historically.  Output is <b>ts_cleaned.csv</b><br>
