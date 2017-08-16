#!/usr/bin/python

# this program is for running cmfid docker image
# for output. It will use multiprocessing to make
# 2 threads to call cmfid docker image and get results
# cuncurrently until all the jobs done in input file.

import os
import sys
import config
from util import get_input_file, split_input_file
import re
import subprocess
from multiprocessing import Pool


def jobs(file):
    with open(file, "r") as f:
        for line in f:
            m = re.search("^(\S*)\t(\S*)", line)
            hmdb_id = m.group(1)
            smile = m.group(2)
            for c in config.case_dir:
                if c == 'positive':
                    param_file = "/root/param_output0.log"
                    config_file = "/root/param_config.txt"
                elif c == 'negative':
                    param_file = "/root/negative_param_output0.log"
                    config_file = "/root/negative_param_config.txt"
                elif c == 'ei':
                    param_file = "/root/ei_param_output.log"
                    config_file = "/root/ei_param_config.txt"
                cmd = ("docker run -v {0}:/root " + ""
                     "-i cfmid:latest sh -c \"cd /root/; cfm-predict " +
                     "'{1}' 0.001 {2} {3} " +
                     "1 /root/{4}/{5}; chmod 777 /root/{4}/{5}\" ").format(config.out_dir, smile, \
                                            param_file, config_file, c, \
                                            "{0}.out".format(hmdb_id))
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, \
                        stderr=subprocess.STDOUT, shell=True)
                p.wait()
                output_file = "{0}/{1}/{2}".format(config.out_dir, c, "{0}.out".format(hmdb_id))
                file_to_master_host = ''
                # if failed, generate fail file
                if not os.path.isfile(output_file) or os.stat(output_file).st_size == 0:
                    fail_file = "{0}/{1}/{2}".format(config.out_dir, c, "{0}.fail".format(hmdb_id))
                    with open(fail_file, "w") as ff:
                        ff.write(cmd + "\n")
                        ff.write(p.stdout.read() + "\n")
                    file_to_master_host = fail_file
                else:
                    file_to_master_host = output_file
                # transfer back to master host
                cm = "scp {0} centos_1:{1}/{2}/.".format(file_to_master_host, config.dir_back_to_host, c)
                p = subprocess.Popen(cm, stdout=subprocess.PIPE, \
                        stderr=subprocess.STDOUT, shell=True)
                p.wait()
                # delete the result file
                os.remove(file_to_master_host)


def run_jobs(input_file, pieces):
    argvs = []
    for i in range(1, pieces+1):
        file = "{0}_{1}".format(input_file, i)
        argvs.append(file)
    p = Pool(pieces)
    p.map(jobs, argvs)
    p.close()
    p.join()

def main():
    input_file = get_input_file("run_job_each_host.py")
    pieces = split_input_file(input_file, config.pieces_in_each_host)
    run_jobs(input_file, pieces)
    print "Program exit!"

if __name__ == "__main__":
   main()