# -*- coding: utf-8 -*-
import pickle

import math
from collections import Counter
from difflib import SequenceMatcher

import numpy as np
import requests
import json
from sklearn.neighbors import NearestNeighbors
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import euclidean_distances
from pyemd import emd
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import CountVectorizer
import time

with open('word2Vec_top70000.p', 'rb') as f:
    word_to_vec = pickle.load(f)

word_to_index = {w : i for i, w in enumerate(word_to_vec.keys())}


def get_vec(w):
    if w in word_to_vec.keys():
        return word_to_vec[w].astype('float32')
    print("WARNING: {} not in vocabulary".format(w))
    return np.zeros(300).astype('float32')

def get_text_in_vocab(text):
    vocab = word_to_vec.keys()
    return " ".join([w for w in text.split()if  w in vocab])

def distance(w1, w2):
    return np.linalg.norm(get_vec(w1) - get_vec(w2))

def get_vec_of_text(text):
    return np.average([get_vec(w) for w in text.split()], axis = 0)

def get_text_distances(text1, text2):
    vec1 = np.average([get_vec(w) for w in text1.split()], axis = 0)
    vec2 = np.average([get_vec(w) for w in text2.split()], axis = 0)
    return np.linalg.norm(vec1 - vec2)

def simplify_text(text):
    data = requests.post('http://textapi.melingo.com/Melingo/TextAnalysis.svc/AnalyzeText/',
                         json={"Query":"{}".format(text), "UserID": "Hackathon2"}).text
    data = json.loads(data)
    return " ".join(x['lemma'] for x in data)


def preprocess_texts(json_path, pickle_path):
    with open(json_path, 'r') as f:
        all_data = json.load(f)
    knn = NearestNeighbors(n_neighbors=5)
    samples = []
    psakim = []
    for psak_i, psak in enumerate(all_data):
        print(psak_i, "/", len(all_data), psak['title'])
        #print(psak['mini'])
        #psak_text = psak['title'] + " " + " ".join(psak['judges']) + " " + psak['mini']
        psak_text = psak['title']+ " " + psak['mini']
        mini_simple = simplify_text(psak_text)
        mini_in_vocav = get_text_in_vocab(mini_simple)
        #psak_vect = get_vec_of_text(mini_simple)
        #samples.append(psak_vect)
        psak['simple'] = mini_in_vocav
        psakim.append(psak)

    with open(json_path, 'w') as f:
        json.dump(psakim, f)
    # knn.fit(samples)
    # with open(pickle_path, 'wb') as f:
    #     pickle.dump((knn, psakim), f)

def get_similar(text, psakim_json='scraping/all_TA.json'):
    N_SIMILAR = 5
    text_simple = simplify_text(text)
    text_in_vocav = get_text_in_vocab(text_simple)
    with open(psakim_json, 'r') as f:
        psakim = json.load(f)
    #psakim = psakim[:10]
    distances = [get_documents_distance(text_in_vocav, psak['simple']) for psak in psakim]
    N_SIMILAR_INDICES = np.argpartition(distances, N_SIMILAR)
    return [psakim[i] for i in N_SIMILAR_INDICES]


def get_cosine(vec1, vec2):
    intersection = set(vec1) & set(vec2)
    return 1.0/(len(intersection) + 1)


def text_to_vector(text):
    words = text.split()
    return Counter(words)

def get_documents_distance(doc1, doc2):
   # print("A")
   #  d1_simple = simplify_text(doc1)
   #  d2_simple = simplify_text(doc2)
   #  # print(d1_simple)
   #  # print(d2_simple)
   #  d1_good = " ".join([w for w in d1_simple.split() if w in word_to_index.keys()])
   #  d2_good = " ".join([w for w in d2_simple.split() if w in word_to_index.keys()])
   #  # print(d1_good)
    # print(d2_good)

    vect = CountVectorizer().fit([doc1, doc2])
    #print("Features:", ", ".join(vect.get_feature_names()))

    v_1, v_2 = vect.transform([doc1, doc2])
    v_1 = v_1.toarray().ravel()
    v_2 = v_2.toarray().ravel()
    # print(v_1, v_2)
    # print("cosine(doc_1, doc_2) = {:.2f}".format(cosine(v_1, v_2)))
    vocab_list = word_to_index.keys()
    vocab_dict = {w: k for k, w in enumerate(vocab_list)}
    # W_ = [np.random.random(300) for w in vect.get_feature_names()]
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
    emd_dis = emd(v_1, v_2, D_)
    #cosine_dis = get_cosine(text_to_vector(doc1), text_to_vector(doc2))


    vect = TfidfVectorizer(min_df=1)

    tfidf = vect.fit_transform([doc1, doc2])

    tokens_distance = 1 - (tfidf * tfidf.T).A[0][1]

    W_EMD = 0.0
    return W_EMD * emd_dis + (1-W_EMD) * tokens_distance
    #print("d(doc_1, doc_2) = {:.2f}".format(emd(v_1, v_2, D_)))


if __name__ == "__main__":
    # with open('word2Vec_top20000.p', 'rb') as f:
    #     word_to_vec = pickle.load(f)
    # text1 = 'היו היתה כיפה אדומה'
    # text2 = 'דני רובין התחפש אליה וכותב על החזה חרא על זאבים'
    # text3 = 'כיפה אדומה היא מגניבה'
    # print(get_text_distances(text1,text2))
    # print(get_text_distances(text1,text3))
    # print(get_text_distances(text2,text3))
    # t1 = simplify_text('הייתכן שלאדם משכיל ורב אשכולות שכמותך תהיינה שאיפות אבסולוטיות שכאלה')
    # t2 = simplify_text('הייתכן שלאדם משכיל ורב אשכולות שכמותך תהיינה שאיפות גדולות שכאלה')
    # t = time.time()
    # print(get_text_distances(t1,t2))
    # print(time.time() - t)

    #preprocess_texts('scraping/all_TA.json', 'knn_psakim_1.p')

    # with open('knn_psakim_1.p', 'rb') as f:
    #     knn, psakim = pickle.load(f)
    #
    text = 'שוחד'
    similar = get_similar(text, 'scraping/all_TA.json')
    print([s['simple'] for s in similar])
    a = 1