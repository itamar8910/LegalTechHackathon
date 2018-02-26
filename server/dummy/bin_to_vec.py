
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division, absolute_import, print_function

import pickle
from fastText import load_model
import argparse
import errno

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=("Print fasttext .vec file to stdout from .bin file")
    )
    parser.add_argument(
        "model",
        help="Model to use",
    )
    args = parser.parse_args()

    f = load_model(args.model)
    words = f.get_words()
    print(len(words))
    N_WORDS = 70000
    word_to_vec = {}
    for w in words[:N_WORDS]:
        word_to_vec[w] = f.get_word_vector(w)
    print(words[N_WORDS])
    #exit()
    with open('word2Vec_top{}.p'.format(N_WORDS), 'wb') as f:
        pickle.dump(word_to_vec, f)

    # print(str(len(words)) + " " + str(f.get_dimension()))
    # for w in words:
    #     v = f.get_word_vector(w)
    #     vstr = ""
    #     for vi in v:
    #         vstr += " " + str(vi)
    #     try:
    #         print(w + vstr)
    #     except IOError as e:
    #         if e.errno == errno.EPIPE:
    #             pass