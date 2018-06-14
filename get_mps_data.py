import datetime
import json
import logging
import mnis

# Uses mnis to fetch data about all MPs and saves it to a file as JSON.

# Location of our already-prepared JSON file about UK population age bands:
UK_FILEPATH = './public/data/uk.json'

# Destination for the JSON file with all MPs data:
MPS_FILEPATH = './public/data/mps.json'

# Destination for the JSON file created for use by D3.js:
AGES_FILEPATH = './public/data/ages.json'


logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def fetch_data():
    logger.info("Fetching data for all current MPs")

    mps = []

    data = mnis.getCommonsMembersOn(datetime.date.today())

    for row in data:
        person = {
            'memberId':         int(row['@Member_Id']),
            'gender':           row['Gender'],
            'name':             row['DisplayAs'],
            'partyId':          int(row['Party']['@Id']),
            'partyName':        row['Party']['#text'],
            # Will be set below:
            'dateOfBirth':      None,
            'constituencyId':   None,
            'constituencyName': None,
        }

        # Some don't have a date of birth listed.
        if '@xsi:nil' not in row['DateOfBirth'] or row['DateOfBirth']['@xsi:nil'] == 'false':
            # Only need the date part out of "1960-09-15T00:00:00":
            person['dateOfBirth'] = row['DateOfBirth'][:10]

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

        person['constituencyId'] = int(constituency['@Id'])
        person['constituencyName'] = constituency['Name']

        mps.append(person)

    with open(MPS_FILEPATH, 'w') as f:
        json.dump({'members': mps}, f, indent=2, ensure_ascii=False)

    logger.info("Saved data for {} MPs at {}".format(len(mps), MPS_FILEPATH))


def create_ages_file():
    """
    Open the JSON file of data about individual MPS created in fetchg_data().
    And the manually-created file of data about the whole UK population.

    Go through all the MPs and create counts for each party, and each age band.
    And overall age bands for all MPS.

    Then combine the UK data, parties data, and all MPs data, into a single
    JSON file, and save that.
    """

    logger.info("Creating file of age bands at {}".format(AGES_FILEPATH))

    # Empty dict we'll make copies of and populate with data:
    template = {
        '0-9': 0,
        '10-19': 0,
        '20-29': 0,
        '30-39': 0,
        '40-49': 0,
        '50-59': 0,
        '60-69': 0,
        '70-79': 0,
        '80-89': 0,
        '90-99': 0,
        '100-109': 0,
    }

    # Where we'll store data about MPs from all parties:
    all_mps = template.copy()

    # Where we'll store data about MPs from individual parties:
    # Based on the partyId's from the saved MP data.
    parties = {
        '4': {
            'name': 'Conservative',
            'bands': {},
        },
        '7': {
            'name': 'Democratic Unionist Party',
            'bands': {},
        },
        '15': {
            'name': 'Labour',
            'bands': {},
        },
        '17': {
            'name': 'Liberal Democrat',
            'bands': {},
        },
        '29': {
            'name': 'Scottish National Party',
            'bands': {},
        },

        # '22': {},     # Plaid Cymru
        # '8': {},    # Independent
        # '30': {},     # Sinn Féin
        # '44': {},     # Green
        # '47': {},   # Speaker
    }

    # Inflate the parties' bands dict swith empty bands:
    for id, dct in parties.items():
        parties[id]['bands'] = template.copy()


    today = datetime.date.today()

    # Create the data about all MPs and each party.
    with open(MPS_FILEPATH, 'r') as f:
        data = json.load(f)

        for m in data['members']:

            if m['dateOfBirth'] is None:
                # Can't calculate their age.
                continue

            party_id = str(m['partyId'])

            if party_id not in parties:
                # Skip a few parties with few MPS
                continue

            birthdate = datetime.datetime.strptime(
                                        m['dateOfBirth'], '%Y-%m-%d').date()
            age = today.year - birthdate.year - \
                ((today.month, today.day) < (birthdate.month, birthdate.day))

            if age < 10:
                band = '0-10'
            elif age < 20:
                band = '10-19'
            elif age < 30:
                band = '20-29'
            elif age < 40:
                band = '30-39'
            elif age < 50:
                band = '40-49'
            elif age < 60:
                band = '50-59'
            elif age < 70:
                band = '60-69'
            elif age < 80:
                band = '70-79'
            elif age < 90:
                band = '80-89'
            elif age < 100:
                band = '90-99'
            elif age < 110:
                band = '100-109'

            parties[party_id]['bands'][band] += 1
            all_mps[band] += 1

    # Also get the UK population data.
    with open(UK_FILEPATH, 'r') as f:
        uk_data = json.load(f)

    # Combine and save all of the above.
    ages_data = {
        'uk': uk_data['bands'],
        'mps': all_mps,
        'parties': parties,
    }

    with open(AGES_FILEPATH, 'w') as f:
        json.dump(ages_data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":

    fetch_data()

    create_ages_file()
