# mechanical_property_parsing
This repo contains scripts that parses 1014 alloy compositions and their mechanical properties collected by Birbilis' research group.
The script main.py reads and parses alloy information from 'HEA_mechanical_dataset_ZL_full.xlsx' and outputs a excel file 'parsed_result_mechanical.xlsx'. 

Parsing rules for alloy composition:
1. The alloy composition are in a form same to CoFeNiSi0.5 or Al20(CoCrCuFeMnNiTiV)80.
2. When there is parenthesis, the program will first identify the parenthesis in the composition then parse the composition sequentially.
3. The output of the composition parser should be an N x M array contains all the molar ratios of elements that occurred in the dataset, where N is the number of alloys, M is the number of element.

Parsing rules for alloy phase:
1. The phases are in the form of Phase1+Phase2+...
2. The phases are divided into four groups: FCC, BCC, HCP, IM
3. The output of the phase parser should be an N x 4 array contains all the phases information of the alloy, where N is the number of alloys. The phase result should be either 1 or 0.


