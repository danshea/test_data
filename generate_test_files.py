#!/usr/bin/env python

import datetime
import hashlib
import os
import os.path
import random
import sys
import time

def timestamp():
    return str(datetime.datetime.today())

def genfile(filename, size):
    '''
    genfile(filename, size): create a file of randomized data of size in bytes
    '''
    with open(filename, 'w') as fh:
        for i in xrange(size):
            fh.write(chr(random.randint(97,122)))

    print '{0:s}: {1:s} created.'.format(timestamp(), filename)

def sha256(filename):
    '''
    sha256(filename): compute sha256 of filename and store the result in filename.sha256
    '''
    with open(filename, 'r') as fh:
        stat  = os.stat(filename)
        # since our files are going to be 1GB in size let's just break each file into 10 parts
        parts = 10 
        size  = stat.st_size
        chunk = size / parts
        buf   = fh.read(chunk)
        csum  = hashlib.sha256()
        while buf:
            csum.update(buf)
            buf = fh.read(chunk)
        digest = csum.hexdigest()
        
        with open(filename+'.sha256', 'w') as outfile:
            outfile.write(digest)
        
        print '{0:s}: {1:s}: {2:s}'.format(timestamp(), filename, digest)

def main(myname, numfiles, outputdir):
    # Set my $CWD as /mnt/test
    os.chdir(outputdir)
    # Define some sizes for the files to be created (1kB, 1MB, 1GB)
    sizes = [1024, 1048576, 1073741824]
    #sizes = [1024]
    # Create 100 files on the glusterfs cluster
    for i in xrange(numfiles):
        # create a zero padded number and append that to myname to create output filename
        filename = (myname+'{0:0'+str(len(str(numfiles)))+'d}').format(i)
        # select a file size to be created and generate a file of that size
        genfile(filename, random.choice(sizes))
        # calculate the sha256
        sha256(filename)
    print '{0:s}: Generated {1:d} files, exiting.'.format(timestamp(), numfiles)
    sys.exit(0)
    
def usage():
    print 'usage: {0:s} filename_prefix numfiles outputdir'.format(sys.argv[0])
    print 'filename_prefix is the prefix to prepend to files generated.'
    print 'numfiles is the number of files to create.'
    print 'outputdir is the directory where the files should be placed.'
    sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) != 4:
        usage()
    else:
        main(sys.argv[1], int(sys.argv[2]), sys.argv[3])
