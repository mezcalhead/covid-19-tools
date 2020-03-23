# covid-19-tracker
COVID-19 Tracker at County Level

The goal of this project is to unify the reporting of the 52 'states' (counting DC and PR) into a structured unified view at the county level.  At a future time, zip code (ZCTA) could be addressed.

For speed and simplicity, the project will utilize an AirTable (www.airtable.com) repository that has been created and sponsored by <b>Culmen International</b> (www.culmen.com).  Registered developers will inject data into the airtable repository using the AirTable API, by contacting <b>mark.dumas@culmen.com</b>.

Public access will be via this link: <b>https://airtable.com/shrdzCswX95pa42qb</b>

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
    <td>Primary Key that is the Log ID (format described below)</td>
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


