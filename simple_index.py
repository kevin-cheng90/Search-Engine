
# simple_index.py

# Run this file to build the index for the main index,
# then run search.
# This should prob be put in the m1 file later on
# and run at the end of the index creation.


def index_simplifier(file_index: 'file'):
    counter = 0
    simple_index = open("simple_index.txt", "w")
    with open(file_index) as f:
        # to get the first token
        item = f.readline()
        simple_index.write(item.strip('\n'))
        simple_index.write("," + str(0) + '\n')
        counter += len(item) + 1

        # file.seek() works char by char, so adds the length
        # of the line to counter and if line is \n, 
        # the next line must be a token so writes token and 
        # seek position to file
        for line in f:
            if line == "\n":
                counter += len(line) + 1
                l = f.readline()
                simple_index.write(l.strip('\n'))
                simple_index.write("," + str(counter) + '\n')
                counter += len(l) + 1
            else:
                counter += len(line) + 1
    simple_index.close()


import time
if __name__ == '__main__':
    start = time.time()
    index_simplifier("index.txt")
    end = time.time()
    print(str(end-start))
