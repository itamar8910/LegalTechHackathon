from scipy.spatial.distance import cosine
import os
from sklearn.metrics import euclidean_distances
import numpy as np
from pyemd import emd
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import CountVectorizer
#from sklearn.cross_validation import train_test_split

d1 = "Obama speaks to the media in Illinois"
d2 = "The President addresses the press in Chicago"

vect = CountVectorizer().fit([d1, d2])
print("Features:",  ", ".join(vect.get_feature_names()))

v_1, v_2 = vect.transform([d1, d2])
v_1 = v_1.toarray().ravel()
v_2 = v_2.toarray().ravel()
#print(v_1, v_2)
#print("cosine(doc_1, doc_2) = {:.2f}".format(cosine(v_1, v_2)))

W_ = [np.random.random(300) for w in vect.get_feature_names()]
#W_ = W[[vocab_dict[w] for w in vect.get_feature_names()]]
D_ = euclidean_distances(W_)
print("d(addresses, speaks) = {:.2f}".format(D_[0, 7]))
print("d(addresses, chicago) = {:.2f}".format(D_[0, 1]))

# pyemd needs double precision input
v_1 = v_1.astype(np.double)
v_2 = v_2.astype(np.double)
v_1 /= v_1.sum()
v_2 /= v_2.sum()
D_ = D_.astype(np.double)
D_ /= D_.max()  # just for comparison purposes
print("d(doc_1, doc_2) = {:.2f}".format(emd(v_1, v_2, D_)))

