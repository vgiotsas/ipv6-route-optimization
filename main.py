#!/usr/bin/env python3
from atlas_ipv6_opt.find_probes import load_json
import random
import os
import csv

from ripe.atlas.cousteau import (
    Traceroute,
    AtlasSource,
    AtlasCreateRequest)

API_KEY = os.getenv('RIPE_API')
base_url = 'https://atlas.ripe.net/api/v2/'
probe_limit = 100
debug = True
output_csv = 'atlas_measurements.csv'
interesting_asns = 'interesting_asns'


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
    probes = [p[0] for (a, p) in probes_by_as.items()]
    with open(interesting_asns) as r:
        asns = [int(l) for l in r.readlines()]

    new_probes = {}

    for p in probes:
        if p['asn_v6'] in asns:
            new_probes[p['id']] = p
    for p in random.sample(probes, len(probes)):
        if len(new_probes) >= probe_limit:
            break
        if p['asn_v6'] not in asns:
            new_probes[p['id']] = p

    with open(output_csv, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['dst_probe_id', 'msm_id_v4', 'msm_id_v6'])
        for target in new_probes.values():
            response = create_measurements(list(new_probes.keys()), target)
            if True in response:
                print(response[1]['measurements'])
                writer.writerow([target['id']] + response[1]['measurements'])
            else:
                print(response)


if __name__ == '__main__':
    main()

