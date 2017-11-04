#!/usr/bin/env python

"""

Utilities to find IPv4/IPv6 prefixes that are "colocated", in the sense
that they are likely routed to the same physical location.

"""

import json
import sys

def prefixes_from_asn(probes_file, asn):
    """Given an ASN, returns a list of (IPv4 prefix, IPv6 prefix) of colocated
    prefixes originated from this ASN.  It uses Atlas probes."""
    probes = json.load(probes_file)
    interesting_probes = [probe for probe in probes['objects'] if probe['asn_v4'] == asn and probe['asn_v4'] == probe['asn_v6']]
    return set((probe['prefix_v4'], probe['prefix_v6']) for probe in interesting_probes)


if __name__ == '__main__':
    with open(sys.argv[1]) as probe_file:
        for pair in prefixes_from_asn(probe_file, int(sys.argv[2])):
            print("{}\t{}".format(pair[0], pair[1]))
