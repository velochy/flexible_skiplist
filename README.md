# A Flexible implementation of Skiplist

This implementation of skiplist unlocks the full potential of the data structure by also allowing for both sorted and non-sorted skiplists and also enabling O(logn) search by cumulative sums.

In short, it can serve as the standard sorted key-value store (as do other implementations), but it can also allow you to keep a non-sorted list which gives you O(logn) calculation of sums from beginning to k-th element. 

Or, as was the use case the author needed but did not find, both at the same time - a sorted list with search into it also by cumulative sums.

The code is written in pure Python 3 without external dependencies and is moderately optimized. 

A simple example to illustrate usage
```
from flexible_skiplist import skiplist

# Create a list of tuples, sorted by first value and cumulating the second one
sl = skiplist([(3,5.1),(7,2.2),(1,3.7)],key=lambda x: x[0], cumulate_field_fns=[lambda x: x[1]])

# Fetch the first element in order, i.e. (1,3.7)
sl[0] 

# Add an element - will be sorted to place if sort key given
# Without sort key, expects index to insert at as second parameter
sl.insert( (10,1.2) ) 

# Delete element by index
sl.delete(2) 

# Remove an element by value - only when sort key provided
sl.remove( (3,5.1) ) 

# Find the element the adding of which would push the 1. cumulate field above 4.0
# Returns a pair: the element, and a list of all the sums up to but not including it
sl.find_by_cumulative_sum(4.0,1) 
```

### NB! Currently, the API is subject to change with each minor version.
This will remain so until version 1.0.0 is released. This is currently a hobby project that I myself use in one other project. 
If you need this functionality to be stable, do feel free to reach out to me at velochy@gmail.com and I'd be happy to agree on a stable final version. 