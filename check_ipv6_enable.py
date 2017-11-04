import csv
import subprocess
with open('top-1m.csv', 'rb') as csvfile:
    top_sites = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in top_sites:
        return_code = subprocess.check_output("nslookup -type=aaaa " + row[1] + ' 8.8.8.8', stderr = subprocess.STDOUT,shell = True)
        return_code = return_code.replace('Address:  8.8.8.8', '')
        return_code = return_code.replace('Server:  google-public-dns-a.google.com', '')
        return_code = return_code.replace('Non-authoritative answer:', '')
        if 'Address' in return_code:
            v6 = 1
        else:
            v6 = 0
        with open('ipv6_result.csv', 'ab') as f:
            writer = csv.writer(f)
            writer.writerow([row[1], v6])
