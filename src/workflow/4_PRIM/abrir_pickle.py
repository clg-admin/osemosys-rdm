# import pickle

# x=pickle.load('all_comp_pfd.pickle')

import pickle

# open a file, where you stored the pickled data
file = open('comp_pfd_1.pickle', 'rb')

# dump information to that file
data = pickle.load(file)

# close the file
file.close()