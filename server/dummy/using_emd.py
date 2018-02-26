import os

import pickle
from sklearn.metrics import euclidean_distances
import numpy as np
from pyemd import emd
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import CountVectorizer
import requests
import json
from scipy.spatial import distance_matrix

def simplify_text(text):
    data = requests.post('http://textapi.melingo.com/Melingo/TextAnalysis.svc/AnalyzeText/',
                         json={"Query":"{}".format(text), "UserID": "Hackathon2"}).text
    data = json.loads(data)
    return " ".join(x['lemma'] for x in data)

d1 = "אני הלכתי לקניות"
d2 = "אני מאוד רוצה לרוץ"

with open('../word2Vec_top70000.p', 'rb') as f:
    word_to_vec = pickle.load(f)
word_to_index = {w : i for i, w in enumerate(word_to_vec.keys())}

d1_simple = simplify_text(d1)
d2_simple = simplify_text(d2)
print(d1_simple)
print(d2_simple)
d1_good = " ".join([w for w in d1_simple.split() if w in word_to_index.keys()])
d2_good = " ".join([w for w in d2_simple.split() if w in word_to_index.keys()])
print(d1_good)
print(d2_good)

vect = CountVectorizer().fit([d1_good, d2_good])
print("Features:",  ", ".join(vect.get_feature_names()))

v_1, v_2 = vect.transform([d1_good, d2_good])
v_1 = v_1.toarray().ravel()
v_2 = v_2.toarray().ravel()
#print(v_1, v_2)
#print("cosine(doc_1, doc_2) = {:.2f}".format(cosine(v_1, v_2)))
vocab_list = word_to_index.keys()
vocab_dict = {w: k for k, w in enumerate(vocab_list)}
#W_ = [np.random.random(300) for w in vect.get_feature_names()]
W_ = [word_to_vec[w] for w in vect.get_feature_names()]
D_ = euclidean_distances(W_)
# print("d(addresses, speaks) = {:.2f}".format(D_[0, 7]))
# print("d(addresses, chicago) = {:.2f}".format(D_[0, 1]))

# pyemd needs double precision input
v_1 = v_1.astype(np.double)
v_2 = v_2.astype(np.double)
v_1 /= v_1.sum()
v_2 /= v_2.sum()
D_ = D_.astype(np.double)
D_ /= D_.max()  # just for comparison purposes
print("d(doc_1, doc_2) = {:.2f}".format(emd(v_1, v_2, D_)))

