#!/usr/bin/python

# this program is for running cmfid docker image
# for output. It will use multiprocessing to make
# 2 threads to call cmfid docker image and get results
# cuncurrently until all the jobs done in input file.

import os
import sys
import config
from util import get_args, split_input_file
import re
import subprocess
from multiprocessing import Pool
import time

def jobs(argvs):
    file = argvs[0]
    der_arg = argvs[1]
    done_file = file + ".done"
    done_list = []
    if os.path.isfile(done_file):
        with open(done_file, 'r') as df:
            done_list = df.read().split("\n")
    #done_list = set(done_list)
    if not der_arg:
       case_dir = config.case_dir
       dir_back_to_host = config.dir_back_to_host
       out_dir = config.out_dir       
    else:
       case_dir = config.case_dir_d
       dir_back_to_host = config.dir_back_to_host_d
       out_dir = config.out_dir_d

    with open(file, "r") as f:
        for line in f:
            if not der_arg:
                m = re.search("^(\S*)\t(\S*)", line)
                hmdb_id = m.group(1)
                smile = m.group(2)
            else:
                m = re.search("^(\S*)\t(\S+)\t(\S+)\t(\S+)", line)
                hmdb_id = m.group(1)
                smile = m.group(4)
                deri = m.group(2)
                cnt = m.group(3)
            if hmdb_id in done_list:
                continue
            for c in case_dir:
                if not der_arg:
                    remote_file = "{0}/{1}/{2}*".format(dir_back_to_host, c, hmdb_id)
                else:
                    remote_file = "{0}/{1}/{2}_{3}_{4}*".format(dir_back_to_host, c, \
                                                        hmdb_id, deri, cnt)
                cm1 = "ssh centos_1 \"ls {0}\"".format(remote_file)
                count = 0
                read_out = ''
                while(1):
                    count += 1
                    rp = subprocess.Popen(cm1, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                    rp.wait()
                    read_out = rp.stdout.read()
                    if read_out:
                        break
                    if count == 3:
                        break
                    time.sleep(3)

                if read_out:
                    #print >> sys.stderr, "Bypass " + remote_file
                    continue
                #print >> sys.stderr, "Run " + remote_file
                if c == 'positive':
                    param_file = "/root/param_output0.log"
                    config_file = "/root/param_config.txt"
                elif c == 'negative':
                    param_file = "/root/negative_param_output0.log"
                    config_file = "/root/negative_param_config.txt"
                elif c == 'ei':
                    param_file = "/root/ei_param_output.log"
                    config_file = "/root/ei_param_config.txt"
 
                if not der_arg:
                    out_file = "{0}.log".format(hmdb_id)  
                else:
                    out_file = "{0}_{1}_{2}.log".format(hmdb_id, deri, cnt)              
                cmd = ("docker run --rm=true -v {0}:/root " + ""
                     "-i cfmid:latest sh -c \"cd /root/; cfm-predict " +
                     "'{1}' 0.001 {2} {3} " +
                     "1 /root/{4}/{5}; chmod 777 /root/{4}/{5}\" ").format(out_dir, smile, \
                                            param_file, config_file, c, \
                                            out_file)
                x = config.timeout * 60 
                delay = 3
                timeout = int(x / delay)
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, \
                        stderr=subprocess.STDOUT, shell=True)
                while p.poll() is None and timeout > 0:
                    time.sleep(delay)
                    timeout -= delay
                #p.wait()
                if timeout == 0:
                    p.kill()
                    # the above just kill 'docker run', the below will kill the exec in docker container.
                    cmd = "ps aux|grep '.:.. cfm-'|grep {0}|tr -s ' '|cut -d ' ' -f 2|xargs sudo kill -9 ".format(hmdb_id)
                    p1 = subprocess.Popen(cmd, stdout=subprocess.PIPE, \
                            stderr=subprocess.STDOUT, shell=True)  
                    p1.wait()
                output_file = "{0}/{1}/{2}".format(out_dir, c, out_file)
                file_to_master_host = ''
                # if failed, generate fail file
                if not os.path.isfile(output_file) or os.stat(output_file).st_size == 0:
                    if not der_arg:
                        fail_file = "{0}/{1}/{2}".format(out_dir, c, "{0}.fail".format(hmdb_id))
                    else:
                        fail_file = "{0}/{1}/{2}".format(out_dir, c, "{0}_{1}_{2}.fail".format(hmdb_id, deri, cnt))
                    with open(fail_file, "w") as ff:
                        ff.write(cmd + "\n")
                        if timeout == 0:
                            ff.write("Time out {0} minutes!\n".format(config.timeout))
                        else:
                            ff.write(p.stdout.read() + "\n")
                    file_to_master_host = fail_file
                else:
                    file_to_master_host = output_file
                # transfer back to master host
                cm = "scp {0} centos_1:{1}/{2}/.".format(file_to_master_host, dir_back_to_host, c)
                cn =0
                while(cn <3):
                    p = subprocess.Popen(cm, stdout=subprocess.PIPE, \
                        stderr=subprocess.STDOUT, shell=True)
                    p.wait()
                    cn += 1
                # delete the result file
                os.remove(file_to_master_host)
            #write done file
            if not hmdb_id in done_list:
                with open(done_file, "a") as df:
                    df.write(hmdb_id + "\n")

def run_jobs(input_file, pieces, der_arg):
    argvs = []
    for i in range(1, pieces+1):
        file = "{0}_{1}".format(input_file, i)
        argvs.append((file, der_arg))
    p = Pool(pieces)
    print argvs
    p.map(jobs, argvs)
    p.close()
    p.join()

def main():
    der_arg, input_file = get_args("run_job_each_host.py")
    print "python ../bin/run_job_each_host.py {0} {1}".format(input_file, der_arg)
    pieces = split_input_file(input_file, config.pieces_in_each_host)
    print "Pieces {0}".format(pieces)
    run_jobs(input_file, pieces, der_arg)
    print "Program exit!"

if __name__ == "__main__":
   main()
