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
import re


app = Flask(__name__)


Entrez.email = "vb272@cornell.edu"
stop_words = {
    "i",
    "me",
    "my",
    "myself",
    "we",
    "our",
    "ours",
    "ourselves",
    "you",
    "your",
    "yours",
    "yourself",
    "yourselves",
    "he",
    "him",
    "his",
    "himself",
    "she",
    "her",
    "hers",
    "herself",
    "it",
    "its",
    "itself",
    "they",
    "them",
    "their",
    "theirs",
    "themselves",
    "what",
    "which",
    "who",
    "whom",
    "this",
    "that",
    "these",
    "those",
    "am",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "have",
    "has",
    "had",
    "having",
    "do",
    "does",
    "did",
    "doing",
    "a",
    "an",
    "the",
    "and",
    "but",
    "if",
    "or",
    "because",
    "as",
    "until",
    "while",
    "of",
    "at",
    "by",
    "for",
    "with",
    "about",
    "against",
    "between",
    "into",
    "through",
    "during",
    "before",
    "after",
    "above",
    "below",
    "to",
    "from",
    "up",
    "down",
    "in",
    "out",
    "on",
    "off",
    "over",
    "under",
    "again",
    "further",
    "then",
    "once",
    "here",
    "there",
    "when",
    "where",
    "why",
    "how",
    "all",
    "any",
    "both",
    "each",
    "few",
    "more",
    "most",
    "other",
    "some",
    "such",
    "no",
    "nor",
    "not",
    "only",
    "own",
    "same",
    "so",
    "than",
    "too",
    "very",
    "s",
    "t",
    "can",
    "will",
    "just",
    "don",
    "should",
    "now",
}


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

    corpus.append(keywords + title)

    articleMap[keywords + title] = (title, link, abstract, firstID)


def process_articles_multithread(df, corpus, articleMap):
    threads = []
    for index, article in df.iterrows():
        thread = threading.Thread(
            target=process_article, args=(article, corpus, articleMap)
        )
        thread.start()
        threads.append(thread)
        # time.sleep(0.4) # change?

    for thread in threads:
        thread.join()


def search(words, sy, ey, author):
    start = time.perf_counter()
    count_vect = CountVectorizer()

    pubmed = PubMed(tool="PubSearch", email="yjc22@cornell.edu")

    query = "hasabstract AND English[Language]"

    if author != "":
        query += " AND " + author + " [Author]"

    if sy == "":
        sy = "1900"
    if ey == "2024":
        ey = "3000"
    sy = int(sy)
    ey = int(ey)

    # Define the number of eras
    num_eras = 5
    era_length = (ey - sy) // num_eras
    results = []

    # Query for each era
    for i in range(num_eras):
        start_year = sy + i * era_length
        end_year = start_year + era_length
        if i == num_eras - 1:
            end_year = ey  # Ensure the last era reaches the end year

        era_query = f"{query} AND ({start_year}[Date - Publication] : {end_year}[Date - Publication]) AND {words}"
        era_results = pubmed.query(
            era_query, max_results=10
        )  # Adjust number if necessary
        results.extend(era_results)

    dflist = []

    resultdf = pd.DataFrame([item.toDict() for item in results])

    dflist.append(resultdf)
    df = pd.concat(dflist)

    df = df.drop_duplicates(subset=["abstract"], keep="last").reset_index(drop=True)

    corpus = []
    articleMap = OrderedDict()
    # citations_count = {}
    corpus.append(words)
    # added = time.perf_counter()
    # print(added-start)

    process_articles_multithread(df, corpus, articleMap)

    # end = time.perf_counter()
    # print(end-start)
    X_train_counts = count_vect.fit_transform(corpus)

    sims = []
    for a in range(1, len(corpus)):
        sims.append(
            jaccard_score(
                X_train_counts[0].toarray()[0],
                # query_svd,
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
                articleMap[a][3],
                # citations_count[a],
            )
        )
        ctr += 1

    sorted_array = sorted(sorter, reverse=True)
    return sorted_array


def highlight_words(text, query):
    query_words = set(preprocess_text(query).split())

    highlighted_text = " ".join(
        [
             word if word.lower() in query_words else word
            for word in text.split()
        ]
    )
    return highlighted_text


def get_context_lines(lines, best_idx, num_lines=3):
    start = max(0, best_idx - num_lines)
    end = min(len(lines), best_idx + num_lines + 1)
    return lines[start:end]


##helper to return the top 5 results
def getTop5(query, sy, ey, author, irrelevant_titles):

    sorted_array = search(query, sy, ey, author)
    new_sorted_array = []
    for a in range(len(sorted_array)):
        if sorted_array[a][1] not in irrelevant_titles:
            new_sorted_array.append(sorted_array[a])
    results = []
    for a in range(min(len(new_sorted_array), 5)):
        abstract = new_sorted_array[a][3]
        abstract_lines = abstract.split(". ")
        vectorizer = CountVectorizer().fit([query] + abstract_lines)
        query_vec = vectorizer.transform([query])
        line_vecs = vectorizer.transform(abstract_lines)

        similarities = cosine_similarity(query_vec, line_vecs).flatten()
        best_idx = np.argmax(similarities)
        best_line = abstract_lines[best_idx]
        for i in range(len(abstract_lines)):
            abstract_lines[i] = (abstract_lines[i] + ".")
        abstract_lines[best_idx] = ("***" + best_line + "***.")
        print("best_line: \n" + best_line)
        context_lines = get_context_lines(abstract_lines, best_idx, 3)

        highlighted_context = highlight_words(" ".join(context_lines), query)

        citation_query = Entrez.read(
            Entrez.elink(
                dbfrom="pubmed",
                db="pmc",
                LinkName="pubmed_pubmed_citedin",
                from_uid=new_sorted_array[a][4],
            )
        )
        if citation_query and citation_query[0]["LinkSetDb"]:
            citations = str(len(citation_query[0]["LinkSetDb"][0]["Link"]))
        else:
            citations = "0"

        results.append(
            (
                new_sorted_array[a][1]
                + "@"
                + new_sorted_array[a][2]
                + "@"
                + highlighted_context
                + "@"
                + citations
            )
        )
        # print(sorted_array[a][1] + "@" + sorted_array[a][2] +"\n")

    # print("Done search!")
    return results


def preprocess_text(text):
    # Convert to lower case
    text = text.lower()
    # Remove special characters
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = " ".join([word for word in text.split() if word not in stop_words])
    return text


def tokenize(text):
    return text.split()


def create_count_vector(query, text):
    # Preprocess and tokenize both query and text
    query_words = tokenize(preprocess_text(query))
    text_words = tokenize(preprocess_text(text))

    # Create a dictionary to count occurrences of each query word in the text
    count_dict = dict.fromkeys(query_words, 0)
    for word in text_words:
        if word in count_dict:
            count_dict[word] += 1

    print("done making vectors!")
    # Return counts in the order of words in the query
    return [count_dict[word] for word in query_words]


def rocchio(
    words,
    relevant_indices,
    irrelevant_indices,
    sy,
    ey,
    author,
):
    """
    This function implements the Rocchio algorithm for relevance feedback.

    Args:
            words (str): The query words, a string.
            relevant_indices (list): Indices of relevant documents.
            irrelevant_indices (list): Indices of irrelevant documents.
            sorted_array (list): A list containing details of each document, including abstracts.
            sy, ey (str): Start and end years for the query.
            author (str): Author filter for the query.

    Returns:
            The search results based on the adjusted query from Rocchio algorithm.
    """
    # Get the abstract for each relevant and irrelevant document

    # issue: if filters are changed, this returns completely diff results. Store sorted array as a global variable that gets updated during search so that
    # it is called only once initially. ex. sorted array = [] at the top, and then sorted array = results before the return at the end of search
    # make sure to pass in filter info. Then, get word count vector for each abstract marked relevant/irrelevant and perform rocchios. Search should only be called once (also for efficiency)
    sorted_array = search(words, sy, ey, author)
    abstracts = [None] * 20
    print(len(sorted_array))
    for a in range(len(sorted_array)):
        abstracts[a] = sorted_array[a][3]  ##THIS IS WHERE THE ABSTRACTs IS STORED
    print("ABSTRACT LENGTH" + str(len(abstracts)))
    # now these lists contain the raw, unprocesssed texts for each irrelevant and relevant abstract
    relevant_abstracts = [abstracts[i] for i in relevant_indices]
    irrelevant_abstracts = [abstracts[i] for i in irrelevant_indices]

    # Extract abstracts for relevance feedback
    relevant_abstracts = [sorted_array[i][3] for i in relevant_indices]
    irrelevant_abstracts = [sorted_array[i][3] for i in irrelevant_indices]

    irrelevant_titles = [sorted_array[i][1] for i in irrelevant_indices]
    print(irrelevant_titles)

    # Parameters for Rocchio algorithm
    alpha = 1.0
    beta = 1.0
    gamma = 0.8

    # Create the initial query vector from the original query words
    query_vector = create_count_vector(words, words)

    # Create vectors for relevant and irrelevant documents
    relevant_vectors = np.array(
        [create_count_vector(words, abstract) for abstract in relevant_abstracts]
    )
    irrelevant_vectors = np.array(
        [create_count_vector(words, abstract) for abstract in irrelevant_abstracts]
    )

    # Calculate centroids for relevant and irrelevant vectors
    relevant_centroid = (
        np.mean(relevant_vectors, axis=0)
        if len(relevant_vectors) > 0
        else np.zeros(len(query_vector))
    )
    irrelevant_centroid = (
        np.mean(irrelevant_vectors, axis=0)
        if len(irrelevant_vectors) > 0
        else np.zeros(len(query_vector))
    )

    # Apply Rocchio algorithm to adjust the query vector
    new_query_vector = (
        alpha * np.array(query_vector)
        + beta * relevant_centroid
        - gamma * irrelevant_centroid
    )

    # Convert the new query vector back to a string query
    query_words = tokenize(preprocess_text(words))
    new_query = " ".join(
        [word for word, count in zip(query_words, new_query_vector) if count > 0]
    )
    print(new_query)
    # Perform the search with the new query
    return getTop5(new_query, sy, ey, author, irrelevant_titles)


"""if __name__ == "__main__":
	search("mental health and artifical intelligence","","","")
	getTop5("mental health and artifical intelligence","","","")"""
