import pandas
import numpy
import math

mech_data = pandas.read_excel('HEA_mechanical_dataset_ZL_full.xlsx')
element_set = set()


def parse(comp):
    # print('start decoding: ', comp)
    ele_list = []
    ratio_list = []

    head = 0
    while head < len(comp):
        if not comp[head].isupper():
            head += 1
            continue

        num_start = head + 1
        num_end = num_start
        if head + 1 < len(comp) and comp[head + 1].islower():
            ele = comp[head:head + 2]
            num_start = head + 2
        else:
            ele = comp[head:head + 1]

        for i in range(len(comp) - num_start):
            if not comp[num_start + i].isnumeric() and not comp[num_start + i] == '.':
                num_end = num_start + i
                break
            if num_start + i == len(comp) - 1:
                num_end = num_start + i + 1
        number = comp[num_start:num_end]
        ele_list.append(ele.strip())
        element_set.add(ele.strip())

        ele_ratio = float(1)
        if len(number.strip()) > 0:
            ele_ratio = float(number.strip())
        ratio_list.append(ele_ratio)
        head += 1
    return ele_list, ratio_list


def decode(alloy_name):
    # print('start decoding:', alloy_name)

    ele_list = []
    ratio_list = []

    comp = alloy_name.strip()
    paren_start = 0
    paren_end = 0
    has_paren = False

    # check if there is a parenthesis in the composition.
    for i in range(len(comp)):
        if comp[i] == '(':
            paren_start = i
            has_paren = True
        if comp[i] == ')':
            paren_end = i
    # If there is, parse the composition, molar ratio of the elements in the parenthesis.
    if has_paren:
        comp_in_paren = comp[paren_start + 1:paren_end]
        paren_num = ""
        paren_num_end = 0
        for k in range(len(comp) - paren_end - 1):
            if k > len(comp) - 1 or comp[k + 1 + paren_end].isupper():
                break
            paren_num = comp[paren_end + 1:k + 2 + paren_end]
            paren_num_end = k + 2 + paren_end
        # Decode the compositions before and after the parenthesis.
        comp_front = comp[0:paren_start]
        comp_end = comp[paren_num_end:]

        # Print all the composition strings.

        # print('find parenthesis composition:', comp)
        # print('start decoding parenthesis composition:', comp_in_paren, 'with parenthesis number:', paren_num)

        paren_ele_list, paren_ratio_list = parse(comp_in_paren)
        paren_ratio = float(paren_num) / sum(paren_ratio_list)
        for i in range(len(paren_ratio_list)):
            paren_ratio_list[i] = round(paren_ratio_list[i] * paren_ratio, 2)

        # print('paren ele list:', paren_ele_list)
        ele_list = paren_ele_list
        # print('paren ratio list:', paren_ratio_list)
        ratio_list = paren_ratio_list

        if len(comp_front) > 0:
            # print('comp_front:', comp_front)
            front_ele_list, front_ratio_list = decode(comp_front)
            ele_list = front_ele_list + ele_list
            ratio_list = front_ratio_list + ratio_list
        if len(comp_end) > 0:
            # print('comp_end:', comp_end)
            end_ele_list, end_ratio_list = decode(comp_end)
            ele_list = ele_list + end_ele_list
            ratio_list = ratio_list + end_ratio_list

    else:
        ele_list, ratio_list = parse(comp)

    return ele_list, ratio_list


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    feature = mech_data.columns.values

    alloy_list = mech_data[feature[0]]
    phase_list = mech_data[feature[1]]
    hardness_list = mech_data[feature[2]]
    yield_list = mech_data[feature[3]]
    tensile_list = mech_data[feature[4]]
    elongation_list = mech_data[feature[5]]
    compressive_list = mech_data[feature[6]]
    plasticity_list = mech_data[feature[7]]

    decoded_alloy_list = []
    decoded_ratio_list = []

    # parse('Al11.3V2.3Be4.5')
    # print(decode(' (Al2V Be 2Ve 3BE)18 Ti2(Ti4Be3)34'))

    # for each alloy composition in the dataset, decode and parse each composition and add the decoded result into list
    for i in range(len(alloy_list)):
        alloy_comp = alloy_list[i]
        # print(i+1, alloy_comp)
        decoded_alloy, decoded_ratio = decode(alloy_comp)
        ratio_sum = sum(decoded_ratio)
        for j in range(len(decoded_ratio)):
            decoded_ratio[j] = decoded_ratio[j] / ratio_sum
        # print(decoded_alloy)
        # print(decoded_ratio)
        decoded_alloy_list.append(decoded_alloy)
        decoded_ratio_list.append(decoded_ratio)

    # count all the element occurred in the decoding and create an element list.
    element_list = sorted(list(element_set))
    # print()
    # print('element list:', element_list)

    # use a numpy array to record all the molar ratios for the whole dataset
    n_y = len(mech_data[feature[0]])
    n_x = len(element_list)
    ele_ratio_array = numpy.zeros((n_y, n_x))
    for i in range(n_y):
        decoded_alloy = decoded_alloy_list[i]
        decoded_ratio = decoded_ratio_list[i]
        for j in range(len(decoded_alloy)):
            element = decoded_alloy[j]
            ratio = decoded_ratio[j]
            index = element_list.index(element)
            ele_ratio_array[i][index] = ratio
    # print(ele_ratio_array)

    # for each alloy composition, decode its phase information into a list of [FCC, BCC, HCP, IM]
    phase_array = numpy.zeros((n_y, 4))

    for i in range(len(phase_list)):
        # print(i)
        if isinstance(phase_list[i], str):
            phases = []
            split_list = phase_list[i].split('+')
            for j in range(len(split_list)):
                phases.append(split_list[j].strip().upper())
            # print(phases)

            for phase in phases:
                if 'FCC' in phase:
                    phase_array[i][0] = 1
                elif 'BCC' in phase:
                    phase_array[i][1] = 1
                elif 'HCP' in phase:
                    phase_array[i][2] = 1
                else:
                    phase_array[i][3] = 1

            # print(phase_array[i])

    # print('phase array:',phase_array)

    # concatenate the parsed result and the original dataset, write to an excel file

    ratios_df = pandas.DataFrame(ele_ratio_array, columns=element_list)
    phases_df = pandas.DataFrame(phase_array, columns=['FCC', 'BCC', 'HCP', 'IM'])
    output_df = pandas.concat([phases_df, mech_data.drop([feature[1], feature[9]], axis=1), ratios_df],
                              axis=1)
    print(output_df)
    output_df.to_excel('parsed_result_mechanical.xlsx')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
