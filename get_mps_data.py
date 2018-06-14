import datetime
import json
import logging
import mnis

# Uses mnis to fetch data about all MPs and saves it to a file as JSON.

# Destination for our data:
JSON_FILEPATH = './public/data/mps.json'


logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def fetch_data():
    logger.info("Fetching data for all current MPs")

    mps = []

    data = mnis.getCommonsMembersOn(datetime.date.today())

    for row in data:
        person = {
            'memberId':         row['@Member_Id'],
            'gender':           row['Gender'],
            'name':             row['DisplayAs'],
            'partyId':          row['Party']['@Id'],
            'partyName':        row['Party']['#text'],
            # Will be set below:
            'dateOfBirth':      None,
            'constituencyId':   None,
            'constituencyName': None,
        }

        # Some don't have a date of birth listed.
        if '@xsi:nil' not in row['DateOfBirth'] or row['DateOfBirth']['@xsi:nil'] == 'false':
            person['dateOfBirth'] = row['DateOfBirth']

        # Sometimes there's only one constiuency (a dict), but usually it's a
        # list of them, only one being their 'current' constituency.
        if isinstance(row['Constituencies']['Constituency'], dict):
            constituency = row['Constituencies']['Constituency']
        else:
            for c in row['Constituencies']['Constituency']:
                # Go through all constituencies and find their current one.
                if '@xsi:nil' in c['EndDate'] and c['EndDate']['@xsi:nil'] == 'true':
                    constituency = c
                    break

        person['constituencyId'] = constituency['@Id']
        person['constituencyName'] = constituency['Name']

        mps.append(person)

    with open(JSON_FILEPATH, 'w') as f:
        json.dump({'members': mps}, f, indent=2, ensure_ascii=False)

    logger.info("Saved data for {} MPs".format(len(mps)))


if __name__ == "__main__":

    fetch_data()
