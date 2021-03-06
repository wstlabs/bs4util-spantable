import os, sys, argparse
from glob import glob
from bs4 import BeautifulSoup
from tests.util import find_files, read_file, extract_test, test_pair
import logging

parser = argparse.ArgumentParser()
parser.add_argument('--prefix',  dest='prefix', default='')
parser.add_argument('--no-skip', dest='noskip', action='store_true')
parser.add_argument('--skip',    dest='noskip', action='store_false')
parser.add_argument('--loud',    dest='loud',   action='store_true')
args = parser.parse_args()

if args.loud:
    _loglevel = logging.DEBUG
else:
    _loglevel = logging.INFO

logging.basicConfig(
    format = "::%(levelname)s %(funcName)s %(message)s",
    level  = _loglevel
    stream = sys.stdout
)
log = logging.getLogger()

skip = not args.noskip
todolist,skiplist = find_files('tests/data',args.prefix,skip)
log.info("that be %d files (%d skipped)." % (len(todolist),len(skiplist)))

for path in todolist:
    log.info("%s .." % path)
    html = read_file(path)
    soup = BeautifulSoup(html)
    frame,spec = extract_test(soup)
    test_pair(frame,spec)

