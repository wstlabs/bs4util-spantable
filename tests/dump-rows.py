#!/usr/bin/env python
#
# Reads an HTML file, dumps the rows of the first table it finds. 
#
import sys
from bs4 import BeautifulSoup
from bs4util.spantable import parse_table

filename = sys.argv[1]

html = "\n".join(open(filename,"rt").readlines())
soup = BeautifulSoup(html)
table = soup.find_all('table')[0]
frame = parse_table(table)
for row in frame.rows():
    print(row)
