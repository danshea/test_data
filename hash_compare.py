#!/usr/bin/env python

'''
Author: djs
Date: 2012-09-12
Description: Compare files on the back end of the glusterfs cluster and ensure the sha256 sums match.
'''

import datetime
import os
import os.path
import shlex
import subprocess
import sys

def timestamp():
    return str(datetime.datetime.today())

def runcmd(cmd):
    print '{0:s}: {1:s}: invoked'.format(timestamp(), cmd)
    args = shlex.split(cmd)
    out,err = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    print '{0:s}: {1:s}: stdout {2:s}'.format(timestamp(), cmd, out)
    print '{0:s}: {1:s}: stderr {2:s}'.format(timestamp(), cmd, err)
    return (out,err)

def main(myname, spath1, spath2):
    # parse the spath
    server1, path1 = spath1.split(':')
    server2, path2 = spath2.split(':')
    # compare sha256 values between machines
    cmd1 = 'ssh {0:s} \'for file in {1:s};do echo $file $(cat $file);done\''.format(server1, os.path.join(path1,'*.sha256'))
    cmd2 = 'ssh {0:s} \'for file in {1:s};do echo $file $(cat $file);done\''.format(server2, os.path.join(path2,'*.sha256'))
    files1, err1 = runcmd(cmd1)
    files2, err2 = runcmd(cmd2)
    mismatch_count = 0
    for a, b in zip(sorted(files1), sorted(files2)):
        if a != b:
            print '{0:s}: SHA256 mismatch'.format(timestamp())
            print '{0:s}: {1:s} {2:s}'.format(timestamp(), a, b)
            mismatch_count += 1
    if mismatch_count != 0:
        print '{0:s}: SHA256 mismatch count: {1:d}'.format(timestamp(), mismatch_count)
    else:
        print '{0:s}: No mismatches found.'.format(timestamp())
    sys.exit(0)

def usage():
    print 'usage: {0:s} server1:/path/to/files server2:/path/to/files '.format(sys.argv[0]) 
    sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        usage()
    else:
        main(sys.argv[0], sys.argv[1], sys.argv[2])
