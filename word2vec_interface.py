# -*- coding: utf-8 -*-
"""
Created on Sun Apr 26 17:53:38 2015

@author: andy
"""

import gensim
import hansard_fetcher as fetcher

WORDVECS = 'temporary/GoogleNews-vectors-negative300.bin'

def load_wordvecs():
    return gensim.models.Doc2Vec.load_word2vec_format(WORDVECS, binary=True)
    
def get_test_sentences():
    speeches = fetcher.load_test_speeches()
    text = fetcher.get_text_by_speaker(speeches)
    
    results = []
    for sid, sentences in text.iteritems():
        for sentence in sentences:
            words = gensim.utils.to_unicode(sentence).split()
            labelled_sentence = gensim.models.doc2vec.LabeledSentence(words, [sid])
            results.append(labelled_sentence)
            
    return results