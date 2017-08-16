#!/usr/bin/python

# this program is used to split input files into pieces
# and then dispatch them to each host to start their jobs.
# The result will be transferred back to the master host 
# in each node's jobs.

import sys
import os
import config
import subprocess
from multiprocessing import Pool
from util import get_input_file, split_input_file

def transfer(argvs):
    file = argvs[0] 
    i_piece = argvs[1]
    host = "centos_{0}".format(i_piece)
    os.system("scp {0} {1}:cfm_id/inputs/.".format(file, host))
    
def transfer_files(input_file, pieces):
    argvs = []
    for i in range(1, pieces+1):
        file = "{0}_{1}".format(input_file, i)
        argvs.append((file, i))
    p = Pool(pieces)
    p.map(transfer, argvs)
    p.close()
    p.join()

def run_cmd(argvs):
    file = argvs[0]
    i_piece = argvs[1]
    host = "centos_{0}".format(i_piece)
    file = os.path.basename(file)
    cmd = "ssh {0} \"python cfm_id/bin/run_job_each_host.py cfm_id/inputs/{1}\" ".format(host, file)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, \
                        stderr=subprocess.STDOUT, shell=True)
    p.wait()

def run_remote_cmd(input_file, pieces):
    argvs = []
    for i in range(1, pieces+1):
        file = "{0}_{1}".format(input_file, i)
        argvs.append((file, i))
    p = Pool(pieces)
    p.map(run_cmd, argvs)
    p.close()
    p.join()

def send_jobs(input_file, pieces):
    transfer_files(input_file, pieces)
    run_remote_cmd(input_file, pieces)

def main():
    input_file = get_input_file("send_jobs.py")
    pieces = split_input_file(input_file, config.pieces)
    send_jobs(input_file, pieces)
    print "Program exit!"

if __name__ == "__main__":
   main()
 