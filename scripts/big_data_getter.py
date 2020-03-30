import json
from urllib.request import urlopen
from sys import exit
import csv

##########################################################################################
### Gets many adsorbent/adsorbate combinations at once                                 ###
### Can be edited to the user's purposes by changing the names in the nested for-loops ###
### Comments in code are past edits and possible future updates                        ###
##########################################################################################

# get list of adsorbents
adsorbent_json = json.load(urlopen("https://adsorbents.nist.gov/matdb/api/materials.json"))

# get list of adsorbates
adsorbate_json = json.load(urlopen("https://adsorbents.nist.gov/isodb/api/gases.json"))


# get list of isotherms for searching
item1 = json.load(urlopen("https://adsorbents.nist.gov/isodb/api/isotherms.json"))


# User-input section (searches all combinations of adsorbents, adsorbates, temperatures, and units)
for adsorbent in ['CuBTC', 'Zeolite 13X', 'MOF-1', 'UiO-66', 'Activated Carbon']:
    for adsorbate1 in ['', 'N2', 'CO2', 'CH4', 'Ar', 'H2', 'H2O']:
        for adsorbate2 in ['', 'N2', 'CO2', 'CH4', 'Ar', 'H2', 'H2O']:
            for temperature in [77, 298, 303, 308]:
                for ads_unit in ['mmol/g', 'mg/g']:

                    # list of good files
                    file_list = []

                    # list of data pts
                    data = []

                    # find hashkey for adsorbent
                    #adsorbent_hashkey = None
                    #while adsorbent_hashkey == None:

                      #adsorbent = input("adsorbent >> ")

                    # Finds the adsorbent's hashkey
                    for x in adsorbent_json:
                        if x['name'] == adsorbent or adsorbent in x['synonyms']:
                          adsorbent_hashkey = x['hashkey']
                          break

                      #if adsorbent_hashkey == None:
                        #print("adsorbent not found")
                    
                    # Gets the number of adsorbates proposed
                    num_adsorbate = 1 if (adsorbate1 == '' or adsorbate2 == '') else 2
                    #while num_adsorbate == None:
                     # try:
                    #    num_adsorbate = int(input("How many adsorbates? >> "))
                     # except ValueError:
                    #    print("please input a valid integer")

                    # List of adsorbates and their InChIKeys
                    adsorbate_InChIKey_list = []
                    adsorbate_list = []

                    # find InChIKey for adsorbate
                    #for n in range(num_adsorbate):
                      #adsorbate_InChIKey = None
                      #while adsorbate_InChIKey == None:

                        #adsorbate = input("adsorbate >> ")
                    
                    # Adds adsorbates and InChIKeys to lists
                    if adsorbate1 != '':
                        for x in adsorbate_json:
                          if x['name'] == adsorbate1 or adsorbate1 in x['synonyms']:
                            adsorbate_InChIKey_list.append(x['InChIKey'])
                            adsorbate_list.append(adsorbate1)
                            #adsorbate_InChIKey =
                            break

                    if adsorbate2 != '' and not adsorbate1 == adsorbate2:
                        for x in adsorbate_json:
                          if x['name'] == adsorbate2 or adsorbate2 in x['synonyms']:
                            adsorbate_InChIKey_list.append(x['InChIKey'])
                            adsorbate_list.append(adsorbate2)
                            #adsorbate_InChIKey = 1
                            break


                        #if adsorbate_InChIKey == None:
                          #print("adsorbate not found")

                    #temperature = None
                    #while temperature == None:

                      #temperature = input("temp >> ")

                      #try:
                        #temperature = int(temperature)
                        #break
                      #except ValueError:
                        #print("please input a valid integer")

                    #ads_unit = input("adsorption units >> ")

                    # Adds files to list if adsorbates and adsorbents match user input
                    # for each isotherm
                    for x in item1:
                      count = 0
                      for key in adsorbate_InChIKey_list:
                        # if adsorbate is N2 and adsorbent is CuBTC, add it to list
                        if {"InChIKey": f"{key}"} in x['adsorbates'] and x['adsorbent']['hashkey'] == f'{adsorbent_hashkey}' and len(x['adsorbates']) == num_adsorbate and x['temperature'] == temperature:
                          count += 1
                      if count == num_adsorbate and x['filename'] not in file_list:
                        file_list.append(x['filename'])

                    # Prints name of all files matching the adsorbate/adsorbent combination and adds files with the requested units to done_files
                    # for each isotherm
                    done_files = []
                    for filename in file_list:
                      #open JSON file
                      file_ = json.load(urlopen(f"https://adsorbents.nist.gov/isodb/api/isotherm/{filename}.json"))
                      print(filename)
                      # if the units are what we want
                      if file_['adsorptionUnits'] == ads_unit and filename not in done_files:
                        done_files.append(filename)
                        for l in range(num_adsorbate):
                          #for each data pt
                          for num in range(len(file_['isotherm_data'])):
                            #for type in ['pressure', 'total_adsorption']:
                              #print(f"{type}: {file_['isotherm_data'][num][type]}")
                            # add data pt to list
                            data.append((file_['isotherm_data'][num]['pressure'], 
                                         file_['isotherm_data'][num]['species_data'][l]['composition'], 
                                         file_['isotherm_data'][num]['species_data'][l]['adsorption'], 
                                         adsorbate_list[l], filename))
                            print((file_['isotherm_data'][num]['pressure'], 
                                   file_['isotherm_data'][num]['species_data'][l]['adsorption'], 
                                   adsorbate_list[l]))

                    adsorbate_str = ' '.join(adsorbate_list)
                    # Creates a csv for an isotherm and writes the isotherm's data
                    with open(((adsorbate_str + ' ' + adsorbent + ' ' + str(temperature) + ' ' + ads_unit.replace('/', ' per ') + ".csv") if len(data) != 0 else ('ZZZEMPTY' + adsorbate_str + ' ' +adsorbent + ' ' + str(temperature) + ' ' + ads_unit.replace('/', ' per ') + ".csv")), 'w+') as out:
                        fieldnames = ['pressure', 'composition', 'Q', 'species', 'filename']
                        writer = csv.DictWriter(out, fieldnames=fieldnames)

                        writer.writeheader()

                        for datapoint in data:
                            writer.writerow({'pressure': datapoint[0], 'composition': datapoint[1], 'Q': datapoint[2], 'species': datapoint[3], 'filename': datapoint[4]})

                        out.close()
