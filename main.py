import pandas
import numpy

def parse(comp, element_set):
    """Parse the given composition into elements and ratios.

    Args:
        comp (str): The alloy composition to parse.
        element_set (set): The set of unique elements found so far.

    Returns:
        tuple: The list of elements and corresponding ratios.
    """
    ele_list = []
    ratio_list = []
    head = 0
    while head < len(comp):
        if not comp[head].isupper():
            head += 1
            continue

        if head + 1 < len(comp) and comp[head + 1].islower():
            ele = comp[head:head + 2]
            num_start = head + 2
        else:
            ele = comp[head:head + 1]

        num_end = num_start
        while num_end < len(comp) and (comp[num_end].isnumeric() or comp[num_end] == '.'):
            num_end += 1

        number = comp[num_start:num_end]
        ele_list.append(ele.strip())
        element_set.add(ele.strip())

        ele_ratio = float(number) if number.strip() else 1
        ratio_list.append(ele_ratio)

        head = num_end

    return ele_list, ratio_list


def decode(alloy_name, element_set):
    """Decode the given alloy name into elements and ratios.

    Args:
        alloy_name (str): The alloy name to decode.
        element_set (set): The set of unique elements found so far.

    Returns:
        tuple: The list of elements and corresponding ratios.
    """
    ele_list = []
    ratio_list = []

    comp = alloy_name.strip()
    paren_start = 0
    paren_end = 0
    has_paren = False

    # Check for parentheses in the composition.
    for i in range(len(comp)):
        if comp[i] == '(':
            paren_start = i
            has_paren = True
        if comp[i] == ')':
            paren_end = i

    if has_paren:
        comp_in_paren = comp[paren_start + 1:paren_end]
        paren_num = comp[paren_end + 1:paren_end + 2]
        comp_front = comp[0:paren_start]
        comp_end = comp[paren_end + 2:]

        paren_ele_list, paren_ratio_list = parse(comp_in_paren, element_set)
        paren_ratio = float(paren_num) / sum(paren_ratio_list)
        for i in range(len(paren_ratio_list)):
            paren_ratio_list[i] = round(paren_ratio_list[i] * paren_ratio, 2)

        ele_list = paren_ele_list
        ratio_list = paren_ratio_list

        if comp_front:
            front_ele_list, front_ratio_list = decode(comp_front, element_set)
            ele_list = front_ele_list + ele_list
            ratio_list = front_ratio_list + ratio_list
        if comp_end:
            end_ele_list, end_ratio_list = decode(comp_end, element_set)
            ele_list = ele_list + end_ele_list
            ratio_list = ratio_list + end_ratio_list

    else:
        ele_list, ratio_list = parse(comp, element_set)

    return ele_list, ratio_list

if __name__ == '__main__':
    mech_data = pandas.read_excel('HEA_mechanical_dataset.xlsx')
    element_set = set()

    feature = mech_data.columns.values
    alloy_list = mech_data[feature[0]]
    phase_list = mech_data[feature[1]]

    decoded_alloy_list = []
    decoded_ratio_list = []

    # Decode and parse each alloy composition in the dataset.
    for i in range(len(alloy_list)):
        alloy_comp = alloy_list[i]
        decoded_alloy, decoded_ratio = decode(alloy_comp, element_set)
        ratio_sum = sum(decoded_ratio)
        for j in range(len(decoded_ratio)):
            decoded_ratio[j] = decoded_ratio[j] / ratio_sum
        decoded_alloy_list.append(decoded_alloy)
        decoded_ratio_list.append(decoded_ratio)

    # Create an element list.
    element_list = sorted(list(element_set))

    # Record all the molar ratios for the whole dataset using a numpy array.
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

    # Decode the phase information into an array.
    phase_array = numpy.zeros((n_y, 4))
    for i in range(len(phase_list)):
        if isinstance(phase_list[i], str):
            phases = phase_list[i].split('+')
            for phase in phases:
                if 'FCC' in phase:
                    phase_array[i][0] = 1
                elif 'BCC' in phase:
                    phase_array[i][1] = 1
                elif 'HCP' in phase:
                    phase_array[i][2] = 1
                else:
                    phase_array[i][3] = 1

    # Concatenate the parsed result and the original dataset, write to an excel file.
    ratios_df = pandas.DataFrame(ele_ratio_array, columns=element_list)
    phases_df = pandas.DataFrame(phase_array, columns=['FCC', 'BCC', 'HCP', 'IM'])
    output_df = pandas.concat([phases_df, mech_data.drop([feature[1], feature[9]], axis=1), ratios_df], axis=1)
    output_df.to_excel('parsed_result.xlsx')

