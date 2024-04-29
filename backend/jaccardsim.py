# pylint: disable=invalid-name
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

# # Route to handle incoming data
# @app.route('/send-data', methods=['POST'])
# def receive_data():
#     # Get data from the request
#     data = request.get_json()


#     # Return a response
#     return jsonify(processed_data)

# if __name__ == '__main__':
#     app.run(debug=True)

results_array = []

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

    if title == "" or abstract == "":
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
    results_array = sorted_array
    return sorted_array

    # results = []
    # for a in range(min(len(sorted_array), 10)):
    #     abstract_lines = sorted_array[a][3].split(".")
    #     abstract_final = ""
    #     for i in range(min(10, len(abstract_lines))):
    #         abstract_final += abstract_lines[i]

    #     citation_query = Entrez.read(
    #     Entrez.elink(
    #         dbfrom="pubmed",
    #         db="pmc",
    #         LinkName="pubmed_pubmed_citedin",
    #         from_uid=sorted_array[a][4],
    #         )
    #     )
    #     if citation_query and citation_query[0]["LinkSetDb"]:
    #         citations = str(len(citation_query[0]["LinkSetDb"][0]["Link"]))
    #     else:
    #         citations = "0"

    #     results.append(
    #         (
    #             sorted_array[a][1]
    #             + "@"
    #             + sorted_array[a][2]
    #             + "@"
    #             + abstract_final
    #             + "@"
    #             + citations
    #         )
    #     )
    #     print(sorted_array[a][1] + "@" + sorted_array[a][2] +"\n")
    # return results

# if __name__ == "__main__":
#     search("mental health and artificial intelligence")


##helper to return the top 5 results
def getTop5(query, sy, ey, author):
    sorted_array = search(query, sy, ey, author)
    results = []
    for a in range(min(len(sorted_array), 10)):
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
       # print(sorted_array[a][1] + "@" + sorted_array[a][2] +"\n")
        print("THE SORTED RESULTS LENGTH" + sorted_array[a][3] + "\n")
        print ("SHAPE" + str(len(sorted_array)))
    return results



def rocchio(words, relevant_indices, irrelevant_indices, sy, ey, author):
    """
    This function implements the Rocchio algorithm for relevance feedback.

    Args:
        words (str): The query words.
        relevant_indices (list): The indices of relevant documents.
        irrelevant_indices (list): The indices of irrelevant documents.

    Returns:
        list: The search results based on the Rocchio algorithm.
    """
    # Create a CountVectorizer object to get the term vectors
    count_vect = CountVectorizer()
    # Get the abstract for each relevant and irrelevant document

    # issue: if filters are changed, this returns completely diff results. Store sorted array as a global variable that gets updated during search so that
    # it is called only once initially. ex. sorted array = [] at the top, and then sorted array = results before the return at the end of search
    #make sure to pass in filter info. Then, get word count vector for each abstract marked relevant/irrelevant and perform rocchios. Search should only be called once (also for efficiency)
    sorted_array = results_array
    abstracts = [None] * 20
    for a in range(20):
        print(len(abstracts))
        abstracts[a] = (sorted_array[a][3]) ##THIS IS WHERE THE ABSTRACT IS STORED

    relevant_abstracts = [abstracts[i] for i in relevant_indices]
    irrelevant_abstracts = [abstracts[i] for i in irrelevant_indices]

	# Calculate term vectors based on the query
    query_vector = count_vect.transform([words]).toarray()[0]

	# Calculate term vectors for relevant and irrelevant documents
    relevant_vectors = [count_vect.transform([abstract]).toarray()[0] for abstract in relevant_abstracts]
    irrelevant_vectors = [count_vect.transform([abstract]).toarray()[0] for abstract in irrelevant_abstracts]

    # Calculate the centroid of the relevant and irrelevant documents
    relevant_centroid = np.mean(relevant_vectors, axis=0)
    irrelevant_centroid = np.mean(irrelevant_vectors, axis=0)

    # Calculate the new query vector based on the Rocchio algorithm
    alpha = 1.0  # Weight for the original query vector
    beta = 0.8  # Weight for the relevant centroid vector
    gamma = 0.2  # Weight for the irrelevant centroid vector

    new_query_vector = alpha * query_vector + beta * relevant_centroid - gamma * irrelevant_centroid

    # Convert the new query vector back to a string query
    new_query = ' '.join([word for word, count in zip(count_vect.get_feature_names(), new_query_vector) if count > 0])

    # Perform the search with the new query
    results = search(new_query, sy, ey, author)

    return results
