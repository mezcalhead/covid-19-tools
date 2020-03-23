<h2>COVID-19 Tracker at County Level Project</h2>

<b>THIS PROJECT IS NOT LIVE, BUT LOOKING FOR COLLABORATORS!</b>

The goal of this project is to unify the reporting of the 52 'states' (counting DC and PR) into a structured unified and public view at the county level, as this is sorely needed during this crisis.  At a future time, zip code (ZCTA) could be addressed.<br>

For speed and simplicity, the project will utilize an <b>AirTable</b> (www.airtable.com) repository that has been created and sponsored by <b>Culmen International</b> (www.culmen.com).  Registered developers will inject data into the airtable repo using the AirTable API.  To register, please contact <b>mark.dumas@culmen.com</b> and your assignment can be coordinated and your AirTable API key granted.<br>    

Public access will be via this link: <b>https://airtable.com/shrdzCswX95pa42qb</b><br>

Developers are welcome to add publishing and visualization scripts.  The primary language is requested to be Python v3.<br>

<h2>Lead Collaborators (by State)</h2>

<table>
  <tr>
    <th>State FIPS</th>
    <th>State</th>
    <th>Collaborator GitHub Handle</th>
    <th>Collaborator Email</th>
  </tr>
</table>

<h2>Primary Table: 'Log'</h2>

The format of the primary table will be:

<table>
  <tr>
    <th>Field Name</th>
    <th>Type</th>
    <th>Description</th>
  </tr>
  <tr>
    <td>LID</td>
    <td>String</td>
    <td>Primary Key that is the Log ID (<i>format described <a href='https://github.com/mezcalhead/covid-19-tracker/blob/master/README.md#primary-key-lid'>below</a></i>)</td>
  </tr>
  <tr>
    <td>Date</td>
    <td>Date</td>
    <td>m/d/YYYY format representing the date of the statistic (e.g. '1/1/2020')</td>
  </tr>
  <tr>
    <td>State</td>
    <td>String</td>
    <td>The State name (e.g. 'Alabama')</td>
  </tr>
  <tr>
    <td>County</td>
    <td>String</td>
    <td>The County name (e.g. 'Autauga County')</td>
  </tr>
  <tr>
    <td>Cases</td>
    <td>Integer</td>
    <td>The # of confirmed open cases</td>
  </tr>
  <tr>
    <td>Recovered</td>
    <td>Integer</td>
    <td>The # of confirmed recovered cases</td>
  </tr>
  <tr>
    <td>Deaths</td>
    <td>Integer</td>
    <td>The # of confirmed deaths</td>
  </tr>
  <tr>
    <td>Contributor</td>
    <td>String</td>
    <td>The registered AirTable contributor (e.g. 'John Doe')</td>
  </tr>
  <tr>
    <td>Source Name</td>
    <td>String</td>
    <td>The source name (e.g. 'VA Dept of Health')</td>
  </tr>
  <tr>
    <td>SID</td>
    <td>Integer</td>
    <td>Foreign Key to the Sources table representing a Source ID</td>
  </tr>
  <tr>
    <td>CID</td>
    <td>String</td>
    <td>Foreign Key to the County table representing a County ID (format is [State FIPS] + '_' + [County Fips], e.g. '01_001')</td>
  </tr>
  <tr>
    <td>Notes</td>
    <td>Text</td>
    <td>Additional Notes about the Entry</td>
  </tr>
</table>

2 AirTable views are:<br>
COVID-19 Cases By Date and Location - public URL - note it has hidden fields that can be unhidden by the public<br>
COVID-19 Cases By Date and Location (Full) - this is the full view without hidden fields enabled<br>

<h2>Primary Key: 'LID'</h2>

The LID is of the format <pre>'YYYY-MM-DD_[State FIPS]_[County FIPS]_[Source ID]'</pre> (e.g. '2020-01-01_27_005_1')<br>
This means that there can be multiple sources for any given day, but only one entry for any given day for state/county/source.<br>
This integrity is by design.

