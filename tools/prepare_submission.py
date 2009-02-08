#!/usr/bin/env python

from mstutil import die, get_path_to_project_root, get_path_to_tools_root
from shutil import copy2, copytree, move
from time import strftime
import os, sys

def sh_or_die(cmd, msg):
    if os.system(cmd) != 0:
        die(cmd + ' failed: ' + msg)

root = get_path_to_project_root()
submit = root + 'submit/'
sh_or_die('rm -rf ' + submit, 'could not remove the old submit dir: %s' % submit)

# build the binaries
src = root + 'src/'
srcmst = src + 'mst'
sh_or_die('make -C %s && test -f %s' % (src, srcmst), 'unable to build the binaries')
copy2(srcmst, root + 'mst')
sh_or_die('make -C %s clean' % src, 'unable to cleanup the build byproducts')

# copy in the source and make files
copytree(src, submit)
move(root + 'mst', submit + 'mst')

# build the report
writeup = root + 'writeup/'
report = writeup + 'report.pdf'
sh_or_die('make -C %s && test -f %s' % (writeup, report), 'unable to build the report')

# copy in the report
copy2(report, submit + 'report.pdf')

# copy in the required binary 'random' and its dependencies
tools = root + 'tools/'
random = 'random'
run_test = 'run_test.py'
gen_input = 'generate_input.py'
mstutil = 'mstutil.py'
copy2(tools + random, submit + random)
copy2(tools + run_test, submit + run_test)
copy2(tools + gen_input, submit + gen_input)
copy2(tools + mstutil, submit + mstutil)

# hack up run_test.py a bit so we don't have to include its usual dependency
rt = submit + run_test
cmd = "fgrep -v 'exclude-from-submit' %s | sed -e 's/# include-with-submit //g' > /tmp/dgu-ps && mv /tmp/dgu-ps %s && chmod +x %s" % (rt, rt, rt)
sh_or_die(cmd, 'could not simplify run_test.py for submission')

# copy in the readme
copy2(root + 'readme.txt', submit + 'readme.txt')

print ('***************************\n' + \
       'Done staging the submission on %s.  Please do a MANUAL CHECK to make sure BOTH ' + \
       'mst and random work, and that the required files are indeed in place and look ' + \
       'correct.') % strftime('%A %Y-%b-%d at %H:%M:%S')
