import simplejson as json
from glob import glob
from bs4util.spantable import parse_table, frame_keys, describe_frame
from collections import OrderedDict 
from itertools import chain
from copy import deepcopy
import logging

log = logging.getLogger()

def show_log():
    print("log = %s" % log)
    log.info("info! %s" % __name__)
    log.debug("debug! %s" % __name__)

def find_files(dirpath,prefix,skip=True):
    '''Finds files to test in a given directory.'''
    paths = sorted(glob("%s/%s*.html" % (dirpath,prefix)))
    if (skip):
        todolist = [p for p in paths if 'SKIP' not in p]
        skiplist = [p for p in paths if 'SKIP' in p]
        return todolist,skiplist
    else:
        return paths,[]

def read_file(path):
    with open(path,"rt") as f:
        return "\n".join(f.readlines())

def load_spec(block):
    '''Loads an (ordered) spec dict from a raw JSON string.'''
    d = json.loads(block)
    allkeys = frame_keys() 
    spec = OrderedDict((k,d[k]) for k in allkeys if k in d)
    # We ast the dims member as a tuple, if present, to make it compatible 
    # to the .dims attribute in STDF objects. 
    if 'dims' in spec:
        spec['dims'] = tuple(spec['dims'])
    return spec

def describe_spec(spec):
    for key in spec.keys():
        if key == 'dims':
            yield "spec.dims = %s; keys = %s" % (spec['dims'],list(spec.keys()))
        else:
            yield "spec.%s = %s" % (key,spec[key])

def extract_test(soup):
    table = soup.find_all('table')[0]
    block = soup.find_all('pre')[0].string
    frame = parse_table(table)
    spec  = load_spec(block)
    return frame,spec

def test_dims(frame,spec):
    log.debug("frame.dims: got = %s" % str(frame.dims))
    log.debug("frame.dims: exp = %s" % str(spec['dims']))
    assert frame.dims == spec['dims'], "frame.dims - mismatch"

def test_frame_rows(frame,spec):
    log.debug("frame.rows: got = %s" % list(frame.rows()))
    log.debug("frame.rows: exp = %s" % spec['rows'])
    assert list(frame.rows()) == spec['rows'], "frame.rows - mismatch"

# Note that key is expected to be in spec, but spec[key] may be None. 
def test_section_rows(frame,spec,key):
    section = frame.__getattribute__(key)
    log.debug("frame.%s.rows: got = %s" % (key,list(section.rows())))
    log.debug("frame.%s.rows: exp = %s" % (key,spec[key]))
    assert list(section.rows()) == spec[key], "frame.%s.rows - mismatch" % key

# Note that key is expected to be in spec, but spec[key] may be None. 
def test_section(frame,spec,key):
    section = frame.__getattribute__(key)
    log.debug("frame.%s got = %s" % (key,section))
    log.debug("frame.%s exp = %s" % (key,spec[key]))
    if section is not None and spec[key] is not None:
        test_section_rows(frame,spec,key)
    elif section is not None:
        assert False, "frame.%s present where null expected" % key
    elif spec[key] is not None:
        assert False, "frame.%s is null where non-null" % key
    else:
        # If we get here, both frame and spec members are null. 
        # This means the spec (correctly) requested that the frame 
        # not be present.  So, implicitly a passing result.
        log.debug("frame.%s is null, as expected" % key)


def describe_pair(frame,spec): 
    return chain (describe_spec(spec),describe_frame(frame))

def test_pair(frame,spec): 
    for line in describe_pair(frame,spec):
        log.debug(line)
    for key in spec.keys():
        if key == 'dims':
            test_dims(frame,spec)
        elif key == 'rows':
            test_frame_rows(frame,spec)
        else:
            test_section(frame,spec,key)

