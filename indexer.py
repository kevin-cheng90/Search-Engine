import nltk
import os
import json
from bs4 import BeautifulSoup
from nltk.stem.porter import PorterStemmer
from collections import Counter 

MAX_DOCS = 5000

def compute(): 
    cwd = os.getcwd()
    mapping = {}
    doc_id = 0
    unique_tokens = set()
    doc_token_mapping = dict()
    token_freq = dict() #For milestone 3
    for p, d, f in os.walk(cwd):
        for file in f:
            if '.json' in file:
                mapping[doc_id] = file
                res = extract_tokens(str(p)+'\\'+file)
                tokens = res[0]
                doc_token_mapping[doc_id] = tokens
                unique_tokens.update(tokens)
                token_freq[doc_id] = res[1]
                doc_id += 1
            if (doc_id % MAX_DOCS) == 0:
                if doc_id != 0:
                    if doc_id == MAX_DOCS:      # this means it's the first batch of indexes being written
                        index_values = build_index(mapping, doc_token_mapping, unique_tokens, 0)
                        index_file = open("index1.txt", 'w')
                    else:
                        index_values = build_index(mapping, doc_token_mapping, unique_tokens, doc_id-MAX_DOCS)
                        index_file = open("index2.txt", 'w')
                    # index_values is the finalized index. Sort to make the merge process easier
                    for word in sorted(index_values):
                        index_file.write(word+'\n')
                        l = len(index_values[word])
                        counter = 0
                        # counter to check if we're at the end of the loop, so when we write
                        # the last value we don't need to add ", "
                        for stats in index_values[word]:
                            counter += 1
                            if counter == l:
                                index_file.write(str(stats[0]) + ", " + str(stats[1]))
                            else:
                                index_file.write(str(stats[0]) + ", " + str(stats[1]) + ", ")
                        index_file.write('\n\n')
                    index_file.close()
                    # merge the files, clear the data structures, then store the results as 
                    # "index1.txt" to be merged again with the next index
                    if os.path.isfile("index2.txt"):
                        merge('index1.txt', 'index2.txt')
                        os.remove("index1.txt")
                        os.remove("index2.txt")
                        os.rename("index3.txt", "index1.txt")
                    mapping = {}
                    unique_tokens = set()
                    doc_token_mapping = dict()
    
    # for the final index values
    index_values = build_index(mapping, doc_token_mapping, unique_tokens, doc_id - (doc_id % MAX_DOCS))
    index_file = open("index2.txt", 'w')
    for word in sorted(index_values):
        index_file.write(word+'\n')
        l = len(index_values[word])
        counter = 0
        for stats in index_values[word]:
            counter += 1
            if counter == l:
                index_file.write(str(stats[0]) + ", " + str(stats[1]))
            else:
                index_file.write(str(stats[0]) + ", " + str(stats[1]) + ", ")
        index_file.write('\n\n')
    index_file.close()
    if os.path.isfile("index2.txt") and os.path.isfile("index1.txt"):
        merge('index1.txt', 'index2.txt')
        os.remove("index1.txt")
        os.remove("index2.txt")
        os.rename("index3.txt", "index.txt")

    #For frequency counting
    with open('freq.txt','w') as freq_f:
        for item in token_freq.keys():
            freq_f.write(str(item)+"\n")
            temp1 = str(token_freq[item])
            temp1 = temp1.replace('Counter','')
            temp1 = temp1.replace('(','')
            temp1 = temp1.replace(')','')
            temp1 = temp1.replace('{','')
            temp1 = temp1.replace('}','')
            temp1 = temp1.replace("'",'')
            freq_f.write(temp1+"\n")
        
def merge(index1, index2):
    file1 = open(index1, 'r')
    file2 = open(index2, 'r')
    output_file = open("index3.txt", 'w')

    f1 = file1.readline()
    f2 = file2.readline()
    while True:
        if f1 == '' and f2 == '':
            break
        elif f1 == '' and f2 != '':
            output_file.write(f2)
            output_file.write(file2.readline()+'\n')
            file2.readline()
            f2 = file2.readline()
        elif f1 != '' and f2 == '':
            output_file.write(f1)
            output_file.write(file1.readline()+'\n')
            file1.readline()
            f1 = file1.readline()
        elif f1 < f2:
            output_file.write(f1)
            output_file.write(file1.readline()+'\n')
            file1.readline()
            f1 = file1.readline()
        elif f1 == f2:
            output_file.write(f1)
            output_file.write(file1.readline().strip() + ", ")
            output_file.write(file2.readline()+'\n')
            file1.readline()
            file2.readline()
            f1 = file1.readline()
            f2 = file2.readline()
        elif f1 > f2:
            output_file.write(f2)
            output_file.write(file2.readline()+'\n')
            file2.readline()
            f2 = file2.readline()
    file1.close()
    file2.close()
    output_file.close()


dec_values = set()
dec_values.update(range(48,57+1))
dec_values.update(range(65,90+1))
dec_values.update(range(97,122+1))
def tokenize(s):
    res = []
    p = PorterStemmer()
    for word in s:
        if len(word)>1:
            word = p.stem(word.lower())
            val = checkalnum(word)
            if val:
                res.append(word)
            else:
                continue
    return res


def checkalnum(word):
    for i in range(len(word)):
        if ord(word[i]) not in dec_values:
            return False
    return True


def extract_tokens(file):
    temp = open(file,'r')
    # temp = json.load(temp)
    # soup = BeautifulSoup(temp['content'],'lxml') # this breaks my code because it allows things like făinaru in and i cant encode that
    soup = BeautifulSoup(temp, 'lxml')
    s = soup.get_text()
    results = tokenize(s.split())
    n = len(results)
    # compute and map frequency of each token
    token_freq = Counter(results) #Count frequency
    temp.close()

    #Calculate tf score
    final_res = dict()
    for key in token_freq.keys():
        tf = token_freq[key]/n
        final_res[key] = (token_freq[key],tf) #Ex: Apple: (10, 1.2) where 10 is freq, 1.2 is tf score

    return final_res, token_freq


import math
def build_index(doc_mapping, doc_token, unique_token, count):
#    res = compute() #Returns mapping, doc_token mapping, and unique tokens
    tokens = unique_token #Unique tokens
    mapping = doc_mapping #Document id --> document name mapping
    dt_map = doc_token #document id : {token : (freq, tf)} 
    n = len(unique_token) #Iterate for every unique token
    index = dict()

    for token in tokens:
        token_result = []
        token_count = 0
        '''
        we are building the postings list for token i
        Ex: 
            Loop iterates document ID in range from 0 to number of documents
                On each iteration, we check if the token is in that document
                    If it is, we increment token_count (we need this for idf)
                    Create a temp tuple of the form (doc id, (freq, tf))
                    Append this tuple to the result array 
        '''
        for i in range(count, len(mapping.keys()) + count): #mapping.keys tells us the number of documents 
            doc_tokens = dt_map[i].keys() #Returns {token : (freq, tf)} and then we get just the tokens
            if token in doc_tokens: #If token exists in document
                token_count += 1 #documents with token counter
                temp = (i,dt_map[i][token]) #Create tuple with (doc id, (freq,tf))
                token_result.append(temp) #Add the tuple to list
        #This loop modifies the postings with the idf score.
        '''
        Now that we have an array that tells us all the documents where token i occurs,
            We iterate this array
                Retrieve the stored tuple (freq, tf)
                Calculate the idf by log2(num of docs / num of docs w/ token)
                Overwrite the intial tuple with (doc id, tf * idf)
        After the loop, append this result to the index dictionary where the structure is
            index = {
                            token: [(doc id, tf-idf), (doc id, tf - idf)...]
            }
        '''
        ind = 0
        for item in token_result:
            doc_id = item[0] #get doc_id
            temp_token = item[1] #(freq,tf) of token
            tf = temp_token[1] #get tf score 
            temp = len(mapping.keys())/token_count #num of docs / num of docs with that token 
            idf = math.log(temp,2) #get idf 
            tf_idf = tf*idf
            tf_idf = round(tf_idf, 6)
            token_result[ind] = (doc_id, tf_idf) #set to new tuple 
            ind += 1
        token_result = sorted(token_result,key=lambda tup: tup[0])
        index[token] = token_result
    return index

import time
if __name__ == '__main__':
    if os.path.isfile("index.txt"):
        os.remove("index.txt")
    start = time.time()
    compute()
    end = time.time()
    print(end - start)
