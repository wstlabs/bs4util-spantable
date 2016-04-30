Our test cases are parameterized as HTML files.  Each contains a 'table' element to parse, along with a 'pre' block containing a JSON-serialized specification struct described below.

The tests are performed in lexical order (which will also be the numerical order, as long as the fixed-width integer indexing convention is held to).  Files with names containg the word 'SKIP' anywhere in their name will be skipped, unless the --no-skip option is used in the 'run.py' script.

About the 'spec' struct
-----------------------

Each test has a 'spec' struct specifying certain properties to test (and value to test against).  The 'spec' struct is not a complete serialization of the SpanTableDataFrame object; nor does it permit all features of this object to be otherwise exhaustively tested.  However, it efficiently represents the most important features of this key object, in a format that's easy to read edit. 

Basically the 'spec' struct is a dict which will have at least one of 5 members present, which should be (mostly) self-explanatory.  For example, here's the spec struct for test case 30:

<pre>
{
  "dims": [5,4],
  "head": [ 
    ["A","B","C"],
    ["A","D","C"]
  ],
  "body": [ 
    ["G","H","I",null],
    ["J","J","J","J"]
  ],
  "foot": [
    ["K","K"]
  ],
  "rows": [ 
    ["A","B","C",null],
    ["A","D","C",null],
    ["G","H","I",null],
    ["J","J","J","J"],
    ["K","K",null,null]
  ]
}
</pre>

Specificaly:
- *dims* represents the .dims tuple of the data frame object (that is, the entire aggregate rowset).
- *rows* represents the serialized list-of-list struct produced by exhausting the .rows iterator. 
- And *head*, *body* and *foot* represent the serializations of the .rows iterators on those members.

Again, we don't attempt to cover ever accessor on data frame object (or of its nested members); and there are some obvious gaps (for example, we don't attempt to directly test either the 'physical' or 'section' accessors).  But it does cover the most important accessors likely to be accessed in typical use cases (and implicitly, they do allow us to test corner cases e.g. on frames with multiple sections in non-standard order). 



