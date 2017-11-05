#!/usr/bin/env python

"""

Script to parse Euro-IX json format that describes members of an IXP.

Details here: http://ml.ix-f.net/

"""

import sys
import json
import csv

def json_to_csv(json_in, csv_out):
    data = json.load(json_in)
    out = csv.writer(csv_out)
    for member in data['member_list']:
        asn = member['asnum']
        for c in member['connection_list']:
            for vlan in c['vlan_list']:
                if 'ipv4' in vlan:
                    row = [asn, 'ipv4', vlan['ipv4']['address']]
                    out.writerow(row)
                if 'ipv6' in vlan:
                    row = [asn, 'ipv6', vlan['ipv6']['address']]
                    out.writerow(row)

if __name__ == '__main__':
    json_in = sys.argv[1]
    csv_out = sys.argv[2]
    with open(json_in) as j:
        with open(csv_out, 'w') as c:
            json_to_csv(j, c)
