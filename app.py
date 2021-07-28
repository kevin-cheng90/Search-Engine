from flask import Flask, request, request, render_template
from flask_restful import Resource, Api
import os, sys
sys.path.insert(1, os.getcwd() + '/DEV') # add path for search.py
import search

app = Flask(__name__)

# ROUTES
@app.route('/', methods=['GET', 'POST'])
def call_search():
    """
    URL : /
    Query engine to find a list of relevant URLs.
    Method : POST or GET (no query)
    Form data :
        - query : the search query
        - hits : the number of hits returned by query
        - start : the start of hits
    Return a template view with the list of relevant URLs.
    """
    if request.method == 'POST':
        
        # print(search_script_path)
        query = request.form.get('search')

        #---TESTING CODE---
        import time
        import json
        start = time.time()
        # Queries we need to test for M2:
        #   - cristina lopes
        #   - machine learning
        #   - ACM
        #   - master of software engineering
        res = search.search(query)
        # print(query)
        end = time.time()
        print(f"Time taken to search index for ({query}) = " + str(end-start))
        #---END TESTING CODE---

        #Print top 5 files 
        counter = 1
        seen_url = set()
        for item in res:
            seen_url.add(item)
            if counter > 9:
                break
        seen_url = list(seen_url)
        print(seen_url)
        return render_template("index.html", term=query, top_5=seen_url, time=round(end-start, 4))
    # else, get request
    return render_template("index.html", term=None, res=None)

if __name__ == '__main__':
     app.run()
