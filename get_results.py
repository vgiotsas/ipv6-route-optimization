#!/usr/bin/env python3
import argparse
import requests
import time
import sys
from ripe.atlas.sagan import TracerouteResult

#measurements = [10109356, 10109357]        # 1000 probes on boosh.fm
#measurements = [10113733, 10113734]         # 1000 probes on boosh.fm
#measurements = [10110318, 10110319]         # 100 probes on boosh.fm
#measurements = [10114435, 10114436]         # 1000 probes on www.sprint.net
base_url = "https://atlas.ripe.net/api/v2/"
debug = False
hop_threshold = 5   # How many hops different do we consider bad
rtt_threshold = 10   # How many ms different do we consider bad


def fetch_results(measurements):
    results = {}
    for id in measurements:
        meta = requests.get(base_url+'measurements/'+str(id)).json()
        response = requests.get(base_url+'measurements/'+str(id)+'/latest/').json()
        results[meta['af']] = response

    return results


def combine_results(results):
    """ Combines results in to a searchable table indexed by probe_id
    """
    probe_table = {}

    for result in results[4]:
        probe_table[result['prb_id']] = {}
        probe_table[result['prb_id']][4] = result

    for result in results[6]:
        probe_table[result['prb_id']][6] = result

    return probe_table


def compare_results(probe_table):
    for probe_id in probe_table:
        if debug:
            print('Parsing probe_id: %s' % probe_id)
        r4 = TracerouteResult(probe_table[probe_id][4], on_error=TracerouteResult.ACTION_IGNORE)
        r6 = TracerouteResult(probe_table[probe_id][6], on_error=TracerouteResult.ACTION_IGNORE)

        if r4.is_success and r6.is_success:
            probe = None
            if r6.total_hops - r4.total_hops > hop_threshold:
                probe = get_probe_details(probe_id)
                more_hops = r6.total_hops - r4.total_hops
                print('AS%s - %s hop count:%s vs %s hop count:%s - IPv6 has %s more hops'
                      % (probe['asn_v6'], probe['prefix_v6'], r6.total_hops,
                         probe['prefix_v4'], r4.total_hops, more_hops))

            elif r4.total_hops - r6.total_hops > hop_threshold:
                probe = get_probe_details(probe_id)
                more_hops = r4.total_hops - r6.total_hops
                print('AS%s - %s hop count:%s vs %s hop count:%s - IPv4 has %s more hops'
                      % (probe['asn_v4'], probe['prefix_v4'], r4.total_hops,
                         probe['prefix_v6'], r6.total_hops, more_hops))

            if r6.last_median_rtt - r4.last_median_rtt > rtt_threshold:
                if probe is None:
                    probe = get_probe_details(probe_id)
                percent = int(((r6.last_median_rtt - r4.last_median_rtt) / r4.last_median_rtt) * 100)
                print('AS%s - %s RTT:%s vs %s RTT:%s - IPv6 is %s%% worse'
                      % (probe['asn_v6'], probe['prefix_v6'], r6.last_median_rtt,
                         probe['prefix_v4'], r4.last_median_rtt, percent))
            elif r4.last_median_rtt - r6.last_median_rtt > rtt_threshold:
                if probe is None:
                    probe = get_probe_details(probe_id)
                percent = int(((r4.last_median_rtt - r6.last_median_rtt) / r6.last_median_rtt) * 100)
                print('AS%s - %s RTT:%s vs %s RTT:%s - IPv4 is %s%% worse'
                      % (probe['asn_v4'], probe['prefix_v4'], r4.last_median_rtt,
                         probe['prefix_v6'], r6.last_median_rtt, percent))
        else:
            if debug:
                if r6.destination_ip_responded is False or r6.last_hop_responded is False:
                    print('Probe:%s could not trace to %s' % (r6.probe_id, r6.destination_address))
                elif r4.destination_ip_responded is False or r4.last_hop_responded is False:
                    print('Probe:%s could not trace to %s' % (r4.probe_id, r4.destination_address))
            pass


def get_probe_details(probe_id):
    url = base_url+'probes/'+str(probe_id)
    results = requests.get(url).json()
    return results


def parse_args(args=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('measurementv4', help='Atlas measurement ID for IPv4')
    parser.add_argument('measurementv6', help='Atlas measurement ID for IPv6')
    return parser.parse_args()


def main():

    args = parse_args()

    results = fetch_results([args.measurementv4, args.measurementv6])
    while len(results[4]) != len(results[6]):
        if debug:
            for af in results:
                print("%s has %s results" % (af, len(results[af])))
        print('Waiting for measurements to complete')
        time.sleep(5)
        results = fetch_results(measurements)

    probe_table = combine_results(results)
    compare_results(probe_table)

if __name__ == '__main__':
    main()
