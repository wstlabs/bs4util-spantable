#!/usr/bin/env python
#
# Parses structured information (about verb conjugations) from a table extracted 
# from a Wikipedia page on Japanese grammar.
#
import sys
from bs4 import BeautifulSoup
from bs4util.spantable import parse_table

filename = "tests/data/91-japanese-grammar.html" 

html = "\n".join(open(filename,"rt").readlines())
soup = BeautifulSoup(html)
table = soup.find_all('table')[0]
frame = parse_table(table)

# Constructs a "clean dict" out of two sequences, with degenerate key-val 
# pairs (where the value part is an empty string) omitted.
def cleandict(keys,vals):
    r = dict(zip(keys,vals))
    delkeys = [k for k in r if r[k] == '']
    for k in delkeys:
        del r[k]
    return r

def parse_rows(rows):
    group = rows[0]     # header row with group designations
    body  = rows[2:-1]  # all of the elements live in these rows
    # The first two columns are thought of as keys; the rest are group tags.
    grouptags  = group[2:-1] 
    for i,row in enumerate(body):
        case = row[0]
        rule = row[1]
        cells = row[2:-1]
        r = cleandict(grouptags,cells)
        yield case,rule,r 

rows = list(frame.rows())
for case,rule,r in parse_rows(rows):
    print("%s, %s: %s" % (case,rule,r))


