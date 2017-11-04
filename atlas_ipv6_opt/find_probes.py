#!/usr/bin/env python3
import bz2
import ujson
import collections

probes_file = '20171103.json.bz2'
debug = True

tags = ('system-ipv6-works', 'system-ipv4-works', 'system-ipv4-stable-1d')

def load_json():
    probes = collections.defaultdict(list)
    probes_blob = ujson.loads(bz2.BZ2File(probes_file).read())
    for probe in probes_blob['objects']:
        missing_tag = False
        for tag in tags:
            if tag not in probe['tags']:
                missing_tag = True
        if missing_tag:
            continue
        elif probe['is_public'] is True and probe['asn_v4'] == probe['asn_v6'] \
                and probe['address_v4'] is not None and probe['address_v6'] is not None:
            if len(probes[probe['asn_v6']]) < 1:
                probes[probe['asn_v6']].append(probe)

    if debug:
        print("Found %s probes" % probes_blob['meta']['total_count'])
        print("%s ASes with working dual stack" % len(probes))

    return probes


def main():
    probes = load_json()


if __name__ == '__main__':
    main()