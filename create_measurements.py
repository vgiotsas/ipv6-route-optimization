#!/usr/bin/env python3
import ujson
import bz2
import random
import sys
import os

from ripe.atlas.cousteau import (
    Traceroute,
    AtlasSource,
    AtlasCreateRequest)

API_KEY = os.getenv('RIPE_API')
base_url = "https://atlas.ripe.net/api/v2/"
probes_file = '20171031.json.bz2'
debug = True
num_probes = 50

# Perhaps iterate over each area one at a time and get a selection of probes from each?
areas = ['West', 'North-Central', 'South-Central', 'North-East', 'South-East']

def load_json():
    probes = []
    probes_blob = ujson.loads(bz2.BZ2File(probes_file).read())
    for probe in probes_blob['objects']:
        if ('system-ipv6-works' and 'system-ipv4-works' in probe['tags']) and (probe['asn_v4'] == probe['asn_v6']):
            probes.append(probe['id'])

    if debug:
        print("Found %s probes" % probes_blob['meta']['total_count'])
        print("%s probes with working dual stack" % len(probes))

    return probes


def main():
    try:
        target = sys.argv[1]
    except:
        print('Please provide a host to traceroute')
        exit(1)

    probes = load_json()

    sources = AtlasSource(
        type='probes',
        value=','.join(str(x) for x in random.sample(probes, num_probes)),
        requested=num_probes
    )

    tr4 = Traceroute(
        af=4,
        target=target,
        description='Transient tr4 test',
        protocol='ICMP'
    )

    tr6 = Traceroute(
        af=6,
        target=target,
        description='Transient tr6 test',
        protocol='ICMP'
    )

    atlas_request = AtlasCreateRequest(
        key=API_KEY,
        measurements=[tr4, tr6],
        sources=[sources],
        is_oneoff=True
    )

    response = atlas_request.create()
    print(response)

if __name__ == '__main__':
    main()

