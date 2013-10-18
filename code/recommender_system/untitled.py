import sys
from multiprocessing import Pool

def Map(L):

  results = []
  for w in L:
    # True if w contains non-alphanumeric characters
    if not w.isalnum():
      w = sanitize (w)

    # True if w is a title-cased token
    if w.istitle():
      results.append ((w, 1))

  return results

def Partition(L):
  tf = {}
  for sublist in L:
    for p in sublist:
      # Append the tuple to the list in the map
      try:
        tf[p[0]].append (p)
      except KeyError:
        tf[p[0]] = [p]
  return tf

def Reduce(Mapping):
  return (Mapping[0], sum(pair[1] for pair in Mapping[1]))


def chunks(l, n):
  for i in xrange(0, len(l), n):
    yield l[i:i+n]

def tuple_sort (a, b):
  if a[1] < b[1]:
    return 1
  elif a[1] > b[1]:
    return -1
  else:
    return cmp(a[0], b[0])





if __name__ == '__main__':

  if (len(sys.argv) != 2):
    print "Program requires path to file for reading!"
    sys.exit(1)

  # Load file, stuff it into a string
  text = load (sys.argv[1])

  # Build a pool of 8 processes
  pool = Pool(processes=8,)

  # Fragment the string data into 8 chunks
  partitioned_text = list(chunks(text, len(text) / 8))

  # Generate count tuples for title-cased tokens
  single_count_tuples = pool.map(Map, partitioned_text)

  # Organize the count tuples; lists of tuples by token key
  token_to_tuples = Partition(single_count_tuples)

  # Collapse the lists of tuples into total term frequencies
  term_frequencies = pool.map(Reduce, token_to_tuples.items())

  # Sort the term frequencies in nonincreasing order
  term_frequencies.sort (tuple_sort)

  for pair in term_frequencies[:20]:
    print pair[0], ":", pair[1]
