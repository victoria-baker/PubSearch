from pymed import PubMed
import pandas as pd
import sklearn
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import jaccard_score
from flask import Flask, request, jsonify


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


def search(words): 

	count_vect = CountVectorizer()

	pubmed = PubMed(tool="PubSearch", email="yjc22@cornell.edu")

	q = words
	query =  '(("1970/01/01"[Date - Create] : "2040"[Date - Create])) AND '+words

	results = pubmed.query(query, max_results=10)

	dflist = []

	resultdf = pd.DataFrame([item.toDict() for item in results])
	#resultdf = resultdf[resultdf.abstract.notna()]

	dflist.append(resultdf)
	df = pd.concat(dflist)

	#d = df.drop_duplicates(subset = ['abstract'], keep = 'last').reset_index(drop = True)

	corpus = []
	articleMap = {}
	corpus.append(q)


	for index, article in df.iterrows():
		abstract = article['abstract']
		title = article['title']
		authors = article['authors']
		ids = article['pubmed_id']
		firstID = ""
		rest = ""

		if '\n' in ids:
			firstID, rest = ids.split('\n', 1)
		else:
			firstID = ids

		#print(firstID)
		link = "https://pubmed.ncbi.nlm.nih.gov/"+firstID+"/"

		print("title:", title)
		print("abstract:",abstract)
		if abstract == None:
			abstract = ''
		corpus.append(abstract)
		articleMap[abstract] = (title,link)


	X_train_counts = count_vect.fit_transform(corpus)

	print("WE MADE IT")

	pd.DataFrame(X_train_counts.toarray(),columns=count_vect.get_feature_names_out())


	similarity = cosine_similarity(X_train_counts[0:1], X_train_counts)

	sims = []
	for a in range(1,len(similarity[0])):
		sims.append(similarity[0][a])

	sorter = []

	for a in range(1,len(corpus)):
		sorter.append((sims[a-1],articleMap[corpus[a]][0],articleMap[corpus[a]][1],corpus[a]))

	sorted_array = sorted(sorter)


	results = []
	for a in range(len(sorted_array)):
		results.append((sorted_array[a][1]+" "+sorted_array[a][2]))
		#results.append({'result': sorted_array[a][1] + " " + sorted_array[a][2]})

	print("DONE with COSINE")
	return results
