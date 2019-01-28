#!/usr/bin/env python
#
# In which we extract a sequence of (period,group,element) tags from 
# an HTML5 representation of the periodic table, extracted from Wikipedia.
#
import sys
from bs4 import BeautifulSoup
from bs4util.spantable import TableFrame

filename = "tests/data/90-periodic-table.html"

html = "\n".join(open(filename,"rt").readlines())
soup = BeautifulSoup(html)
table = soup.find_all('table')[0]
frame = TableFrame(table)
rows = list(frame.rows())

def parse_rows(rows):
    group = rows[1]     # header row with group designations
    head2 = rows[2]     # ignored
    body  = rows[3:14]  # all of the elements live in these rows
    for i,r in enumerate(body):
        period = None
        for j,cell in enumerate(r):
            if j == 0:
                period = cell
            elif cell is not None and len(cell):
                yield {"period":period,"group":group[j],"element":cell}

for r in parse_rows(rows):
    print(r)


