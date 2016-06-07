import re
from copy import deepcopy
from itertools import product, groupby
from collections import defaultdict, OrderedDict

def frame_keys(): 
    return ('dims','head','body','foot','rows')

def section_names(): 
    return ('thead','tbody','tfoot')

class TableFrame(object):

    def __init__(self,table):
        self._first = {}
        self.physical = []
        sections = parse_table(table)
        self.consume(sections)

    def __str__(self):
        sections = ",".join(str(s) for s in self.sections())
        return "TableFrame(%d,%s;%s)" % (self.depth,self.width,sections)

    def __len__(self):
        return len(self.physical)

    def add(self,section):
        if section.name not in self._first:
            self._first[section.name] = len(self.physical)
        self.physical.append(section)

    def consume(self,sections):
        for section in sections:
            self.add(section)
    
    def sections(self):
        '''A generator which yields sections in logical (render) order:'''
        if 'thead' in self._first:
            yield self.physical[self._first['thead']]
        for i,section in enumerate(self.physical):
            if (
                (section.name == 'thead' and self._first.get('thead') != i) or
                (section.name == 'tfoot' and self._first.get('tfoot') != i) or
                (section.name == 'tbody' or section.name is None)
            ): yield section
        if 'tfoot' in self._first:
            yield self.physical[self._first['tfoot']]
            
    def first(self,name):
        if name in self._first:
            return self.physical[self._first[name]]
        else:
            return None


    @property
    def head(self): 
        return self.first('thead')

    @property
    def body(self): 
        if 'tbody' in self._first and None in self._first:
            if self._first['tbody'] < self._first[None]:
                return self.first('tbody')
            else:
                return self.first(None)
        elif 'tbody' in self._first:
            return self.first('tbody')
        elif None in self._first:
            return self.first(None)
        else:
            return None

    @property
    def foot(self): 
        return self.first('tfoot')

    @property
    def depth(self):
        if len(self) > 0:
            return sum(s.depth for s in self.sections())
        else:
            return 0

    @property
    def width(self):
        if len(self) > 0:
            return max(s.width for s in self.sections())
        else:
            return None

    @property
    def dims(self):
        return (self.depth,self.width)

    def rows(self):
        for section in self.sections(): 
            for row in section.rows():
                yield rpad_list(row,self.width)

    # Provides an ordered dict as a convenience for automated testing.  
    # The basic idea is that there are 5 main 'members' of interest 
    # ('dims','head','body','foot','rows') -- corresponding to the 
    # frame_keys() method at the very top -- which are nice to be able 
    # to cycle through and pull in a parameterized fashion.
    def as_dict(self):
        '''Returns an OrderedDict of important attributes of interest.'''
        return OrderedDict((key,self._member(key)) for key in self._keys())

    #
    # Some private helper methods to as_dict, above. 
    #

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
            return self.rows()
        else:
            raise KeyError("invalid memebr key")



class TableFrameSection(object):

    def __init__(self,name,pure,alias):
        self.name = name 
        self.pure = pure 
        self.alias = pivot_alias(alias)
        self.depth = len(self.pure) 
        self.width = logical_width(self.pure,self.alias)

    def __str__(self):
        return "TFS(%s,%d,%s)" % (self.name,self.depth,self.width)

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

    def rows(self):
        for i in range(0,self.depth):
            yield self.get_text_row(i)

#
# Helper methods
#

def rpad_list(row,width):
    extra = [None] * (width - len(row))
    return row + extra

def textify(cell):
    return cell.getText(strip=True) if cell is not None else None

def pivot_alias(alias):
    jmax = 0
    a = defaultdict(dict) 
    for i,j in alias:
        a[i][j] = alias[(i,j)]
    return a

def _pure_width(row):
    if len(row):
        return 1 + max(j for j in row.keys())
    else:
        return 0

def logical_width(pure,alias):
    '''Determines the effective (or logical) width of a grid represented by a pair of (pure,alias) structs.'''
    if len(pure):
        pure_width = max(_pure_width(row) for row in pure) 
    else:
        return 0
    if alias:
        alias_width = 1 + max(max(j for j in alias[i]) for i in alias) 
        return max(pure_width,alias_width)
    else:
        return pure_width 


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
        for t in product(range(i,rowmax),range(j,colmax)):
            if t != (i,j):
                a[t] = (i,j)


def assert_section_name(name):
    if name not in section_names():
        raise ValueError("invalid section name '%s'" % name)


# Takes an iterable of tag objects (presumably 'tr' elements), and 
# returns a convenient list-of-list struct where the row elements are 
# table cell elements (name = 'th','td') only.
def cell_grid(tagseq):
    nameset = set(['th','td'])
    return [ list(expected_children(tag,nameset)) for tag in tagseq ]


#
# The main guts of our parsing algorithm: traverses a "cell grid" 
# struct of the type above, and returns tuple of (pure,alias) structs 
# which get fed into the STDF constructor. 
#
def parse_grid(rows):
    depth = len(rows)
    pure,alias = [],{}
    for i,cells in enumerate(rows):
        k = 0
        purerow = {}
        for j,cell in enumerate(cells):
            while alias.get((i,k)):
                k += 1
            purerow[k] = cell 
            spantup = logical_span(cell)
            paint_alias(alias,i,k,spantup,depth)
            k += 1
        pure.append(purerow)
    return pure,alias




def expected_children(tag,nameset):
    '''Yields direct child elements of a tag matching a given name set.''' 
    def is_expected(tag):
        return tag.name in nameset
    return filter(is_expected,tag.find_all(recursive=False))


#
# A crucial grouping iterator which looks at Tag object (presumably a 'table' 
# element) and yields tuples of (enclosing tag, rowgroup), taking care to 
# logically group sequences of "free" rows (sequences of 'tr' elements with no 
# enclosing tags), returning None in place of their enclosing tag eleement.
#
# More specifically: in canonically defined tables the enclosing tag will be a 
# thead/tbody/tfoot element, and the rowgroup will be an iterator if its child 
# 'tr' elements.  And in tables with blocks of "free rows" we simply yield None 
# in place of the enclosing tag object (and yield the sequence of 'tr' elements 
# as its "child" row elements).
#
# So if we had a table element which had 'thead' and 'tfoot' sections declared, 
# with a block of "free" rows in between (i.e. with no enclosing 'tbody' tags), 
# our (key,group) sequence might look like this:
#
#   ( 
#     ('thead',('tr','tr')),
#     ( None,  ('tr','tr','tr')),
#     ('tfoot',('tr'))
#   )
#      
#
def groupby_virtual_sections(tag):
    nameset = set(['thead','tbody','tfoot','tr']) 
    children = expected_children(tag,nameset)
    for key,group in groupby(children,lambda child:child.name):
        if key == 'tr':
            yield None,group 
        else:
            for enctag in group:
                rowgroup = enctag.find_all('tr',recursive=False)
                yield enctag,rowgroup


def parse_logical_sections(table):
    for enctag,rowgroup in groupby_virtual_sections(table):
        name = None if enctag is None else enctag.name
        rows = cell_grid(rowgroup)
        pure,alias = parse_grid(rows)
        yield (name,pure,alias)

def parse_table(table):
    '''Yields a sequence of TableFrameSection objects for physical sections under a table element.''' 
    for name,pure,alias in parse_logical_sections(table):
        yield TableFrameSection(name,pure,alias)

def describe_rows(rows):
    yield "depth=%d" % len(rows)
    for i,row in enumerate(rows):
        yield "row[%d] : width=%d" % (i,len(row))
        for j,cell in enumerate(row):
            yield "cell[%d,%d] = %s : %s" % (i,j,cell.name,cell.attrs)
    dims = declared_dimensions(rows)
    yield "dims = %s" % str(dims)

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
            yield "frame.%s = %s = %s" % (key,member,member.rows())

def dump_table(table):
    for i,tr in enumerate(table.find_all('tr')):
        cells = [td.string for td in tr.find_all('td')]
        attrs = [deepcopy(td.attrs) for td in tr.find_all('td')]
        print("cells[%d] = %s" % (i,cells))
        print("attrs[%d] = %s" % (i,attrs))

def print_frame(frame):
    for line in describe_frame(frame):
        print(line)

#1234567890123456789012345678901234567890123456789012345678901234567890123456789

