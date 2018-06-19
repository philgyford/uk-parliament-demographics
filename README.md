

Uses Python 3 to fetch data about MPs and Lords members from the [Members Names Information Services](http://data.parliament.uk/membersdataplatform/memberquery.aspx). That process is inspired by [mnis](https://github.com/olihawkins/mnis) (which only fetches data for the Commons).


## Updating data about members

Data about MPs and Lords members is included. To get the latest data:

    pip install -r requirements.txt

    python ./get_members_data.py

Useful bits of the fetched data will be saved into the files
`public/data/commons.json` and `public/data/lords.json`.

Then that will be used, alongside the prepared `public/data/uk.json` file,
to create the JSON file used by the chart, `public/data/ages.json`.


## UK Data

The data about UK population age bands, in `public/data/uk.json`, is based on
mid-2016 figures from [this Office for National Statistics bulletin](https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationprojections/bulletins/nationalpopulationprojections/2016basedstatisticalbulletin).

Each band shows the number of people in the UK in that age band, rounded to the nearest 1000.
