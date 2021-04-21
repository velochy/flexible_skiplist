from random import getrandbits

# TODO: add bounardy checks for indices

class skiplist:
  def __init__(self, in_lst = None, key=None, cumulate_field_fns=[]):

    self._sort_fn = key
    self.sum_field_fns = cumulate_field_fns + [lambda _: 1] # always cumulate indices for position
    self._zeros = [] # initialized by _init_zeros when first element added

    self._used_level = 1
    self._head = self._tail = None

    # Cache used for internal operations
    self._path = None
    self._psums = None # initialized by _init_zeros

    # If an initialization list was provided, use it
    if in_lst is not None and len(in_lst) > 0:
      self._initialize_from_list(in_lst)


  # Called when first element added to initialize zeros to right types
  def _init_zeros(self,val):
    self._zeros = [ fn(val)-fn(val) for fn in self.sum_field_fns]

    self._head = self._create_node(None,self._used_level,True)
    self._tail = self._create_node(None,self._used_level,True)

    # Set head and tail to one level above used_level and keep them that way
    # This will make trail track cumulative sums (including length of list)
    self._head[1].append(None)
    self._tail[1].append(None)

    # Link head to tail in all levels
    for i in range(len(self._head[1])):
      self._head[1][i] = self._tail

    self._psums = [self._zeros[:] for _ in range(self._used_level+1) ]
    self._path = [self._head] * (self._used_level+1)

  def _update_used_level(self,add):
    
    # Check if last layer has any elements
    # If yes, increase used_level so that would no longer be the case
    if add:
      while add > self._used_level:
        self._head[1].append(self._tail)
        self._tail[1].append(None)

        self._path.append(self._head)
        self._psums.append(self._zeros[:])

        self._used_level+=1
    elif add is None:
      # Remove levels until only the topmost one is empty
      while len(self._head[1])>=3 and self._head[1][-2]==self._tail:
        self._head[1].pop()
        self._tail[1].pop()

        self._path.pop()
        self._psums.pop()

        self._used_level-=1

  # Normal use case is with getrandbits, but also useful for
  # creating perfectly balanced tree on init by just feeding indices
  def _gen_level(self, bits):
    lvl = 0
    while bits & (1<<lvl) and lvl < self._used_level: lvl+=1
    return lvl+1 # at least 1

  # Helper function to create a node of fixed level
  def _create_node(self,val,level=None,head_or_tail=False):
    # Unless level specified, choose randomly, but at most one level higher than used_level
    # Use p = 1/2, as it simplifies things a lot, and is only very marginally less efficient than the optimal 1/e
    if level is None: level = self._gen_level(getrandbits(self._used_level))

    node = (val,[None for _ in range(level)],self._zeros[:])

    if self._sort_fn is not None:
      node = node + (self._sort_fn(val) if not head_or_tail else None,)

    return node

  # Initialize from values in a list - O(n) whereas serial insertion is O(nlogn)
  def _initialize_from_list(self,in_lst):

    # Find highest bit of length, and set height once
    lvl, l = 1, len(in_lst)
    while l>0:
      l=l>>1
      lvl+=1
    self._used_level = lvl

    # Initialize zeros (and everything else needed)
    self._init_zeros(in_lst[0])

    # Sort array if key was provided
    if self._sort_fn: in_lst = sorted(in_lst,key=self._sort_fn)  

    # Create a perfectly balanced tree structure by feeding indices to _gen_level
    li = len(in_lst)-1 # (li-i) is used to also reverse indices
    prev_ll = self._head[1] # linked list of head

    # Doing it in reverse is faster because links are simpler to handle
    for i,val in enumerate(reversed(in_lst)):

      node = self._create_node(val,self._gen_level(li-i))
      lvl = len(node[1])

      # Insert it into level i linked list
      csums = self._zeros
      for i in range(lvl):
        nxt = prev_ll[i]
        node[1][i] = nxt
        prev_ll[i] = node
        
        # Set the sum of next element
        # Done this way it is amortized O(1)
        for j,pv in enumerate(self._psums[i]):
          nxt[2][j] = pv
          self._psums[i+1][j] += pv
          self._psums[i][j] = self._zeros[j]

      for j,sf in enumerate(self.sum_field_fns):
          self._psums[lvl-1][j] += sf(val)

    # Final pass on sums - from head element to first of each level
    for i in range(self._used_level+1):
      nxt = prev_ll[i]
      for j,pv in enumerate(self._psums[i]):
        nxt[2][j] = pv
        if i<self._used_level:
          self._psums[i+1][j] += pv
        self._psums[i][j] = self._zeros[j]


  # Assumes both path and psums is filled accurateily
  def _insert_after_path(self,val,level=None):

    # If zeros have not yet been initialized, do so
    if len(self._zeros)==0: self._init_zeros(val)

    node = self._create_node(val,level)

    # Add levels if needed
    self._update_used_level(add=len(node[1]))

    # Set sums to full sum from beginning
    full_sums = self._psums[0]

    # Compute values of comulative functions only once
    node_cvals = [ sf(node[0]) for sf in self.sum_field_fns ]

    for i in range(len(node[1])):
      # Insert it into level i linked list
      prev = self._path[i]
      node[1][i] = nxt = prev[1][i]
      prev[1][i] = node

      # Update sums as well, if we are at the highest level of next
      if i == len(nxt[1])-1:
        for j,sf in enumerate(self.sum_field_fns):
          nxt[2][j] -= full_sums[j] - self._psums[i][j]

    for j,cv in enumerate(node_cvals):
      node[2][j] += cv + full_sums[j] - self._psums[i][j]

    # Fix the sums of higher lists too
    for i in range(len(node[1]),self._used_level+1):
        nxt = self._path[i][1][i]

        # Again, only update for highest level 
        if i == len(nxt[1])-1:
          for j,cv in enumerate(node_cvals):
            nxt[2][j] += cv

  # remove the element right after the current path
  def _delete_after_path(self):
    # Set sums to full sum from beginning
    full_sums = self._psums[0]
    node = self._path[0][1][0]

    # Compute values of comulative functions only once
    node_cvals = [ sf(node[0]) for sf in self.sum_field_fns ]

    for i in range(len(node[1])):
      # Insert it into level i linked list
      prev = self._path[i]
      nxt = node[1][i]
      prev[1][i] = nxt

      # Update sums as well, if we are at the highest level of next
      if i == len(nxt[1])-1:
        for j,sf in enumerate(self.sum_field_fns):
          nxt[2][j] += full_sums[j] - self._psums[i][j]

    # Fix the sums of higher lists too
    for i in range(len(node[1]),self._used_level+1):
        nxt = self._path[i][1][i]

        # Again, only update for highest level 
        if i == len(nxt[1])-1:
          for j,cv in enumerate(node_cvals):
            nxt[2][j] -= cv

    # Remove levels if there are any extra
    self._update_used_level(add=False)


  # Find the element and set path and psums while doing so
  def _find_set_path(self, sval, ind=None):
    if len(self._zeros)==0: return None # not initialized yet
    
    # Check if path already points to the right place
    # Worth it in practical applications where you often check value before adding/removing
    '''prv, nxt = self._path[0], self._path[0][1][0]
    if ind: print(sval,ind,prv[0],nxt[0],"PS",self._psums[0][ind],"N",nxt[2][ind])
    if (ind is None and (prv == self._head or prv[3]<sval) and (nxt == self._tail or nxt[3]>=sval)) or \
       (ind is not None and self._psums[0][ind]<sval and 
              self._psums[0][ind]+self.sum_field_fns[ind](nxt[0])>=sval):
      return nxt'''
      
    # Start search from beginning
    cur, csum = self._head, self._zeros[:]

    for i in range(self._used_level-1,-1,-1): # equivalent to reversed(range(self._used_level))
      while True:
        nxt = cur[1][i]

        if nxt == self._tail: # end-of-list
          break
        elif ind is None and nxt[3]>=sval: # by search index
          break 
        elif ind is not None and csum[ind]+nxt[2][ind]>=sval: # by cumulative sum
          break
        else: # take the step
          for j,v in enumerate(nxt[2]):
            csum[j] += v
          cur = nxt

      # Set psums to intermediate values
      # These are needed when adding/removing elements
      for j, v in enumerate(csum):
        self._psums[i][j] = v 

      self._path[i] = cur

    # Path is to the last element < sval so ..
    # next element is the one >= searched value
    return self._path[0][1][0]

  # move path forward to next element
  def _path_to_next(self):
    nxt = self._path[0][1][0]
    llvl = len(nxt[1])-1

    # Update sums on highest level of new node
    for j, v in enumerate(nxt[2]):
        self._psums[llvl][j] += v
    self._path[llvl] = nxt

    # Set all lower levels to same values
    for i in range(llvl-1,-1,-1):
      for j, cv in enumerate(self._psums[llvl]):
        self._psums[i][j] = cv 
      self._path[i] = nxt
      
    return self._path[0][1][0]


  def _avg_step_count(self):
    lsteps = [ 0 for _ in range(self._used_level)]
    ssum, max_steps = 0, 0

    cur = sl.head[1][0]
    while cur!=sl.tail:
      
      lvl = len(cur[1])-1

      # Count horizontal steps
      csteps = lsteps[lvl] = lsteps[lvl] + 1
      for i in range(lvl-1,-1,-1):
        lsteps[i] = csteps

      # Add vertical steps too
      csteps += self._used_level;

      ssum += csteps

      if csteps>max_steps: max_steps = csteps

      cur = cur[1][0]

    return float(ssum)/len(self), max_steps


  def _print_state(self):
    csum, ind = 0, 0
    print("Skip-list, len %i" % (len(self)))
    cur = self._head[1][0]
    while cur!=self._tail:
      csum += cur[0][1]
      print(" %3i val: %10r ci: %3i len %3i lst: %r" % (ind, cur[0], cur[2][-1], len(cur[1]), list(map(lambda x: x[0], cur[1]))) )
      cur = cur[1][0]
      ind += 1


  # Check all links and cumsums
  # Useful for testing
  def _verify_structure(self):
    # TODO
    pass

  def _print_debug(self):
    #TODO
    pass

  # Iterate over list starting from (and including) pos
  def iterator(self,pos):
    #TODO
    pass

  def insert(self,val,pos=None):
    # TODO - throw errors if pos given and sorted, or if not given and not sorted

    if self._sort_fn:
      self._find_set_path(self._sort_fn(val))
    else:
      self._find_set_path(pos+1,-1)

    self._insert_after_path(val)

  def remove(self,val):
    if self._sort_fn:
      sval = self._sort_fn(val)
      cur = self._find_set_path(sval)

      # Iterate over all values that share the same search_value
      while cur[3]==sval and cur[0]!=val:
        cur = self._path_to_next()

      if cur[3]!=sval:
        raise Exception('element to be removed not found in skiplist')
      else:
        self._delete_after_path()
    else:
      raise Exception('remove only works for sorted skiplist')

  def delete(self,pos):
    self._find_set_path(pos+1,-1)
    self._delete_after_path()

  # Find first element for which i-th cumulative sum is at or above val
  # Return that element + the cumulative sums up to (but not including) it
  # Returns None as the element if overall sum is less than val
  def find_by_cumulative_sum(self,val,i=0):
    res = self._find_set_path(val,i) # Finds path to previous element
    return res[0],self._psums[0][:-1]

  def __getitem__(self, pos):
    # Position indexing is 1-based in skiplist, so look for pos+1
    return self._find_set_path(pos+1,-1)[0]

  def __len__(self):
    return self._tail[2][-1]
