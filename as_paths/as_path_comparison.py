#!/usr/bin/env python

import sys
import json
import requests
import csv

RIPE_STAT_API = "https://stat.ripe.net/data/looking-glass/data.json"

def uniqify(l):
    return [e for i, e in enumerate(my_list) if my_list.index(e) == i]

def _as_paths(prefix):
    """Get all AS paths towards the given prefix, as seen by RIS."""
    result = list()
    response = requests.get(RIPE_STAT_API, params={"resource": prefix})
    decoded_response = response.json()
    for collector in decoded_response['data']['rrcs'].values():
        for entry in collector['entries']:
            result.append([int(asn) for asn in entry['as_path'].split()])
    return result

def as_path_length_to_csv(dest_prefix_v4, dest_prefix_v6, out_csv):
    aspaths_v4 = _as_paths(dest_prefix_v4)
    aspaths_v6 = _as_paths(dest_prefix_v6)
    with open(out_csv, 'w') as file_out:
        out = csv.writer(file_out)
        row = ['AddrFamily', 'ASPathLength']
        out.writerow(row)
        for path in aspaths_v4:
            out.writerow(['ipv4', len(path)])
        for path in aspaths_v6:
            out.writerow(['ipv6', len(path)])

def as_paths_by_neighbour(dest_prefix_v4, dest_prefix_v6, out_csv):
    """For the given prefixes, classify the AS paths from RIS based on the
    neighbouring ASes of the prefixes.  This allows to compare the
    "connectivity" of transit providers, by looking at the AS length.
    """
    aspaths_v4 = _as_paths(dest_prefix_v4)
    aspaths_v6 = _as_paths(dest_prefix_v6)
    find_neighbours()


v4_prefix = sys.argv[1]
v6_prefix = sys.argv[2]
outfile = '{}-{}.csv'.format(v4_prefix.replace('/', '_'), v6_prefix.replace('/', '_'))
as_path_length_to_csv(v4_prefix, v6_prefix, outfile)
