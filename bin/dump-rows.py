#!/usr/bin/env python
#
# Reads an HTML file, dumps the rows of the first table it finds. 
#
import sys
from bs4 import BeautifulSoup
from bs4util.spantable import TableFrame

filename = sys.argv[1]

html = "\n".join(open(filename,"rt").readlines())
soup = BeautifulSoup(html)
tables = soup.find_all('table')
print("Document has %d table(s)." % len(tables))
table = tables[0]

frame = TableFrame(table)
for row in frame.rows():
    print(row)
