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
	query =  '(("1970/01/01"[Date - Create] : "2040"[Date - Create])) AND ffrft[Filter] AND '+words

	results = pubmed.query(query, max_results=50)

	dflist = []

	resultdf = pd.DataFrame([item.toDict() for item in results])
	#resultdf = resultdf[resultdf.abstract.notna()]

	dflist.append(resultdf)
	df = pd.concat(dflist)

	df = df.drop_duplicates(subset = ['abstract'], keep = 'last').reset_index(drop = True)

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

		if title == "" or abstract == "":
			continue

		if '\n' in ids:
			firstID, rest = ids.split('\n', 1)
		else:
			firstID = ids

		#print(firstID)
		link = "https://pubmed.ncbi.nlm.nih.gov/"+firstID+"/"

	
		if abstract == None:
			abstract = ''
		corpus.append(abstract)
		articleMap[abstract] = (title,link)

	X_train_counts = count_vect.fit_transform(corpus)

	if X_train_counts.shape[0] > 1:
		svd = TruncatedSVD(n_components=2, random_state=42)
		X_svd = svd.fit_transform(X_train_counts)

		singular_values = svd.singular_values_
		threshold = 0.5  # Set your threshold
		important_indices = np.where(singular_values > threshold)[0]

		X_filtered = np.dot(X_svd[:, important_indices], np.diag(singular_values[important_indices]))

		query_vector = count_vect.transform([words])  
		query_svd = svd.transform(query_vector)
		query_filtered = np.dot(query_svd[:, important_indices], np.diag(singular_values[important_indices]))

		similarity = cosine_similarity(query_filtered.reshape(1, -1), X_filtered)

		sims = []
		for a in range(1,len(similarity[0])):
			sims.append(similarity[0][a])

		sorter = []

		for a in range(1,len(corpus)):
			sorter.append((sims[a-1],articleMap[corpus[a]][0],articleMap[corpus[a]][1],corpus[a]))

		sorted_array = sorted(sorter)


		results = []
		for a in range(min(len(sorted_array),10)):
			results.append((sorted_array[a][1]+"@"+sorted_array[a][2]))
			print((sorted_array[a][1]+"@"+sorted_array[a][2])+"\n")
		return results
	else:
		return []

	
