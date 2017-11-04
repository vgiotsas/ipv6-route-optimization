#!/usr/bin/env python3
import bz2
import ujson
import collections

probes_file = '20171103.json.bz2'
debug = True


def load_json():
    probes = collections.defaultdict(list)
    probes_blob = ujson.loads(bz2.BZ2File(probes_file).read())
    for probe in probes_blob['objects']:
        if 'system-ipv6-works' in probe['tags'] and 'system-ipv4-works' in probe['tags'] \
                and probe['asn_v4'] == probe['asn_v6'] and 'system-ipv4-stable-1d' in probe['tags']:
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