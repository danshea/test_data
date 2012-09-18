#!/usr/bin/env python

'''
Author: djs
Date: 2012-09-13
Description: 4C's - Create a file, Check the sha-256, Copy it to glusterfs, Compare the sha-256
'''

import datetime
import os
import os.path
import shlex
import subprocess
import sys

def timestamp():
    return str(datetime.datetime.today())

def runcmd(cmd, stdin=None, stdout=None, stderr=None):
    print '{0:s}: {1:s}: invoked'.format(timestamp(), cmd)
    args = shlex.split(cmd)
    out,err = subprocess.Popen(args, stdin=stdin, stdout=stdout, stderr=stderr).communicate()
    print '{0:s}: {1:s}: stdout {2:s}'.format(timestamp(), cmd, out)
    print '{0:s}: {1:s}: stderr {2:s}'.format(timestamp(), cmd, err)
    return (out,err)

def usage():
    print 'USAGE: {0:s} filename num_runs bs count'.format(sys.argv[0])
    print '       filename is the name of the file to create'
    print '       num_runs is the number of runs to perform'
    print '       bs is the block size in bytes dd will use to write the file'
    print '       count is the number of blocks of size bs that dd will write'
    print 'EXAMPLE:'
    print '       {0:s} out.txt 100 1024 10 > logfile.log'.format(sys.argv[0])
    print '       This creates a file out.txt of size 10kB and runs the sha256'
    print '       check against a copy to the glusterfs.  It will perform this'
    print '       100 times and the output will be logged to logfile.log'
    sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) != 5:
        usage()
    infile = '/dev/zero'
    bs = sys.argv[3]
    size = sys.argv[4]
    mismatch_count = 0
    for i in xrange(int(sys.argv[2])):
        # Create a file
        outfile = os.path.join('/home/system/test_data',sys.argv[1])
        runcmd('dd if={0:s} of={1:s} bs={2:s} count={3:s}'.format(infile,outfile,bs,size), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # Check the sha-256
        with open(outfile, 'r') as fh:
            hash1,err = runcmd('sha256 -q -x', stdin=fh, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # Copy it to the glusterfs
        src = outfile
        dst = os.path.join('/mnt/test',sys.argv[1])
        runcmd('cp {0:s} {1:s}'.format(src,dst), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # Compare the hashes
        with open(dst, 'r') as fh:
            hash2,err = runcmd('sha256 -q -x', stdin=fh, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if hash1 != hash2:
            mismatch_count += 1
            print '{0:s}: SHA-256 mismatch detected.  Mismatch count: {1:d}'.format(timestamp(), mismatch_count)
        print '{0:s}: {1:d} files moved. {2:d} errors. Error Rate: {3:0.2f}'.format(timestamp(), i+1, mismatch_count, (mismatch_count/float(i+1))*100)
    print '{0:s}: Run Complete.'.format(timestamp())
