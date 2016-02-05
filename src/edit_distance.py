import csv
import os
import math
from collections import defaultdict

SPECS = defaultdict()  # defined design pattern specifications
INSTANCES = defaultdict()  # identified/implemented design patterns
CENTROIDS = defaultdict(list)  # distances between specifications
RESULTS = defaultdict(list)  #matrix of distances
SPEC_LIST = []


def generate_data():
    """
    Generate a csv of edit distances for files found
    in the directory via the find_files function
    """

    #  grab files and populate SPECS, INSTANCES dictionary
    find_files()

    #  separate the names from the specs and instances for creating the CSV
    spec_names = [['MATRIX']]
    instances_names = []
    for key, values in SPECS.items():
        spec_names.append(key)
    for key, values in INSTANCES.items():
        instances_names.append(key)

    # calculate the scores
    for spec, spec_file in SPECS.items():
        spec_file = open(SPECS.get(spec), 'r')
        # break down into list of lines (as required for calculation functions)
        spec_lines = spec_file.readlines()

        for instance, instance_file in INSTANCES.items():
            instance_file = open(INSTANCES.get(instance), 'r')
            instance_lines = instance_file.readlines()

            score = edit_distance(spec_lines, instance_lines)
            RESULTS[instance].append(score)

    # populate proximity_matrix csv with edit_distance scores
    score_writer = csv.writer(open('proximity_matrix.csv', 'at', encoding='utf8'))

    # header
    score_writer.writerow(spec_names)
    # write rows of scores
    for instance, scores in RESULTS.items():
        temp_list = [instance] + scores
        score_writer.writerow(temp_list)


def edit_distance(lines1, lines2):
    """
    :param lines1: first file for comparison, represented as an array of strings
    :param lines2: second file for comparison, represented as an array of strings

    Given two files, lines1 and lines2,
    return the distance between the two
    Operations: Add, Delete, Indent
    """

    m = len(lines1)
    n = len(lines2)

    index1 = 0
    index2 = 0

    # base cases
    if lines1 == lines2:
        return 0
    if m == 0:
        return n
    if n == 0:
        return m

    # if lines are equivalent, move to next set of lines
    if lines1[index1] == lines2[index2]:
        while lines1[index1] == lines2[index2]:
            index1 += 1
            index2 += 1

            if index1 + 1 == m:
                break
            if index2 + 1 == n:
                break

    #  TODO: add handling for indents/conditionals, skip for now
    if lines1[index1].startswith('\t'):
        while lines1[index1].startswith('\t'):
            index1 += 1
            if index1 == m:
                break
    if lines2[index2].startswith('\t'):
        while lines2[index2].startswith('\t'):
            index2 += 1
            if index2 == n:
                break

    # all power to the recursion
    add = edit_distance(lines1[index1:m], lines2[index2+1:n]) + 1
    delete = edit_distance(lines1[index1+1:m], lines2[index2:n]) + 1

    return min([add, delete])


def find_files():
    """
    Get files in project directory, add the spec files to the SPEC dictionary keyed off of the file names
    and add the instance files to the INSTANCES dictionary keyed off of the file name.

    This function will only add files that end with .txt to dictionaries, we want to ignore
    any python or project files in the same directory
    """

    # path, parent dir(?), file_name w/ extension
    for path, dirnames, file_names in os.walk('.'):
        print(path)
        for file in file_names:

            file_name, file_extension = os.path.splitext(file)
            extended_file_name = str(path) + "-" + file_name

            # only add the text files to dictionary - note the funny notation/approach is
            # to make formatting the csv easier
            if file_extension == ".txt":
                if file_name.endswith("_spec"):
                    SPECS[str(file_name)] = path + "\\" + file
                else:
                    INSTANCES[str(extended_file_name)] = path + "\\"+file


def print_dict(dictionary):
    """
    :param dictionary: a dictionary to be printed out

    Helper Function for testing purposes, it's helpful to be able to print a dictionary (defaultdict)
    to see what values are being stored as keys and their values
    """
    for key, item in dictionary.items():
        print("===================Key:" + key)
        print(item)


def generate_centroids():
    """
    Sets up the design pattern specifications as the centroids

    There is a lot of duplicated calculations in this method. Needs
    refactoring.
    """
    for spec, spec_file in SPECS.items():
        spec_file = open(SPECS.get(spec), 'r')
        spec_lines = spec_file.readlines()

        for spec_find, spec_file_find in SPECS.items():
            spec_file_find = open(SPECS.get(spec_find), 'r')   # open Spec file
            spec_lines_find = spec_file_find.readlines()   # break down spec file into list of lines

            # get the difference between the specks (?)
            spec_diff = edit_distance(spec_lines, spec_lines_find)

            # remove the "_spec" at the end of the pattern name
            short_pattern = str(spec_find).replace("_spec", "")

            # distance between pattern text-book definitions
            CENTROIDS[short_pattern].append(spec_diff)

    # populate proximity_matrix csv with edit_distance scores
    centroid_writer = csv.writer(open('proximity_matrix_specs.csv', 'at', encoding='utf8'))
    for spec_find, spec_diff in CENTROIDS.items():
        temp_list = [spec_find] + spec_diff
        centroid_writer.writerow(temp_list)


def get_distances():
    rq1 = defaultdict(list)
    for i in range(len(CENTROIDS)):
        SPEC_LIST.append("temp")

    for key in CENTROIDS.keys():
        placement = 0
        for dist in CENTROIDS[key]:
            if dist == 0:
                SPEC_LIST[placement] = key
            else:
                placement += 1

    # Provides output for RQ1 (Research Question 1)
    for key in RESULTS:
        pattern_instance = key.rsplit("-")[0][2:]
        spot = -1
        for i in range(len(SPEC_LIST)):
            if pattern_instance == SPEC_LIST[i]:
                spot = i

        rq1[key].append(0)  # expected difference
        rq1[key].append(RESULTS[key][spot])  # actual difference
        print(rq1[key])

    # Provides output for RQ2 (Research Question 2)
    rq2 = defaultdict(list)
    for key in RESULTS:
        pattern_instance = key.rsplit("-")[0][2:]
        rq2[pattern_instance].append(euclidean_dist(CENTROIDS[pattern_instance], RESULTS[key]))

    print(rq2)

    writer3 = open('prox.out', 'w')

    for key in RESULTS.keys():
        writer3.write('%s ' % key)
        for value in RESULTS[key]:
            writer3.write('& %s ' % value)
        writer3.write('\\\\ \\hline\n')
    for key in CENTROIDS.keys():
        writer3.write('%s ' % key)
        for value in CENTROIDS[key]:
            writer3.write('& %s ' % value)
        writer3.write('\\\\ \\hline\n')


def euclidean_dist(expected_list, actual_list):
    if len(expected_list) != len(actual_list):
        print("euclidean distance error")
    running_sum = 0
    for i in range(len(expected_list)):
        running_sum += (math.pow(expected_list[i] - actual_list[i], 2))

    return round(math.sqrt(running_sum), 4)

generate_data()
generate_centroids()
get_distances()