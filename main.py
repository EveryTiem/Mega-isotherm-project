import json
from urllib.request import urlopen
from sys import exit
import csv

# get list of adsorbents
adsorbent_json = json.load(urlopen("https://adsorbents.nist.gov/matdb/api/materials.json"))

# get list of adsorbates
adsorbate_json = json.load(urlopen("https://adsorbents.nist.gov/isodb/api/gases.json"))


# get list of isotherms for searching
item1 = json.load(urlopen("https://adsorbents.nist.gov/isodb/api/isotherms.json"))

# list of good files
file_list = []

# list of data pts
data = []

# find hashkey for adsorbent
adsorbent_hashkey = None
while adsorbent_hashkey == None:

  adsorbent = input("adsorbent >> ")

  for x in adsorbent_json:
    if x['name'] == adsorbent or adsorbent in x['synonyms']:
      adsorbent_hashkey = x['hashkey']
      break

  if adsorbent_hashkey == None:
    print("adsorbent not found")

num_adsorbate = None
while num_adsorbate == None:
  try:
    num_adsorbate = int(input("How many adsorbates? >> "))
  except ValueError:
    print("please input a valid integer")

adsorbate_InChIKey_list = []
adsorbate_list = []

# find InChIKey for adsorbate
for n in range(num_adsorbate):
  adsorbate_InChIKey = None
  while adsorbate_InChIKey == None:

    adsorbate = input("adsorbate >> ")

    for x in adsorbate_json:
      if x['name'] == adsorbate or adsorbate in x['synonyms']:
        adsorbate_InChIKey_list.append(x['InChIKey'])
        adsorbate_list.append(adsorbate)
        adsorbate_InChIKey = 1
        break

    if adsorbate_InChIKey == None:
      print("adsorbate not found")

temperature = None
while temperature == None:

  temperature = input("temp >> ")

  try:
    temperature = int(temperature)
    break
  except ValueError:
    print("please input a valid integer")

ads_unit = input("adsorption units >> ")

# for each isotherm
for x in item1:
  count = 0
  for key in adsorbate_InChIKey_list:
    # if adsorbate is N2 and adsorbent is CuBTC, add it to list
    if {"InChIKey": f"{key}"} in x['adsorbates'] and x['adsorbent']['hashkey'] == f'{adsorbent_hashkey}' and len(x['adsorbates']) == num_adsorbate and x['temperature'] == temperature:
      count += 1
  if count == num_adsorbate:
    file_list.append(x['filename'])

# for each isotherm
for filename in file_list:
  #open JSON file
  file_ = json.load(urlopen(f"https://adsorbents.nist.gov/isodb/api/isotherm/{filename}.json"))
  print(filename)
  # if the units are what we want
  if file_['adsorptionUnits'] == ads_unit:
    for l in range(num_adsorbate):
      #for each data pt
      for num in range(len(file_['isotherm_data'])):
        #for type in ['pressure', 'total_adsorption']:
          #print(f"{type}: {file_['isotherm_data'][num][type]}")
        # add data pt to list
        data.append((file_['isotherm_data'][num]['pressure'], file_['isotherm_data'][num]['species_data'][l]['adsorption'], adsorbate_list[l], filename))
        print((file_['isotherm_data'][num]['pressure'], file_['isotherm_data'][num]['species_data'][l]['adsorption'], adsorbate_list[l]))

adsorbate_str = ' '.join(adsorbate_list)

with open(((adsorbate_str + ' ' + adsorbent + ' ' + str(temperature) + ' ' + ads_unit.replace('/', ' per ') + ".csv") if len(data) != 0 else ('ZZZEMPTY' + adsorbate_str + ' ' +adsorbent + ' ' + str(temperature) + ' ' + ads_unit.replace('/', ' per ') + ".csv")), 'w+') as out:
    fieldnames = ['pressure', 'Q', 'species', 'filename']
    writer = csv.DictWriter(out, fieldnames=fieldnames)

    writer.writeheader()

    for datapoint in data:
        writer.writerow({'pressure': datapoint[0], 'Q': datapoint[1], 'species': datapoint[2], 'filename': datapoint[3]})

    out.close()
