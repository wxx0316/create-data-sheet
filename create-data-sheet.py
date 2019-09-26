import argparse
import requests, json
import csv

def parse_arg():
	p = argparse.ArgumentParser()
	p.add_argument('-i', help="Input metadata table.")
	p.add_argument('-o', help="Output prefix.")
	p.add_argument('-d', help="Directory of downloaded data.")

	return p.parse_args()

def getinfo(s,directory,head):

    #get track name
	accession = s[3]
	headers = {'accept': 'application/json'}
	url = 'https://data.4dnucleome.org/experiment-set-replicates/'+ s[3] +'/?frame=object'
	response = requests.get(url, headers=headers)
	biosample = response.json()
	if 'track_title' in biosample['track_and_facet_info'].keys():
		track_name=biosample['track_and_facet_info']['track_title']
	else:
		#print("No track name for " + s[3] + "!")
		#track_name=s[3]
		url = 'https://data.4dnucleome.org/experiment-set-replicates/'+ s[1] +'/?frame=object'
		response = requests.get(url, headers=headers)
		biosample = response.json()
		if 'description' in biosample.keys():
			track_name = biosample['description']
		else:
			print("No track name for " + s[3] + "!")
			track_name = s[3]
    
    #genome version
	if s[13]=="human":
		genome = "hg38"
	if s[13]=="mouse":
		genome = "mm10"
    
    #info_json
	#d = {}
	#for i in range(len(head)):
	#	d[head[i]]=s[i]
	#info = json.dumps(d)
	info = track_name    

	if s[7]=="bw":
		extension = ".bw"
	elif s[7]=="bigbed":
		extension = ".bb"
	elif s[7]=="contact matrix":
		extension = ".hic"
	else:
		extension = "."+s[7]
    
    #name
	short_name = s[3]
	long_name = track_name
    
	line = [s[3],s[8],s[7],s[8],genome,s[11],directory+s[3]+extension,short_name,long_name,'https://data.4dnucleome.org/'+s[3],info]
	return line

def writeTSV(output,table):
	with open(output, 'w') as tsv_file:
		tsv_writer = csv.writer(tsv_file, delimiter='\t', lineterminator='\n')
		tsv_writer.writerow(["Accession_ID","Data_Type","Format","Protocol","Genome","Biosource","uri","shortLabel","longLabel","metaLink","Notes"])
		for i in range(len(table)):
			tsv_writer.writerow(table[i])




if __name__ == '__main__':

	args = parse_arg()

	#read metadata
	metadata = []
	with open(args.i) as tsvfile:
		tsvreader = csv.reader(tsvfile, delimiter="\t")
		for line in tsvreader:
			if not line[0].startswith("#"):
				metadata.append(line)

	table = []
	for i in range(len(metadata)):
		if metadata[i][7] in ["bw","bigbed","hic","contact matrix"] and metadata[i][13] in ["human","mouse"]:
			table.append(getinfo(metadata[i],args.d,metadata[0]))

	table_list = {}
	for i in range(len(table)):
		if (table[i][1],table[i][4]) in table_list.keys():
			table_list[(table[i][1],table[i][4])].append(table[i])
		else:
			table_list[(table[i][1],table[i][4])]=[table[i]]

	for (data,genome) in table_list.keys():
		writeTSV(args.o + "." + data + "." + genome + ".tsv",table_list[(data,genome)])










