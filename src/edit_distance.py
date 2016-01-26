import filecmp
import csv
import os
import math
from collections import defaultdict

SPECS = defaultdict()   # dictionary with key of spec file names, values of spec files
INSTANCES = defaultdict()  # dictionary with key of instance file names, values of instance files
centroids = defaultdict(list)
results = defaultdict(list)
spec_list = []


def generate_data():
    """
    Generate a csv of edit distances for files found
    in the directory via the find_files function
    """

    #  grab files in directory
    find_files()

    #  separate the names from the specs and instances for creating the CSV
    spec_names = [['MATRIX']]   # list of pattern specs
    instances_names = []   # list of instance_names
    for key, values in SPECS.items():
        spec_names.append(key)
    for key, values in INSTANCES.items():
        instances_names.append(key)

    # calculate the scores
    for spec, spec_file in SPECS.items():
        spec_file = open(SPECS.get(spec), 'r')  # open Spec file
        spec_lines = spec_file.readlines()  # break down spec file into list of lines
        for instance, instance_file in INSTANCES.items():
            instance_file = open(INSTANCES.get(instance), 'r')  # open instance file
            instance_lines = instance_file.readlines()  # break down into list of lines

            score = edit_distance(spec_lines, instance_lines)
            print("====SCORE: "+str(score))
            results[instance].append(score)

    # populate proximity_matrix csv with edit_distance scores
    score_writer = csv.writer(open('proximity_matrix.csv', 'at', encoding='utf8'))

    # header
    score_writer.writerow(spec_names)
    # write rows of scores
    for instance, scores in results.items():
        temp_list = [instance]+scores
        score_writer.writerow(temp_list)


def edit_distance(lines1, lines2):
    """
    Given two files, return the distance between the two
    Operations: Add, Delete, Indent
    """

    m = len(lines1)
    n = len(lines2)

    index1 = 0
    index2 = 0

    # base cases
    if lines1 == lines2:   # the lines are equivalent between files
        return 0
    if m == 0:   # no more elements in lines1
        return n
    if n == 0:   # no more elements in lines2
        return m

    # if lines are equivalent, move to next set of lines
    if lines1[index1] == lines2[index2]:
        while lines1[index1] == lines2[index2]:
            index1 += 1
            index2 += 1

            # I added the following to cover cases where lines1=lines2
            # We were getting an array index oob
            if index1 + 1 == m:
                break
            if index2 + 1 == n:
                break

    #  we will skip indented lines (which indicates conditionals) for now
    if lines1[index1].startswith('\t'):
        while lines1[index1].startswith('\t'):
            index1 += 1
            if index1 == m:   # we've reached the end
                break
    if lines2[index2].startswith('\t'):
        while lines2[index2].startswith('\t'):
            index2 += 1
            if index2 == n:   # we've reached the end
                break

    # recursive cases
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
    For testing purposes, it's helpful to be able to print a dictionary (defaultdict)
    to see what values are being stored as keys and their values
    """
    for key, item in dictionary.items():
        print("===================Key:" + key)
        print(item)


def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1


def generate_centroids():
    for spec, spec_file in SPECS.items():
        spec_file = open(SPECS.get(spec), 'r')   # open Spec file
        spec_lines = spec_file.readlines()   # break down spec file into list of lines
        for spec_find, spec_file_find in SPECS.items():
            spec_file_find = open(SPECS.get(spec_find), 'r')   # open Spec file
            spec_lines_find = spec_file_find.readlines()   # break down spec file into list of lines
            spec_diff = edit_distance(spec_lines, spec_lines_find)
            short_pattern = str(spec_find).replace("_spec", "")
            centroids[short_pattern].append(spec_diff)
    # populate proximity_matrix csv with edit_distance scores
    centroid_writer = csv.writer(open('proximity_matrix_specs.csv', 'at', encoding='utf8'))
    for spec_find, spec_diff in centroids.items():
        temp_list = [spec_find] + spec_diff
        centroid_writer.writerow(temp_list)


def get_distances():
    rq1 = defaultdict(list)
    for i in range(len(centroids.keys())):
        spec_list.append("temp")

    for key in centroids.keys():
        placement = 0
        for dist in centroids[key]:
            if dist == 0:
                spec_list[placement] = key
            else:
                placement += 1

    # Provides output for RQ1
    for key in results:
        pattern_instance = key.rsplit("-")[0][2:]
        spot = -1
        for i in range(len(spec_list)):
            if pattern_instance == spec_list[i]:
                spot = i

        rq1[key].append(0)  # expected difference
        rq1[key].append(results[key][spot])  # actual difference
        print(rq1[key])

    # Provides output for RQ2
    rq2 = defaultdict(list)
    for key in results:
        pattern_instance = key.rsplit("-")[0][2:]
        rq2[pattern_instance].append(euclidean_dist(centroids[pattern_instance], results[key]))

    print(rq2)

    writer3 = open('prox.out', 'w')

    for key in results.keys():
        writer3.write('%s ' % key)
        for value in results[key]:
            writer3.write('& %s ' % value)
        writer3.write('\\\\ \\hline\n')
    for key in centroids.keys():
        writer3.write('%s ' % key)
        for value in centroids[key]:
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
