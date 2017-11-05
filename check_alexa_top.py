#!/usr/bin/env python3
""" A small script to check the Alexa top 1M sites
    and spit out a file with the top X that have AAAA records. """
import csv
import dns.resolver
import requests
import io
import zipfile

url = 'http://s3.amazonaws.com/alexa-static/top-1m.csv.zip'
outfile = 'top-ipv6.csv'
max_count = 100
debug = True

def get_top1m(url):
    top_sites = []
    if debug:
        print('Fetching %s' % url)
    r = requests.get(url)
    if debug:
        print('Unzipping')
    z = io.BytesIO(r.content)
    z = zipfile.ZipFile(z, 'r')
    data = z.read('top-1m.csv')
    csvfile = csv.reader(io.StringIO(data.decode('utf-8')))
    for line in csvfile:
        top_sites.append(line[1])

    return top_sites


def resolve_host(host):
    try:
        A = dns.resolver.query(host, rdtype='A')
        AAAA = dns.resolver.query(host, rdtype='AAAA')
        if debug:
            print('%s has both A and AAAA records' % host)
        return True
    except:
        return False


def main():

    hosts = get_top1m(url)
    ds_hosts = []
    with open(outfile, 'w') as out:
        writer = csv.writer(out)
        for line in hosts:
            if len(ds_hosts) < max_count:
                response = resolve_host(line)
                if response is True:
                    ds_hosts.append(line)
                    writer.writerow([line])


if __name__ == '__main__':
    main()

