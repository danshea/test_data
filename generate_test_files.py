#!/usr/bin/env python

import hashlib
import os
import random
import sys

def genfile(filename, size):
    '''
    genfile(filename, size): create a file of randomized data of size in bytes
    '''
    with open(filename, 'w') as fh:
        for i in xrange(size):
            fh.write(chr(random.randint(97,122)))

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
        digest = csum.digest()
        
        with open(filename+'.sha256', 'w') as outfile:
            outfile.write(digest)

def main():
    num_files = 250
    file_size = 1073741824
    for i in xrange(num_files):
        filename = 'file' + str(i)
        genfile(filename, file_size)
        sha256(filename)
        sys.stdout.write('#')
    sys.stdout.write('Done!\n')
    sys.exit(0)

if __name__ == '__main__':
    main()