import filecmp
import csv
import os
from collections import defaultdict

SPECS = defaultdict()  # dictionary with key of the file names containing defined design pattern specifications
INSTANCES = defaultdict()  # dictionary with key of file name for identified/implemented design patterns


def generate_data():
    """
    Generate a csv of edit distances for files found
    in the directory via the find_files function
    """

    # grab files in directory
    find_files()

    # separate the names from the specs and instances for creating the CSV
    spec_names = [['MATRIX']]  # list of pattern specs
    instances_names = []  # list of instance_names
    results = defaultdict(list)
    for key, values in SPECS.items():
        spec_names.append(key)
    for key, values in INSTANCES.items():
        instances_names.append(key)

    # calculate the scores
    for spec, spec_file in SPECS.items():
        spec_file = open(SPECS.get(spec), 'r')   # open Spec file
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
    operations: Add, Delete, Indent
    """
    m = len(lines1) - 1  # number of lines in file1
    n = len(lines2) - 1  # number of lines in file2

    # base cases - no more lines to compare in the files
    if m == 0:
        return n
    if n == 0:
        return m

    # indices to loop through the input
    index1 = 0
    index2 = 0

    # if lines are equivalent, move to next line, and keep going until they are not
    if lines1[index1] == lines2[index2]:
        while lines1[index1] == lines2[index2]:
            index1 += 1
            index2 += 1

    #  we will skip indented lines (which indicates conditionals) for now
    if lines1[index1].startswith('\t'):
        while lines1[index1].startswith('\t'):
            index1 += 1
            if index1 == m:  # we've reached the end
                break
    if lines2[index2].startswith('\t'):
        while lines2[index2].startswith('\t'):
            index2 += 1
            if index2 == n:  # we've reached the end
                break

    # recursive cases
    add = edit_distance(lines1[index1:m], lines2[index2+1:n]) + 1
    delete = edit_distance(lines1[index1+1:m], lines2[index2:n]) + 1

    # return the minimum distance
    return min([add, delete])


def find_files():
    """
    Get files in project directory, add the spec files to the SPEC dictionary keyed off of the file names
    and add the instance files to the INSTANCES dictionary keyed off of the file name.

    This function will only add files that end with .txt to dictionaries, we want to ignore
    any python or project files in the same directory
    """

    # path, parent dir(?), filename w/ extension
    for path, dirnames, filenames in os.walk('.'):
        for file in filenames:

            filename, file_extension = os.path.splitext(file)
            extended_filename = str(path) + "-" + filename

            #  only add the text files to dictionary - note the funny notation/approach is
            #  to make formatting the csv easier
            if file_extension == ".txt":
                if filename.endswith("_spec"):
                    SPECS[str(filename)] = path + "\\" + file
                    #  SPECS[str(fileName)].append(fileName)
                else:
                    INSTANCES[str(extended_filename)] = path + "\\" + file
                    #  INSTANCES[str(extended_filename)].append(extended_filename)

        print_dict(INSTANCES)
        print_dict(SPECS)

def print_dict(dictionary):
    """
    For testing purposes, it's helpful to be able to print a dictionary (defaultdict)
    to see what values are being stored as keys and their values
    """

    for key, item in dictionary.items():
        print("===================Key:" + key)
        print(item)


# def file_len(fname):
#     with open(fname) as f:
#         for i, l in enumerate(f):
#             pass
#     return i + 1

# go and generate the results
generate_data()
