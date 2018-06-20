import datetime
import json
import logging
import requests


JSON_DIR = './public/data'

FILEPATHS = {
    # Location of our already-prepared JSON file about UK population age bands:
    'uk':       '{}/uk.json'.format(JSON_DIR),
    # Files we'll save fetched data about individual Commons/Lords members:
    'commons':  '{}/commons.json'.format(JSON_DIR),
    'lords':    '{}/lords.json'.format(JSON_DIR),
    # Destination for the JSON file created for use by D3.js:
    'chart':     '{}/chart.json'.format(JSON_DIR),
}


logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def fetch_commons_data():
    logger.info("Fetching data for all current MPs")

    mps = []

    data = fetch_members_from_api(datetime.date.today(), 'commons')

    for row in data:
        person = make_member_from_raw_data(row, 'commons')
        mps.append(person)

    with open(FILEPATHS['commons'], 'w') as f:
        json.dump({'members': mps}, f, indent=2, ensure_ascii=False)

    logger.info("Saved data for {} MPs at {}".format(len(mps), FILEPATHS['commons']))


def fetch_lords_data():
    """
    """
    logger.info("Fetching data for all current Lords members")

    lords = []

    data = fetch_members_from_api(datetime.date.today(), 'lords')

    for row in data:
        person = make_member_from_raw_data(row, 'lords')
        lords.append(person)

    with open(FILEPATHS['lords'], 'w') as f:
        json.dump({'members': lords}, f, indent=2, ensure_ascii=False)

    logger.info("Saved data for {} Lords members at {}".format(len(lords), FILEPATHS['lords']))



def fetch_members_from_api(date, house):
    """
    This is pretty much replicating what mnis's getCommonsMembersOn() does,
    but for Lords, and only fetching bits of data that we need.

    date is the date on which we want to get the members for (probably today).
    house is either 'commons' or 'lords'
    """

    s = '{0}-{1}-{2}'.format(date.year, date.month, date.day)
    e = '{0}-{1}-{2}'.format(date.year, date.month, date.day)
    urlParameters = '{0}memberbetween={1}and{2}'.format(house, s, e)

    outputParameters = ['Parties', 'HouseMemberships']

    if house == 'commons':
        outputParameters.append('Constituencies')

    url = 'http://data.parliament.uk/membersdataplatform/services/' \
		'mnis/members/query/House={0}|Membership=all|{1}/{2}' \
		.format(house, urlParameters, '|'.join(outputParameters))

    headers = {'content-type': 'application/json'}
    response = requests.get(url, headers=headers)

    # Handle byte order marker
    response.encoding='utf-8-sig'

    members = response.json()

    members = members['Members']['Member']

    return members


def make_member_from_raw_data(data, house):
    """
    data is a single 'Member' from the data returned by mnis.
    house is either 'commons' or 'lords'.
    """
    person = {
        'memberId':         int(data['@Member_Id']),
        'gender':           data['Gender'],
        'name':             data['DisplayAs'],
    }

    if data['Party']:
        person['partyId'] = int(data['Party']['@Id'])
        person['partyName'] = data['Party']['#text']
    else:
        person['partyId'] = None
        person['partyName'] = ''


    # Some don't have a date of birth listed.
    if '@xsi:nil' not in data['DateOfBirth'] or data['DateOfBirth']['@xsi:nil'] == 'false':
        # Only need the date part out of "1960-09-15T00:00:00":
        person['dateOfBirth'] = data['DateOfBirth'][:10]
    else:
        person['dateOfBirth'] = None

    if house == 'commons':
        # Sometimes there's only one constiuency (a dict), but usually it's a
        # list of them, only one being their 'current' constituency.
        if isinstance(data['Constituencies']['Constituency'], dict):
            constituency = data['Constituencies']['Constituency']
        else:
            for c in data['Constituencies']['Constituency']:
                # Go through all constituencies and find their current one.
                if '@xsi:nil' in c['EndDate'] and c['EndDate']['@xsi:nil'] == 'true':
                    constituency = c
                    break

        person['constituencyId'] = int(constituency['@Id'])
        person['constituencyName'] = constituency['Name']

    return person


def create_chart_file():
    """
    Open the JSON files of data about individual members created in fetch_data().
    And the manually-created file of data about the whole UK population.

    Go through all members and create counts for each party, and each age band.
    And overall age bands for all Commons and Lords members.

    Then combine the UK data, parties data, and all members' data, into a single
    JSON file, and save that.
    """

    logger.info("Creating file of age bands at {}".format(FILEPATHS['chart']))

    bands_template = get_bands_template()

    # Where we'll store data about ages for members in all parties:
    all_members = {
        'commons': bands_template.copy(),
        'lords': bands_template.copy(),
    }

    # Where we'll store data about ages for members in individual parties:
    parties = {
        'commons': get_parties('commons'),
        'lords': get_parties('lords'),
    }

    # Where we'll store data about MPs from individual parties:

    today = datetime.date.today()

    bands = get_bands()

    for house in ['commons', 'lords',]:
        # Create the data about all members and each party.
        with open(FILEPATHS[house], 'r') as f:
            data = json.load(f)

            for m in data['members']:

                if m['dateOfBirth'] is None:
                    # Can't calculate their age.
                    continue

                party_id = str(m['partyId'])

                if party_id not in parties[house]:
                    # We skip a few parties with few members
                    continue

                birthdate = datetime.datetime.strptime(
                                            m['dateOfBirth'], '%Y-%m-%d').date()
                age = today.year - birthdate.year - \
                    ((today.month, today.day) < (birthdate.month, birthdate.day))

                band = None

                # Find which band, e.g. ages 20-29, that this age falls in.
                for lower_upper in bands:
                    if age >= lower_upper[0] and age <= lower_upper[1]:
                        band = '{}-{}'.format(lower_upper[0], lower_upper[1])
                        break

                if band is not None:
                    parties[house][party_id]['bands'][band] += 1
                    all_members[house][band] += 1

    # Also get the UK population data.
    with open(FILEPATHS['uk'], 'r') as f:
        uk_data = json.load(f)

    # Convert our dicts of dicts into lists of dicts:
    commons = [{'id': k, **v} for k,v in parties['commons'].items()]
    lords = [{'id': k, **v} for k,v in parties['lords'].items()]

    # Prepend the data for ALL members:
    commons.insert(0, {
        'id': 'all',
        'name': 'All MPs',
        'ages': all_members['commons'],
    })
    lords.insert(0, {
        'id': 'all',
        'name': 'All members',
        'bages': all_members['lords'],
    })

    # Combine and save all of the above.
    ages_data = {
        'uk': {
            'name': 'UK adult population',
            'ages': uk_data['bands'],
        },
        'commons': commons,
        'lords': lords,
    }

    with open(FILEPATHS['chart'], 'w') as f:
        json.dump(ages_data, f, indent=2, ensure_ascii=False)


def get_parties(house):
    """
    Return a dict of all the parties for this house that we want to generate
    separate age breakdowns for.

    The dict will be something like:

    {
        '4': {
            'name': Conservative',
            'bands': {
                '0-9': 0,
                '10-19': 0,
                ...
            }
        },
        ...
    }

    We'll ignore parties that have only a few members, because they're such a
    small sample.

    The keys in the returned dit are based on the partyId's in the API data.

    house is 'commons' or 'lords'
    """
    if house == 'commons':
        parties = {
            '4':  { 'name': 'Conservative', },
            '7':  { 'name': 'DUP', },
            '15': { 'name': 'Labour', },
            '17': { 'name': 'Liberal Democrat', },
            '29': { 'name': 'SNP', },

            # '8':  { 'name': 'Independent', },
            # '44': { 'name': 'Green Party', },
            # '22': { 'name': 'Plaid Cymru', },
            # '30': { 'name': 'Sinn Féin', },
            # '47': { 'name': 'Speaker', },
        }
    else:
        parties = {
            '3':  { 'name': 'Bishops', },
            '4':  { 'name': 'Conservative', },
            '6':  { 'name': 'Crossbench', },
            '15': { 'name': 'Labour', },
            '17': { 'name': 'Liberal Democrat', },
            '49': { 'name': 'Non-affiliated', },

            # '7':  { 'name': 'Democratic Unionist Party', },
            # '10': { 'name': 'Independent Labour', },
            # '22': { 'name': 'Plaid Cymru', },
            # '35': { 'name': 'UK Independence Party', },
            # '38': { 'name': 'Ulster Unionist Party', },
            # '44': { 'name': 'Green Party', },
            # '52': { 'name': 'Independent Ulster Unionist', },
            # '53': { 'name': 'Independent Social Democrat', },
            # '283': { 'name': 'Lord Speaker', },
        }

    bands_template = get_bands_template()

    # Inflate the parties' bands dict swith empty bands:
    for id, dct in parties.items():
        parties[id]['bands'] = bands_template.copy()

    return parties


def get_bands_template():
    """
    Returns an empty dict we'll make copies of and populate with data:

    {
        '0-9': 0,
        '10-19': 0,
        '20-29': 0,
        ...
    }
    """
    template = {}

    bands = get_bands()

    for band in bands:
        key = '{}-{}'.format(band[0], band[1])
        template[key] = 0

    return template


def get_bands():
    """
    Returns a list of lists.
    Each inner list has two ints, the lower and upper range of an age band.

    e.g. if bands_lower = [0, 10, 20, 30]

    then this returns:

    [
        [0, 9],
        [10, 19],
        [20, 29],
    ]

    Note the final lower band (30, here) is not used; it is just 1 higher
    than the upper limit for the previous band (29).
    """

    # bands_lower = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110]
    bands_lower = [18, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110,]

    bands = []

    for idx, lower in enumerate(bands_lower):
        if idx < len(bands_lower) - 1:
            upper = bands_lower[idx+1] - 1

            bands.append([lower, upper])

    return bands


if __name__ == "__main__":

    fetch_commons_data()

    fetch_lords_data()

    create_chart_file()
