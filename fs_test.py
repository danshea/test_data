#!/usr/bin/env python
'''
Author: djs
Date: 2012-09-14
Description: Generate an I/O workload on a filesystem and perform some
rudimentary calculations as to the performance of the system.
'''

import ConfigParser
import datetime
import hashlib
import os
import os.path
import random
import sys

def usage():
    print 'usage: {0:s} cfgfile'.format(sys.argv[0])
    sys.exit(1)

# read in global configuration
if len(sys.argv) != 2:
    usage()
else:
    cfgfile=sys.argv[1]
    cfg=ConfigParser.ConfigParser()
    cfg.read(cfgfile)
    srcdir   = cfg.get('GLOBAL','source_directory')
    dstdir   = cfg.get('GLOBAL','destination_directory')
    logfile  = cfg.get('GLOBAL','logfile')
    numfiles = int(cfg.get('GLOBAL','numfiles'))
    numruns  = int(cfg.get('GLOBAL','numruns'))
    outfilename = cfg.get('GLOBAL','outfilename')
    outfilesize = int(cfg.get('GLOBAL','outfilesize'))
    
def timestamp():
    return str(datetime.datetime.now())
    
def log(msg, stdout=logfile):
    with open(logfile, 'a') as fh:
        fh.write('{0:s}: {1:s}\n'.format(timestamp(),msg))

def create(filename, size, buffsz=1024):
    with open(filename, 'w') as fh:
        for i in xrange(size/buffsz):
            buff = list()
            for j in xrange(buffsz):
                buff.append(chr(random.randint(65,90)))
            fh.write(''.join(buff))
    log('INFO: {0:s} created.'.format(filename))

def copy(src, dst, buffsz=1024):
    with open(src, 'r') as fsrc:
        with open(dst, 'w') as fdst:
            buff = fsrc.read(buffsz)
            while buff:
                fdst.write(buff)
                buff = fsrc.read(buffsz)
    log('INFO: {0:s} copied to {1:s}'.format(src, dst))

def sha256(filename, buffsz=1024):
    with open(filename, 'r') as fh:
        buff = fh.read(buffsz)
        sha = hashlib.sha256()
        while buff:
            sha.update(buff)
            buff = fh.read(buffsz)
    digest = sha.hexdigest()
    log('INFO: {0:s}: {1:s}'.format(filename, digest))
    return digest

def run(filename, size=1024):
    fullsrcpath = os.path.join(srcdir, filename)
    create(fullsrcpath, size)
    sha256_src = sha256(fullsrcpath)
    fulldstpath = os.path.join(dstdir, filename)
    copy(fullsrcpath, fulldstpath)
    sha256_dst = sha256(fulldstpath)
    if sha256_src != sha256_dst:
        log('ERROR: sha256 mismatch')
        log('ERROR: src: {0:s}'.format(sha256_src))
        log('ERROR: dst: {0:s}'.format(sha256_dst))

def main():
    for i in xrange(numruns):
        for j in xrange(numfiles):
            # zero-padded filename based on the outfilename prefix defined in the cfg
            filename = outfilename+('{0:0'+str(len(str(numfiles)))+'d}').format(j)
            run(filename, outfilesize)
    log('INFO: Completed {0:d} runs. {1:d} files per run. {2:d} total files created.'.format(numruns, numfiles, numruns*numfiles))
    log('INFO: Total I/O {0:d} bytes'.format(numruns*numfiles*outfilesize))
    sys.exit(0)

if __name__ == '__main__':
    main()