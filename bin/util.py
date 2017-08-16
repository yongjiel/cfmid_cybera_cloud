#!/usr/bin/pytion
import sys
import os

def get_input_file(program):
    if len(sys.argv) == 1:
        print "Usage: python {0} <input_file>".format(program)
        sys.exit(1)
    input_file = sys.argv[1]
    if not os.path.isfile(input_file):
        print "Error: Input file not exist"
        sys.exit(1)
    return input_file

def split_input_file(input_file, default_pieces):
    line_count = count(input_file);
    pieces = get_pieces(line_count, default_pieces)
    split_into_pieces(input_file, pieces)
    return pieces

def count(input_file):
    count = 0
    with open(input_file, "r") as f:
        for i in f:
            count += 1
    return count

def get_pieces(line_count, default_pieces):
    if line_count / default_pieces > 0:
        pieces =  default_pieces
    else:
        pieces = line_count
    return pieces

def split_into_pieces(input_file, pieces):
    count = 0;
    with open(input_file, "r") as f:
        for line in f:
            count += 1
            file_suffix = count % pieces
            if file_suffix == 0:
                file_suffix = pieces
            o_file = "{0}_{1}".format(input_file, file_suffix)
            fo = open(o_file, 'a')
            fo.write(line)
            fo.close()
    print "Splitting files done!"
