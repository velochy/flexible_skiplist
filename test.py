from flexible_skiplist import skiplist
from random import randint

# NB! Can flake as neither sort order is stable. Keep maxval high so values are unlikely to repeat

MAXVAL = 100000
N, M = 100, 100

def test_sorted_skiplist():

  # Create an indexed list of random integers
  lst = [ (i,randint(0,MAXVAL)) for i in range(N)]

  # Sort them by the random value
  sl = skiplist([], key=lambda x: x[1], cumulate_field_fns=[lambda x: x[1]])

  # insert list into skiplist
  for v in reversed(lst):
    sl.insert(v)

  # check length
  assert len(lst) == len(sl)

  # check if it is sorted properly
  slst = sorted(lst,key=lambda x:x[1])
  for i, v in enumerate(slst):
    assert v == sl[i]

  # Initialize with full list
  sl = skiplist(lst, key=lambda x: x[1], cumulate_field_fns=[lambda x: x[1]])

  # Again, check if it is sorted properly
  for i, v in enumerate(slst):
    assert v[1] == sl[i][1]

  # Perform random insertions
  for i in range(N,N+M):
    val = (i,randint(0,MAXVAL))
    sl.insert(val)
    lst.append(val)

  # Check if still sorted properly
  slst = sorted(lst,key=lambda x:x[1])
  for i, v in enumerate(slst):
    assert v[1] == sl[i][1]

  # Perform random deletions
  for i in range(M):
    ind = randint(0,len(lst)-1)
    val = lst[ind]
    sl.remove(val)
    del lst[ind]

  # Check if still sorted properly
  slst = sorted(lst,key=lambda x:x[1])
  for i, v in enumerate(slst):
    assert v[1] == sl[i][1]

  # Create an indexed list of constant 0 values
  lst = [ (i,0) for i in range(N)]
  sl = skiplist(lst,key=lambda x: x[1])

  # Perform random deletions
  for i in range(N-1):
    ind = randint(0,len(lst)-1)
    val = lst[ind]
    sl.remove(val)
    del lst[ind]

  # Check that the right element remains
  assert lst[0] == sl[0]

  
test_sorted_skiplist()

from time import perf_counter

for N in [4,16,64,256,1024,4096]:

  lst = [ (i,randint(0,MAXVAL)) for i in range(N)]

  beg_time = perf_counter()
  for _ in range(M):
    sl = skiplist(lst, cumulate_field_fns=[lambda x: x[1]])

  time = (perf_counter()-beg_time)
  print("%5i: Time: %.6f (%.7f)" % (N,time/M,time/(M*N)))

  beg_time = perf_counter()
  for _ in range(M):
    sl = skiplist([], cumulate_field_fns=[lambda x: x[1]])
    # Doing it in reverse is faster because links are simpler to handle
    li = len(lst)-1
    for i,val in enumerate(reversed(lst)):
      sl._insert_after_path(val,sl._gen_level(li-i))

  time = (perf_counter()-beg_time)
  print("%5i: Time: %.6f (%.7f)" % (N,time/M,time/(M*N)))

