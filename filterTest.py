import random
import math
import sys

rid_size = 64


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
    return rid_size * number_of_elements, bit_per_element * number_of_elements


def generateTable(number_or_rows, cardinality):
    ret = []
    contains_all_numbers = False
    while not contains_all_numbers:
        for i in range(number_or_rows):
            ret.append(random.randint(0, cardinality - 1))
        contains_all_numbers = True
        for i in range(cardinality):
            if i not in ret:
                contains_all_numbers = False
        if not contains_all_numbers:
            ret = []
    return ret

def filterCondition(value):
    # Alter filter condition here!
    if value < 10:
        return True
    else:
        return False


if __name__ == "__main__":
    number_of_rows = 10
    cardinality = 5
    table = generateTable(int(sys.argv[1]), int(sys.argv[2]))

    # The example we used in our paper
    # table = [1, 1, 2, 2, 2, 1, 2, 1, 1, 2, 4, 4, 1]

    smoke_forward_lineage = []
    smoke_backward_lineage = []

    lineage_matrix = []   # How Smokey?'s representation of lineage
    output_column_count = 0

    # Generate lineage representations for Smoke
    for rid, tuple in enumerate(table):
        if filterCondition(tuple):
            smoke_forward_lineage.append(output_column_count)
            output_column_count = output_column_count + 1
            smoke_backward_lineage.append(rid)

    for rid, tuple in enumerate(table):
        if filterCondition(tuple):
            lineage_matrix.append([])
            for row_num in range(len(table)):
                if row_num is rid:
                    lineage_matrix[-1].append(1)
                else:
                    lineage_matrix[-1].append(0)

    print_matrix = False

    print("Input tuples")
    print(table)
    print
    print("Smoke forward lineage")
    if print_matrix:
        print(smoke_forward_lineage)
    forward_lineage_size = calculate_theoretical_size([smoke_forward_lineage])
    print("Smoke forward lineage size: " + str(forward_lineage_size[0]))
    print("Bitpacked Smoke forward lineage size: " + str(forward_lineage_size[1]))
    print
    print("Smoke backward lineage")
    if print_matrix:
        print(smoke_backward_lineage)
    backward_lineage_size = calculate_theoretical_size([smoke_backward_lineage])
    print("Smoke backward lineage size: " + str(backward_lineage_size[0]))
    print("Bitpacked Smoke backward lineage size: " + str(backward_lineage_size[1]))
    print
    print("Smoke total lineage size: " + str(forward_lineage_size[0] + backward_lineage_size[0]))
    print("Bitpacked Smoke total lineage size: " + str(forward_lineage_size[1] + backward_lineage_size[1]))
    print

    print("Lineage matrix")
    if print_matrix:
        pretty_print_lineage_matrix(lineage_matrix)
    print("Smokey lineage size: " + str(calculate_theoretical_size(lineage_matrix)[1]))
