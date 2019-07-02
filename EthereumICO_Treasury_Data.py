import requests
from lxml.html import fromstring
from itertools import islice
import csv

def chunk(it, size):
    it = iter(it)
    return iter(lambda: tuple(islice(it, size)), ())

if __name__ == "__main__":
	
	# request data from webpage
	data = fromstring(requests.get("https://diar.co/ethereum-ico-treasury-balances/").content)
	
	# crafty method to extract table headers
	data_headers = [i.text for i in data.xpath("//*") if i.tag == 'th'][:15]
	
	# crafty method to extract table data
	data_list = [i.text for i in data.xpath("//*") if i.tag == 'td']
	
	# split large list into list of tuples of size 15 for each table row
	eth_ico_balances = list(chunk(data_list, 15))
	
	# create a dictionary to weed out duplicate data
	eth_ico_dict = dict()
	for row in eth_ico_balances:
		if not row[0] in eth_ico_dict.keys():
			eth_ico_dict[row[0]] = tuple([int(i) for i in row[1 :]])
		else:
			pass
	
	#converting back to list of tuples
	x = list(eth_ico_dict.items())
	
	eth_ico_balances_final = []
	for i,j in enumerate(x):
		eth_ico_balances_final.append(tuple([x[i][0]] + list(x[i][1])))
	
	# write to file
	with open('/home/mkultra/Desktop/ETHICO_test.csv','w') as out:
		csv_out=csv.writer(out)
		csv_out.writerow(data_headers)
		for row in eth_ico_balances_final:
			csv_out.writerow(row)
	
	