import bz2
import ujson
import collections
import random
import requests
import os
from ripe.atlas.cousteau import (
    Traceroute,
    AtlasSource,
    AtlasCreateRequest)

debug = True

# Probe list from http://ftp.ripe.net/ripe/atlas/probes/archive/meta-latest
probes_file = 'data/20171103.json.bz2'
API_KEY = os.getenv('RIPE_API')
base_url = 'https://atlas.ripe.net/api/v2/'
cost_per_trace = 6
wanted_tags = ('system-ipv6-works', 'system-ipv4-works', 'system-ipv4-stable-1d')


def check_credits():
    url = base_url+'credits/?key='+API_KEY
    r = requests.get(url)
    atlas_credits = r.json()['current_balance']
    return atlas_credits


def load_json():
    probes = collections.defaultdict(list)
    probes_blob = ujson.loads(bz2.BZ2File(probes_file).read())
    for probe in probes_blob['objects']:
        missing_tag = False
        for tag in wanted_tags:
            if tag not in probe['tags']:
                missing_tag = True
        if missing_tag:
            # skip this probe
            continue
        elif probe['is_public'] is True and probe['asn_v4'] == probe['asn_v6'] \
                and probe['address_v4'] is not None and probe['address_v6'] is not None:
            if len(probes[probe['asn_v6']]) < 1:
                probes[probe['asn_v6']].append(probe)

    if debug:
        print("Found %s probes" % probes_blob['meta']['total_count'])
        print("%s ASes with working dual stack" % len(probes))

    return probes


def create_measurements(probes, target):
    '''
    Create two new ICMP traceroute measurements, one for the IPv4 target address
    and one for the IPv6.
    '''
    num_probes = len(probes)
    atlas_credits = check_credits()
    cost = (num_probes * num_probes) * cost_per_trace
    if debug:
        print('Estimated cost:%s, Available credits:%s' % (cost, atlas_credits))
    if cost < atlas_credits:
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
    else:
        print('The cost %s would exceed your available credits %s' % (cost, atlas_credits))
        response = None

    return response
