from pymed import PubMed
import pandas as pd
from Bio import Entrez
from Bio import Medline
import sklearn
import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import jaccard_score
from flask import Flask, request, jsonify
import time
import concurrent.futures
import threading
from collections import OrderedDict


app = Flask(__name__)

# Route to handle incoming data
@app.route('/send-data', methods=['POST'])
def receive_data():
    # Get data from the request
    data = request.get_json()


    # Return a response
    return jsonify(processed_data)

if __name__ == '__main__':
    app.run(debug=True)

Entrez.email = "vb272@cornell.edu"

def process_article(article, corpus, articleMap):
    abstract = article["abstract"]
    title = article["title"]
    authors = article["authors"]
    ids = article["pubmed_id"]

    keywords = ""
    if not isinstance(article["keywords"], float):
        keywords = '","'.join(filter(None, article.get("keywords", [])))


    firstID = ""
    rest = ""

    if title == "" or len(abstract) < 20:
        return

    if "\n" in ids:
        firstID, rest = ids.split("\n", 1)
    else:
        firstID = ids

    link = "https://pubmed.ncbi.nlm.nih.gov/" + firstID + "/"

    if abstract == None:
        abstract = ""

    corpus.append(keywords+title)
    
    articleMap[keywords+title] = (title, link, abstract, firstID)
    
def process_articles_multithread(df, corpus, articleMap):
    threads = []
    for index, article in df.iterrows():
        thread = threading.Thread(target=process_article, args=(article, corpus, articleMap))
        thread.start()
        threads.append(thread)
        #time.sleep(0.4) # change?

    for thread in threads:
        thread.join()

def search(words, sy, ey, author):
    start = time.perf_counter()
    count_vect = CountVectorizer()

    pubmed = PubMed(tool="PubSearch", email="yjc22@cornell.edu")
    
    query = ('hasabstract')

    if author != "":
    	query += ' AND ' + author + ' [Author]'

    if sy == "":
    	sy = "1900"
    if ey == "":
    	ey = "3000"

    query += ' AND ('+sy+'[Date - Publication] : '+ey+'[Date - Publication])'
    query += ' AND '+words


    results = pubmed.query(query, max_results=20) #500

    dflist = []

    resultdf = pd.DataFrame([item.toDict() for item in results])

    dflist.append(resultdf)
    df = pd.concat(dflist)

    df = df.drop_duplicates(subset=["abstract"], keep="last").reset_index(drop=True)

    corpus = []
    articleMap = OrderedDict()
    #citations_count = {}
    corpus.append(words)
    #added = time.perf_counter()
    #print(added-start)

    process_articles_multithread(df, corpus, articleMap)

    #end = time.perf_counter()
    #print(end-start)
    X_train_counts = count_vect.fit_transform(corpus)

 
    sims = []
    for a in range(1, len(corpus)):
        sims.append(
            jaccard_score(
                X_train_counts[0].toarray()[0],
                #query_svd,
                X_train_counts[a].toarray()[0],
                average="macro",
            )
        )

    sorter = []
    ctr = 0

    for a in articleMap:
        sorter.append(
            (
                sims[ctr],
                articleMap[a][0],
                articleMap[a][1],
                articleMap[a][2],
                articleMap[a][3]
                #citations_count[a],
            )
        )
        ctr+=1

    sorted_array = sorted(sorter)

    results = []
    for a in range(min(len(sorted_array), 10)):
        abstract_lines = sorted_array[a][3].split(".")
        abstract_final = ""
        for i in range(min(10, len(abstract_lines))):
            abstract_final += abstract_lines[i]
        abstract_final += "..."

        citation_query = Entrez.read(
        Entrez.elink(
            dbfrom="pubmed",
            db="pmc",
            LinkName="pubmed_pubmed_citedin",
            from_uid=sorted_array[a][4],
            )
        )
        if citation_query and citation_query[0]["LinkSetDb"]:
            citations = str(len(citation_query[0]["LinkSetDb"][0]["Link"]))
        else:
            citations = "0"

        results.append(
            (
                sorted_array[a][1]
                + "@"
                + sorted_array[a][2]
                + "@"
                + abstract_final
                + "@"
                + citations
            )
        )
        print(sorted_array[a][1] +" "+ abstract_final+"\n")
    return results

'''if __name__ == "__main__":
    search("mental health and artificial intelligence", "", "", "")'''
