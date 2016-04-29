import re
from copy import deepcopy
from itertools import product
from collections import defaultdict, OrderedDict

def frame_keys(): 
    return ('dims','head','body','foot','rows')


class SpanTableDataFrame(object):

    def __init__(self,head=None,body=None,foot=None):
        self.head = head
        self.body = body 
        self.foot = foot

    def __str__(self):
        return "STDF(dims=%s,head=%s,body=%s,foot=%s)" % ( 
            self.dims,
            cast_section_dims(self.head),
            cast_section_dims(self.body),
            cast_section_dims(self.foot)
        )


    def sections(self):
        '''Returns a tuple of (head,body,foot)'''
        return self.head,self.body,self.foot

    @property
    def depth(self):
        return sum(map(cast_section_depth,self.sections()))

    @property
    def width(self):
        return max(map(cast_section_width,self.sections()))

    @property
    def dims(self):
        return (self.depth,self.width)

    @property
    def rows(self):
        for section in (self.head,self.body,self.foot):
            if section is not None:
                for row in section.rowiter():
                    yield rpad_list(row,self.width)

    #
    # This next accessors provided an ordered dict as a convenience for 
    # automated testing.  The basic idea is that there are 5 main 'members' 
    # of interest ('dims','head','body','foot','rows') -- corresponding to
    # the frame_keys() method at the very top -- which are nice to be able 
    # to cycle through and pull in a parameterized fashion.
    #

    def as_dict(self):
        '''Returns an OrderedDict of important attributes of interest.'''
        return OrderedDict((key,self._member(key)) for key in self._keys())

    # The next 3 methods are helpers for the 'as_dict' method, but are kept
    # private so as to not muck up the public interface.

    def _keys(self):
        return (key for key in frame_keys() if self._contains(key)) 

    def _contains(self,key):
        if key in ('dims','rows'):
            return True
        elif key in ('head','body','foot'):
            return self.__getattribute__(key) is not None
        else:
            return False

    def _member(self,key):
        if key == 'dims':
            return self.dims
        elif key in ('head','body','foot'):
            return self.__getattribute__(key) 
        elif key == 'rows':
            return self.rows
        else:
            raise KeyError("invalid memebr key")



class SpanTableSection(object):

    def __init__(self,pure,alias):
        self.pure = pure 
        self.alias = pivot_alias(alias)
        self.depth = len(self.pure) 
        self.width = effective_width(self.pure,self.alias)

    def __str__(self):
        return "STS(%s)" % str(self.dims)

    @property
    def dims(self):
        return (self.depth,self.width)

    def in_bounds(self,i,j):
        if i < 0 or i >= self.depth: return False
        if j < 0 or j >= self.width: return False
        return True

    def cell(self,i,j):
        if not self.in_bounds(i,j): 
            raise ValueError("invalid coordinates (%d,%d)" % (i,j))
        if j in self.pure[i]:
            return self.pure[i][j]
        if j in self.alias[i]:
            ii,jj = self.alias[i][j]
            return self.pure[ii][jj]
        return None

    def get_text_row(self,i):
        return [ textify(self.cell(i,j)) for j in range(0,self.width) ]

    def text(self):
        return [ self.get_text_row(i) for i in range(0,self.depth) ]

    def rowiter(self):
        for i in range(0,self.depth):
            yield self.get_text_row(i)

    @property
    def rows(self):
        return list(self.rowiter())

#
# Helper methods
#

def rpad_list(row,width):
    extra = [None] * (width - len(row))
    return row + extra

#
# A couple of accessors that nicely cast a section's "depth" to 0 if that
# section is.  Note that the intended use is for 'sum' and 'max' functions
# when iterating over lists of sections (e.g. for a given data frame). 
#
# Hence the prefix 'cast_' up front.  In other uses, it's best to consider 
# null sections as having null attributes (including depth/width), to avoid
# semantic confusion.
#
def cast_section_depth(section): 
    return 0 if section is None else section.depth

def cast_section_width(section): 
    return 0 if section is None else section.width

# We also sometimes need to cast the 'dims' tuple when iterating over 
# sections, but since we generally don't need to sum or max over it, we
# can afford to do so in the semantically correct way.
def cast_section_dims(section): 
    return None if section is None else section.dims


def textify(cell):
    return cell.getText(strip=True) if cell is not None else None

def pivot_alias(alias):
    jmax = 0
    a = defaultdict(dict) 
    for i,j in alias:
        a[i][j] = alias[(i,j)]
    return a

def effective_width(pure,alias):
    if pure:
        maxj_pure = max(max(j for j in row.keys()) for row in pure if row) 
    else:
        return 0
    if alias:
        maxj_alias = max(max(j for j in alias[i]) for i in alias) 
        return max(maxj_pure + 1, maxj_alias + 1)
    else:
        return maxj_pure + 1


def is_cell(tag):
    return tag.name in ('td','th')

def find_cells(tag):
    return filter(is_cell,tag.children)

def first_pass(tag):
    rows = tag.find_all('tr',recursive=False)
    # print(":: first_pass - depth=%d" % len(rows)) 
    for i,row in enumerate(rows):
        cells = list(filter(is_cell,row.children))
        # print(":: first_pass - row[%d] : width=%d" % (i,len(cells)))
        for j,cell in enumerate(cells):
            # print(":: first_pass : cell[%d,%d] = %s : %s" % (i,j,cell.name,cell.attrs))
            pass
    rows = [
        list(filter(is_cell,row.children)) for row in tag.find_all('tr',recursive=False)
    ]
    return rows

def describe_rows(rows):
    print(":: describe depth=%d" % len(rows))
    for i,row in enumerate(rows):
        print(":: describe : row[%d] : width=%d" % (i,len(row)))
        for j,cell in enumerate(row):
            print(":: describe : cell[%d,%d] = %s : %s" % (i,j,cell.name,cell.attrs))
    dims = declared_dimensions(rows)
    print(":: describe dims = %s" % str(dims)) 

#
# Returns the "logical" colspan or rowspan value the way a lenient 
# HTML5 parser would.  Spefically, it turns the integer parse of the 
# raw text value of the attribute if it's present and looks like a 
# positive integer, or 1 otherwise.
#
intpat = re.compile('^\d+$')
def logical_spanval(tag,key):
    attrval = tag.attrs.get(key)
    if attrval is None:
        return 1
    m = re.match(intpat,attrval)
    return int(attrval) if m else 1

def logical_colspan(tag):
    return logical_spanval(tag,'colspan')

def logical_rowspan(tag):
    return logical_spanval(tag,'rowspan')

def logical_span(tag):
    return logical_rowspan(tag),logical_colspan(tag)

#
# We define the "declared width" of a row (a list or sequence of cells) 
# as the maximum cell depth we attain if we keep "walking" out to the  
# right in strides of each declared colspan attribute.
#
# For example, if we get a sequence of cells with colspans (4,1,2) then
# the declared with is 7.
#
# Note that in general we have declared_width(row) >= len(row); and
# for an empty row, the declared width is 0.
#
def declared_width(row):
    return sum(map(logical_colspan,row))

def declared_dimensions(rows):
    depth = len(rows)
    width = max(map(declared_width,rows))
    return (depth,width)


def paint_alias(a,i,j,spantup,depth):
    rowspan,colspan = spantup
    if rowspan > 1 or colspan > 1:
        rowmax = min(i+rowspan,depth)
        colmax = j+colspan
        # tups = product(range(i,rowmax),range(j,colmax))
        # print(":: paint[%d,%d] + %s => %s" % (i,j,str(spantup),list(tups)))
        for t in product(range(i,rowmax),range(j,colmax)):
            if t != (i,j):
                a[t] = (i,j)


def parse_section(tag):
    rows = first_pass(tag)
    # describe_rows(rows)
    depth = len(rows)
    pure,alias = [],{}
    rows = tag.find_all('tr',recursive=False)
    # print(":: parse_section - depth=%d" % depth) 
    for i,row in enumerate(rows):
        cells = list(filter(is_cell,row.children))
        # print(":: parse_section - row[%d] : width=%d" % (i,len(cells)))
        k = 0
        purerow = {}
        for j,cell in enumerate(cells):
            # print("..")
            while alias.get((i,k)):
                k += 1
            purerow[k] = cell 
            spantup = logical_span(cell)
            # print("i,k(j) = %d,%d(%d) => cell = %s" % (i,k,j,cell))
            # print(":: parse_section - cell[%d,%d] : span = %s" % (i,k,str(spantup)))
            paint_alias(alias,i,k,spantup,depth)
            # print("alias => ",alias)
            k += 1
            # print("k => %d" % k) 
        pure.append(purerow)
    # print("pure =",pure)
    # print("alias =",alias)
    return SpanTableSection(pure,alias)


def parse_table(soup):
    head = parse_section(soup.thead) if soup.thead is not None else None
    body = parse_section(soup.tbody) if soup.tbody is not None else None
    foot = parse_section(soup.tfoot) if soup.tfoot is not None else None
    if (head,body,foot) == (None,None,None):
        body = parse_section(soup)
    return SpanTableDataFrame(head,body,foot)


def dump_table(table):
    for i,tr in enumerate(table.find_all('tr')):
        cells = [td.string for td in tr.find_all('td')]
        attrs = [deepcopy(td.attrs) for td in tr.find_all('td')]
        print("cells[%d] = %s" % (i,cells))
        print("attrs[%d] = %s" % (i,attrs))

def describe_frame(frame):
    d = frame.as_dict()
    yield "frame = %s" % frame 
    for key,member in d.items(): 
        if key == 'dims':
            yield "frame.%s = %s" % (key,member)
        elif key == 'rows':
            yield "frame.%s = %s" % (key,list(member))
        else: 
            # Implicity key must be one of 'head','body','foot':
            yield "frame.%s = %s = %s" % (key,member,member.rows)

def print_frame(frame):
    for line in describe_frame(frame):
        print(line)

