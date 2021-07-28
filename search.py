import os

from nltk.stem.porter import PorterStemmer
from numpy import dot
from numpy.linalg import norm


def calcCos(vector1, vector2):
    cosSim = dot(vector1, vector2) / (norm(vector1) * norm(vector2))
    return cosSim



def loadFreq():
    data = {}
    with open('freq.txt') as f:
        for line in f:
            docId = line.rstrip('\n')
            line = f.readline()
            data[docId] = line
    return data


def createVectors(freqData, queryTerms):
    vector1 = []
    vector2 = []
    vectors = []
    countCheck = 0
    for item in freqData.split(','):
        items = item.split(":")
        vector1.append(int(items[1].strip()))
        if items[0].strip() in queryTerms:
            vector2.append(1)
            countCheck = countCheck + 1
        else:
            vector2.append(0)
    while (countCheck < len(queryTerms)):
        vector1.append(0)
        vector2.append(1)
        countCheck = countCheck + 1
    vectors.append(vector1)
    vectors.append(vector2)
    return vectors


def gen_mapping():
    cwd = os.getcwd()
    mapping = {}
    doc_id = 0
    for p, d, f in os.walk(cwd):
        dirname = p.split(cwd)[-1].strip("\\") # get dir
        for file in f:
            if '.json' in file:
                mapping[doc_id] = dirname + '\\' + file
                doc_id += 1
    return mapping

mapping = gen_mapping() #Dictionary holds doc_id --> filename mapping


def parse_posting(line):
    res = []
    for i in range(0,len(line),2):
        doc_id = line[i].strip()
        tfidf = line[i+1].strip()
        res.append((doc_id,tfidf))
    return res

#Read stopwords from text 
def load_stopwords():
    stop_words = set()
    f = open("stopwords.txt","r")
    words = f.read().split("\n")
    for word in words:
        stop_words.add(word)
    return stop_words
stop_words = load_stopwords()
'''
Comments in red = CosineScore implementation
'''
import math
from collections import defaultdict

stop_words = load_stopwords()

def search(query):
    '''
    For each token, retrieve the postings list 
    '''
    og_query = query 
    search_result = {}
    query_terms = query.split(" ")
    temp_posting = ""
    for query in query_terms: #For each query term t
        if query in stop_words:
            continue
        term = PorterStemmer().stem(query.lower())
        file = open('index.txt','r')
        simple_index = open("simple_index.txt", "r") 
        for line in simple_index:
            line = line.split(',')
            if term == line[0]:
                file.seek(int(line[1].strip()))
                file.readline() 
                temp_posting = file.readline().strip('\n').split(',') 
                temp_posting = parse_posting(temp_posting) #Fetch postings list
                search_result[term] = temp_posting
                break
        simple_index.close()
        file.close()

    '''
    1. Get list of just doc_id
    Structure: {token: doc_id}
    '''
    doc_id = {}
    for key in search_result.keys():
        temp = set()
        temp_tfidf = []
        for item in search_result[key]:
            temp.add(item[0])
        doc_id[key] = temp
    '''
    Find the intersection of postings
    '''

    
    if len(search_result.keys()) > 1: #If more than one term
        posting_set = []
        for key in search_result.keys(): #Turn each set into posting
            posting_set.append(doc_id[key])
        search_result = set.intersection(*posting_set) #Compute intersection
    else:
        search_result = doc_id[key]
    search_result = sortResults(search_result, temp_posting)


    tempQuery = []
    for words in query_terms:
        tempQuery.append(PorterStemmer().stem(words.lower()))
    cosineRankings = {}
    for f in search_result:
        vectors = createVectors(freqData[f], tempQuery)
        cosineRankings[f] = calcCos(vectors[0],vectors[1])


      #Print top 5 files 
    counter = 1
    seen_url = set()
    result_url = []
    # scores = sorted(scores.items(), key = lambda x: x[1], reverse=True)
    scores = sorted(cosineRankings.items(), key = lambda  x: x[1], reverse=True)
    for item in scores:
        item = item[0]
        with open(mapping[int(item)]) as f:
            line = f.readline()
            url = json.loads(line)
        temp = url["url"].split('#')[0]
        if temp in seen_url:
            continue
        else:
            seen_url.add(temp)
        result_url.append(temp)
        counter += 1
        if counter > 9:
            break
    #return result_url 
    return result_url


def sortResults(searchResult, postings):
    tempList = {}
    postDict = postingDic(postings)
    for id in searchResult:
        tempList[id] = postDict[id]
    tempList = sorted(tempList, key=tempList.get, reverse=True)
    return tempList


def postingDic(postings):
    temp = {}
    for post in postings:
        temp[post[0]] = post[1]
    return temp

#---TESTING CODE---
import time
import json
freqData = loadFreq() #Load freq.txt Small memory footprint keep in memory











