A Beautiful Soup 4 utility class for parsing HTML5 tables with complex row and column layouts.

Requiers Python 3.

### Summary

The assumption is that you've already parsed the HTML document with bs4, and have identifed the table element you'd like to parse (that is, you've found its corresponding 'bs4.element.Tag' object).  What this library provides is a one-time 'parse_table' function that returns a data frame object that provides array-like access to the logical positions of the cells within that table, taking into account all of the various tags attribute directives (like 'colspan', 'rowspan', 'thead','tbody', 'tfoot') that determine how the table is rendered. 

A simple use case might look like this::

    from bs4 import BeautifulSoup
    from bs4util.spantable import TableFrame 

    html = "\n".join(open(filename,"rt").readlines())
    soup = BeautifulSoup(html)
    table = soup.find_all('table')[0]
    frame = TableFrame(table)
    print("dims = %s" % str(frame.dims))
    for row in frame.rows():
        print(row)

Where the rows will be displayed as they would be rendered by a standards-complient browser, taking all of the various positioning directives into account.  There are also two demo scripts::

  - tests/show-periodic.py
  - tests/show-grammar.py

providing somewhat more complex use cases involving semantic extraction from HTML tables Wikipedia (Periodic Table and Japanese verb declension, respectively).

### License
```
Copyright 2017-2018 wstlabs (https://github.com/wstlabs) 

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this software except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
