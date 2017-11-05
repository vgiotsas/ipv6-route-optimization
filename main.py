#!/usr/bin/env python3
from atlas_ipv6_opt.probes import load_json, create_measurements
import random
import csv

base_url = 'https://atlas.ripe.net/api/v2/'
probe_limit = 100
output_csv = 'atlas_measurements.csv'
interesting_asns = 'interesting_asns'


def main():

    probes_by_as = load_json()
    probes = [p[0] for (a, p) in probes_by_as.items()]
    # Hack to prioritise ASNs we think are problematic
    with open(interesting_asns) as r:
        asns = [int(l) for l in r.readlines()]

    new_probes = {}

    for p in probes:
        if p['asn_v6'] in asns:
            new_probes[p['id']] = p
    # Once we've selected the problematic ASNs, fill up remainder randomly
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

