

## Updating data about MPs

Data about MPS is included. To get the latest data:

    pip install -r requirements.txt

    python ./get_mps_data.py

This will download data about all MPs from the [Members Names Information Services](http://data.parliament.uk/membersdataplatform/memberquery.aspx) using [mnis](https://github.com/olihawkins/mnis).

Useful bits of this will be saved into the file `public/data/mps.json`.

Then that will be used, alongside the prepared `public/data/uk.json` file,
to create the JSON file used by the chart, `public/data/ages.json`.

## UK Data

The data about UK population age bands, in `public/data/uk.json`, is based on mid-2016 figures from [this Office for National Statistics bulletin](https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationprojections/bulletins/nationalpopulationprojections/2016basedstatisticalbulletin).

Each band shows the number of people in the UK in that age band, in 1000s.
