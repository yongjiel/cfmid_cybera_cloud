#!/user/bin/python

pieces = 15  # split files into these pieces
pieces_in_each_host = 2 #split input file into these pieces in each host
out_dir = "/home/centos/cfm_id/cfmid/output"  # dir where to store the output of docker image
case_dir = ["positive", "negative", "ei"] # the specific case output dirs for each image run. If you do not want some of them, just change this list.
dir_back_to_host = "/mnt/one/results"  # dir of the result file back to master host
timeout = 40 # minutes for time out of docker run
###
###If call the program with -d arg, the below vars will be used instead of upper vars.
###
case_dir_d = ["positive", "negative", "ei"] # the specific case output dirs for each image run. If you do not want some of them, just change this list. for derivatives.
dir_back_to_host_d = "/mnt/one/results_d"  # dir of the result file back to master host. for derivatives.
out_dir_d = "/home/centos/cfm_id/cfmid/output_d"  # dir where to store the output of docker image, for derivatives.
