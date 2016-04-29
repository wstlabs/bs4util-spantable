A simple Beautiful Soup 4 utility class for parsing HTML5 tables with complex row and column layouts.

The assumption is that you've already parsed the HTML document with bs4, and have identifed the table element you'd like to parse (that is, you've found its corresponding 'bs4.element.Tag' object).  What this library provides is a one-time 'parse_table' function that returns a data frame object that provides array-like access to the logical positions of the cells within that table, taking into account all of the various tags attribute directives (like 'colspan', 'rowspan', 'thead','tbody', 'tfoot') that determine how the table is rendered. 

A simple use case might look like this:

    from bs4 import BeautifulSoup
    from bs4util.spantable import parse_table

    html = "\n".join(open(filename,"rt").readlines())
    soup = BeautifulSoup(html)
    table = soup.find_all('table')[0]
    frame = parse_table(table)
    for row in frame.rows():
        print(row)

Where the rows will be displayed as they would be rendered by a standards-compliaent browser, taking all of the various positioning directives into account. 



