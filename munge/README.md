<h2>Munge Purpose</h2>

Scripts for processing the JHU data to prepare for other forms of analysis.

<b>ts_merge.py</b> combines all the daily files in the JHU repo into one normalized file, but does not clean up the US county data that was originally tracked to adjust for the ADM3 format.  Output is <b>ts_merged.txt</b><br>

<b>ts_clean.py</b> cleans the ts_merged.csv file to fix early US county entries and then intertoplates US counties historically where gaps exist.  Output is <b>ts_cleaned.txt</b><br>

<b>cf_model.py</b> curve fitting utilities<br>

<b>analyze.py</b> applies curve-fitting utilities to figure out best fit, mean, etc and produces basic US county plots and interpolations<br>
