# Implementation of B+-tree functionality.

from index import *
import math

# You should implement all of the static functions declared
# in the ImplementMe class and submit this (and only this!) file.
class ImplementMe:

  # Returns a B+-tree obtained by inserting a key into a pre-existing
  # B+-tree index if the key is not already there. If it already exists,
  # the return value is equivalent to the original, input tree.
  #
  # Complexity: Guaranteed to be asymptotically linear in the height of the tree
  # Because the tree is balanced, it is also asymptotically logarithmic in the
  # number of keys that already exist in the index.
  @staticmethod
  def InsertIntoIndex( index, key ):
    # Return original tree if already exists
    if (ImplementMe.LookupKeyInIndex(index, key)):
      return index

    # Find where to insert key
    cur_node = ImplementMe.findNode(index.root, key)
    
    # Insert into leaf
    if ImplementMe.isNodeFull(cur_node):
      # Overflow 
      root = ImplementMe.splitNode(index.root, cur_node, key)   
      newbtree = Index(root=root)
      return newbtree

    else:
      # No Overflow
      for idx, ele in enumerate(cur_node.keys.keys):
        if ele is None:
          cur_node.keys.keys[idx] = key
          break
      cur_node.keys.keys = ImplementMe.sortNode(cur_node.keys.keys)
    
    return index


  # Returns a boolean that indicates whether a given key
  # is found among the leaves of a B+-tree index.
  #
  # Complexity: Guaranteed not to touch more nodes than the
  # height of the tree
  @staticmethod
  def LookupKeyInIndex( index, key ):
    node = ImplementMe.findNode(index.root, key)
    if node.keys.keys.count(key) == 0:
      return False
    return True


  # Returns a list of keys in a B+-tree index within the half-open
  # interval [lower_bound, upper_bound)
  #
  # Complexity: Guaranteed not to touch more nodes than the height
  # of the tree and the number of leaves overlapping the interval.
  @staticmethod
  def RangeSearchInIndex( index, lower_bound, upper_bound ):
    node = ImplementMe.findNode(index.root, lower_bound)
    start_idx = None

    if lower_bound == upper_bound:
      if (ImplementMe.LookupKeyInIndex(index, lower_bound)):
        return [lower_bound]

    for idx, lkey in enumerate(node.keys.keys):
      if lkey >= lower_bound:
        start_idx = idx
        break
    if start_idx is None:
      return []

    key = node.keys.keys[start_idx]
    if key >= upper_bound:
      return []
    key_list = [key]
    while key < upper_bound:
      if start_idx == 0:
        key = node.keys.keys[1]
        if key is None:
          key = node.keys.keys[0]
          start_idx = start_idx + 1
          continue
        if key < upper_bound:
          key_list.append(key)
        start_idx = start_idx + 1
      else:
        node = node.pointers.pointers[2]
        if node is None:
          return key_list
        key = node.keys.keys[0]
        if key < upper_bound:
          key_list.append(key)
        start_idx = 0
      
    key_list = list(filter(None, key_list))
    return key_list


  # Helper Functions:
  def isLeafNode( node ):
    if (node.pointers.pointers[0] is None):
      return True
    return False


  def isNodeFull( node ):
    if (node.keys.keys.count(None) == 0):
      return True
    return False
  

  def sortNode(list):
    return sorted(list, key=lambda x: (x is None, x))


  def newRoot(lc, rc, key):
    return Node(keys=KeySet([key, None]), pointers=PointerSet([lc, rc, None]))


  def getParentRec(cur_node, child):
    # Basecase
    for pnt in cur_node.pointers.pointers:
      if not (pnt is None):
        if pnt == child:
          return cur_node

    child_key = child.keys.keys[0]

    for idx, key in enumerate(cur_node.keys.keys):
      if (key is None):
        cur_node = cur_node.pointers.pointers[idx]
        return ImplementMe.getParentRec(cur_node, child)
      elif (key > child_key):
        cur_node = cur_node.pointers.pointers[idx]
        return ImplementMe.getParentRec(cur_node, child)

    cur_node = cur_node.pointers.pointers[Index.NUM_KEYS]    
    return ImplementMe.getParentRec(cur_node, child)


  def getParent(root, child):
    return ImplementMe.getParentRec(root, child)


  # returns node that key should be added to or key is inside.
  def findNode(root, key):
    cur_node = root 
    while( ImplementMe.isLeafNode(cur_node) == False):
      for idx, ele in enumerate(cur_node.keys.keys):
        if (ele is None or ele > key):
          cur_node = cur_node.pointers.pointers[idx]
          break           
        else:
          if(idx == cur_node.get_num_keys()-1):
            cur_node = cur_node.pointers.pointers[idx+1]
            break
    return cur_node


  def internalSplit(root, node, new_child, key):
    # splits keys into node and new_node
    if ImplementMe.isNodeFull(node):
    # Overflow
      temp_list = node.keys.keys.copy()
      temp_list.append(key)        
      temp_list = ImplementMe.sortNode(temp_list)

      new_key_idx = temp_list.index(key)     
      split_idx = math.ceil(Index.NUM_KEYS/2)
      new_idx = 0

      new_node = Node()

      for idx, ele in enumerate(temp_list):
        if idx < split_idx:
          node.keys.keys[idx] = ele
        elif idx == split_idx:
          parent_key = ele
          node.keys.keys[idx] = None
        else:
          new_node.keys.keys[new_idx] = ele
          if idx < Index.NUM_KEYS:
            node.keys.keys[idx] = None
          new_idx = new_idx + 1


      if new_key_idx == 0:
        new_node.pointers.pointers[0] = node.pointers.pointers[1]
        new_node.pointers.pointers[1] = node.pointers.pointers[2]
        node.pointers.pointers[1] = new_child
        node.pointers.pointers[2] = None
      elif new_key_idx == 1:
        new_node.pointers.pointers[0] = new_child
        new_node.pointers.pointers[1] = node.pointers.pointers[2]
        node.pointers.pointers[2] = None
      else:
        new_node.pointers.pointers[0] = node.pointers.pointers[2]
        new_node.pointers.pointers[1] = new_child
        node.pointers.pointers[2] = None

      if(node == root):
        new_root = ImplementMe.newRoot(node, new_node, parent_key)
      else:
        new_root = ImplementMe.internalSplit(root, ImplementMe.getParent(root, node), new_node, parent_key)
      return new_root
    else:
    # No Overflow
      insert_idx = 0
      for idx, ele in enumerate(node.keys.keys):
        if ele is None:
          node.keys.keys[idx] = key
          node.pointers.pointers[idx+1] = new_child
        elif ele > key:
          insert_idx = idx  
          continue
        
      # Move keys and pointers over to add element  
      for idx in range(Index.NUM_KEYS-1,insert_idx,-1):
        node.keys.keys[idx] = node.keys.keys[idx-1]
      for idx in range(Index.FAN_OUT-1,insert_idx+1,-1):
        node.pointers.pointers[idx] = node.pointers.pointers[idx-1]
      node.keys.keys[insert_idx] = key
      node.pointers.pointers[insert_idx+1] = new_child

    return root 


  # Splits node and returns updated tree. Works for all overflow cases
  def splitNode(root, node, key):
    # Splits keys into node and new_node
    temp_list = node.keys.keys.copy()
    temp_list.append(key)        
    temp_list = ImplementMe.sortNode(temp_list)

    split_idx = math.ceil(Index.NUM_KEYS/2)-1
    new_idx = 0
    
    new_node = Node()
        
    for idx, ele in enumerate(temp_list):
      if idx <= split_idx:
        node.keys.keys[idx] = ele
      else:
        new_node.keys.keys[new_idx] = ele
        if idx < Index.NUM_KEYS:
          node.keys.keys[idx] = None
        new_idx = new_idx + 1

    new_node.pointers.pointers[Index.FAN_OUT-1] = node.pointers.pointers[Index.FAN_OUT-1]
    node.pointers.pointers[Index.FAN_OUT-1] = new_node

    # Move key up tree
    if( node == root):
      new_root = ImplementMe.newRoot(node, new_node, new_node.keys.keys[0])
    else:
      new_root = ImplementMe.internalSplit(root, ImplementMe.getParent(root, node), new_node, new_node.keys.keys[0])

    return new_root


    