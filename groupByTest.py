import random
import math

def pretty_print_lineage_matrix(lineage_matrix):
    transposed_lineage = [[lineage_matrix[j][i] for j in range(len(lineage_matrix))] for i in range(len(lineage_matrix[0]))]
    for col in transposed_lineage:
        str_array = []
        for tuple in col:
            str_array.append(str(tuple))
        print(' '.join(str_array))

def calculate_theoretical_size(lineage):
    max_numbers = []
    number_of_elements = 0
    for row in lineage:
        if(row):
            max_numbers.append(max(row))
        number_of_elements += len(row)
    max_number = max(max_numbers)
    bit_per_element = int (math.log(max_number, 2)) + 1
    return bit_per_element * number_of_elements

    #print(max_number)


def generateTable(numberOfRows, cardinality):
    ret = []
    contains_all_numbers = False
    while not contains_all_numbers:
        for i in range(numberOfRows):
            ret.append(random.randint(0, cardinality - 1))
        contains_all_numbers = True
        for i in range(cardinality):
            if i not in ret:
                contains_all_numbers = False
        if not contains_all_numbers:
            ret = []
    return ret

if __name__ == "__main__":
    number_of_rows = 10
    cardinality = 5
    table = generateTable(number_of_rows, cardinality)
    table = [0, 0, 1, 1, 1, 0, 1, 0, 0, 1, 3, 3, 1]

    smoke_forward_lineage = []
    smoke_backward_lineage = []

    lineage_matrix = []   # How Smokey?'s representation of lineage
    for i in range(cardinality):
        lineage_matrix.append([])
        smoke_backward_lineage.append([])

    for rid, tuple in enumerate(table):
        smoke_forward_lineage.append([tuple])
        for col_index, col in enumerate(lineage_matrix):
            if col_index is tuple:
                col.append(1)
                smoke_backward_lineage[col_index].append(rid)
            else:
                col.append(0)


    print("Input tuples")
    print(table)
    print
    #calculate_theoretical_size(lineage_matrix)
    print(smoke_forward_lineage)
    forward_lineage_size = calculate_theoretical_size(smoke_forward_lineage)
    print("Smoke forward lineage size: " + str(forward_lineage_size))
    print
    print(smoke_backward_lineage)
    backward_lineage_size = calculate_theoretical_size(smoke_backward_lineage)
    print("Smoke backward lineage size: " + str(backward_lineage_size))
    print
    print("Smoke total lineage size: " + str(forward_lineage_size + backward_lineage_size))
    print


    pretty_print_lineage_matrix(lineage_matrix)
    print("Smokey lineage size: " + str(calculate_theoretical_size(lineage_matrix)))
