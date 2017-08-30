#!/user/bin/python

pieces = 15  # split files into these pieces
pieces_in_each_host = 2 #split input file into these pieces in each host
out_dir = "/home/centos/cfm_id/cfmid/output"  # dir where to store the output of docker image
case_dir = ["positive", "negative", "ei"] # the specific case output dir for each image run
dir_back_to_host = "/mnt/one/results"  # dir of the result file back to master host
timeout = 40 # minutes for time out of docker run
