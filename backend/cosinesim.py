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
    firstID = ""
    rest = ""

    if title == "" or abstract == "":
        return

    if "\n" in ids:
        firstID, rest = ids.split("\n", 1)
    else:
        firstID = ids

    link = "https://pubmed.ncbi.nlm.nih.gov/" + firstID + "/"

    if abstract == None:
        abstract = ""
    corpus.append(abstract)
    
    articleMap[abstract] = (title, link, firstID)
    
def process_articles_multithread(df, corpus, articleMap):
    threads = []
    for index, article in df.iterrows():
        thread = threading.Thread(target=process_article, args=(article, corpus, articleMap))
        thread.start()
        threads.append(thread)
        #time.sleep(0.4) # change?

    for thread in threads:
        thread.join()

def search(words):
    start = time.perf_counter()
    count_vect = CountVectorizer()

    pubmed = PubMed(tool="PubSearch", email="yjc22@cornell.edu")
    q = words
    query = (
        '(("1970/01/01"[Date - Create] : "2023"[Date - Create])) AND ffrft[Filter] AND hasabstract AND '
        + words
    )

    results = pubmed.query(query, max_results=50)
    #start1 = time.perf_counter()
    #print(start1-start)

    dflist = []

    resultdf = pd.DataFrame([item.toDict() for item in results])

    dflist.append(resultdf)
    df = pd.concat(dflist)

    df = df.drop_duplicates(subset=["abstract"], keep="last").reset_index(drop=True)

    corpus = []
    articleMap = OrderedDict()
    #citations_count = {}
    corpus.append(q)
    #added = time.perf_counter()
    #print(added-start)

    process_articles_multithread(df, corpus, articleMap)

    #end = time.perf_counter()
    #print(end-start)
    X_train_counts = count_vect.fit_transform(corpus)

    if X_train_counts.shape[0] > 1:
        svd = TruncatedSVD(n_components=2, random_state=42)
        X_svd = svd.fit_transform(X_train_counts)

        singular_values = svd.singular_values_
        threshold = 0.5  # Set your threshold
        important_indices = np.where(singular_values > threshold)[0]

        X_filtered = np.dot(
            X_svd[:, important_indices], np.diag(singular_values[important_indices])
        )

        query_vector = count_vect.transform([words])
        query_svd = svd.transform(query_vector)
        query_filtered = np.dot(
            query_svd[:, important_indices], np.diag(singular_values[important_indices])
        )

        #end2 = time.perf_counter()
        #print(end2-start)
        similarity = cosine_similarity(query_filtered.reshape(1, -1), X_filtered)

        sims = []
        for a in range(1, len(similarity[0])):
            sims.append(similarity[0][a])

        sorter = []

        ctr = 0
        for a in articleMap:
            sorter.append(
                (
                    sims[ctr],
                    articleMap[a][0],
                    articleMap[a][1],
                    a,
                    articleMap[a][2],
                    #citations_count[a],
                )
            )
            ctr += 1

        sorted_array = sorted(sorter)

        results = []
        for a in range(min(len(sorted_array), 5)):
            abstract_lines = sorted_array[a][3].split(".")
            abstract_final = ""
            for i in range(min(10, len(abstract_lines))):
                abstract_final += abstract_lines[i]

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
            #print((sorted_array[a][1] + "@" + sorted_array[a][2]) + "\n")
        #end3 = time.perf_counter()
        #print(end3-start)
        return results
    else:
        return []
