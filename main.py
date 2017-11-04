#!/usr/bin/env python3
from atlas_ipv6_opt.find_probes import load_json
import random
import os

from ripe.atlas.cousteau import (
    Traceroute,
    AtlasSource,
    AtlasCreateRequest)

API_KEY = os.getenv('RIPE_API')
base_url = "https://atlas.ripe.net/api/v2/"
probe_limit = 1000
debug = True


def create_measurements(probes, target):
    num_probes = len(probes)

    sources = AtlasSource(
        type='probes',
        value=','.join(str(x) for x in random.sample(probes, num_probes)),
        requested=num_probes
    )

    tr4 = Traceroute(
        af=4,
        target=target['address_v4'],
        description='Transient tr4 test',
        protocol='ICMP'
    )

    tr6 = Traceroute(
        af=6,
        target=target['address_v6'],
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
    return response


def main():

    probes_by_as = load_json()
    probes = [p[0] for (a,p) in probes_by_as.items()][:probe_limit]
    probe_ids = [p['id'] for p in probes]

    for target in probes:
        #response = create_measurements(probe_ids, target)
        #print(response)
        break

if __name__ == '__main__':
    main()

