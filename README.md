# Mechanical Property Parsing

This repository contains scripts that parse the multi-principal element alloys (MPEA) dataset, which includes 1014 alloys' element compositions and mechanical properties, collected by Birbilis' research group.

The main script `main.py` reads and parses alloy information from `MPEA_mechanical_dataset_ZL_full.xlsx` and outputs an Excel file `parsed_result_mechanical.xlsx`.

## Parsing Rules

### Alloy Composition

1. The alloy compositions are in forms like `CoFeNiSi0.5` or `Al20(CoCrCuFeMnNiTiV)80`.
2. When there are parentheses, the program first identifies the parentheses in the composition, then parses the composition sequentially.
3. The output of the composition parser is an N x M array containing all the molar ratios of elements that occurred in the dataset, where N is the number of alloys, and M is the number of elements.

### Alloy Phase

1. The phases are in the form of `Phase1+Phase2+...`.
2. The phases are divided into four groups: FCC, BCC, HCP, IM.
3. The output of the phase parser is an N x 4 array containing all the phase information of the alloy, where N is the number of alloys. The phase result should be either 1 or 0.

## Usage

Run the main script to begin parsing:

```bash
python main.py

