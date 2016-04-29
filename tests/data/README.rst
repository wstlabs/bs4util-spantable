Our test cases are parameterized as HTML files.  Each contains a 'table' element to parse, along with a 'pre' block containing a JSON-serialized test spec.

The tests are performed in lexical order (which will also be the numerical order, as long as the fixed-width integer indexing convention is held to).  Files with names containg the word 'SKIP' anywhere in their name will be skipped, unless the --no-skip option is used in the 'run.py' script.

