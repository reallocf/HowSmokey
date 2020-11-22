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


if __name__ == "__main__":
    number_of_rows = 10
    cardinality = 5
    table = generateTable(number_of_rows, cardinality)

    # The example we used in our paper
    table = [1, 1, 2, 2, 2, 1, 2, 1, 1, 2, 4, 4, 1]

    smoke_forward_lineage = []
    smoke_backward_lineage = []

    lineage_matrix = []   # How Smokey?'s representation of lineage
    seen = {}
    output_column_count = 0

    # Generate lineage representations for Smoke
    for rid, tuple in enumerate(table):
        if tuple not in seen:
            seen[tuple] = output_column_count
            smoke_backward_lineage.append([])
            output_column_count += 1
        smoke_forward_lineage.append([seen[tuple]])
        smoke_backward_lineage[seen[tuple]].append(rid)

    # Generate lineage matrix
    for i in range(output_column_count):
        lineage_matrix.append([])

    for rid, tuple in enumerate(table):
        for col_index, col in enumerate(lineage_matrix):
            if col_index is seen[tuple]:
                col.append(1)
            else:
                col.append(0)

    print("Input tuples")
    print(table)
    print
    print("Smoke forward lineage")
    print(smoke_forward_lineage)
    forward_lineage_size = calculate_theoretical_size(smoke_forward_lineage)
    print("Smoke forward lineage size: " + str(forward_lineage_size))
    print
    print("Smoke backward lineage")
    print(smoke_backward_lineage)
    backward_lineage_size = calculate_theoretical_size(smoke_backward_lineage)
    print("Smoke backward lineage size: " + str(backward_lineage_size))
    print
    print("Smoke total lineage size: " + str(forward_lineage_size + backward_lineage_size))
    print

    print("Lineage matrix")
    pretty_print_lineage_matrix(lineage_matrix)
    print("Smokey lineage size: " + str(calculate_theoretical_size(lineage_matrix)))
