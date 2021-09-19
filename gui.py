from os import remove
from flask import Flask, render_template, jsonify, request
import csv
from flask_mysqldb import MySQL
from flask_paginate import Pagination, get_page_args

import pandas as pd
import re
import nltk
import csv
import matplotlib.pyplot as plt
import sklearn.svm

from nltk.corpus import stopwords
from nltk import word_tokenize
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
import emoji

import string
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.svm import LinearSVC
from nltk.classify import SklearnClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
import pickle

import sys
import json
import base64

app = Flask(__name__)

@app.route("/")
def main(): #fungsi yang akan dijalankan ketike route dipanggil
    return render_template('index.html')

@app.route("/input2", methods=['GET', 'POST'])
def input2():   
    with open('newfingbanget_backup.csv', encoding= 'unicode_escape') as csv_file:
        data = csv.reader(csv_file, delimiter=',')
        first_line = True
        dataset = []
        for row in data:
            if not first_line:
                dataset.append({
                "komentar": row[0],
                "sentimen": row[1],
                "label": row[2]
                })
            else:
                first_line = False
    return render_template('input2.html', menu='input2', submenu='data', dataset=dataset)
 
@app.route("/homee")
def homee():
    return render_template('homee.html')

@app.route("/grfk")
def grfk():
    return render_template('grfk.html')

@app.route("/inputdatauji")
def inputdatauji():
    return render_template('inputdatauji.html')   

@app.route('/hasiluji', methods=["GET"])
def hasiluji(): 

    subject = request.args.get("sub")
    subject = [subject]

    result = {}

    def case_folding(tokens): 
        return tokens.lower()

    test_casefolding=[]
    for i in range(0, len(subject)):
        test_casefolding.append(case_folding(subject[i]))
        
    result['casefolding'] = ' '.join(list(map(lambda x: str(x), test_casefolding)))
    casefolding = result['casefolding']

    def remove_num(text):  
        text_nonum = ''
        text_nonum = re.sub(r'\d+',' ', text)
        return text_nonum
    
    test_removenum=[]
    for i in range(0,len(test_casefolding)):
        test_removenum.append(remove_num(test_casefolding[i]))

    result ['remove_num'] = ' '.join(list(map(lambda x: str(x), test_removenum)))
    removenum = result ['remove_num']

    def remove_punct(text):
        text_nopunct = ''
        text_nopunct = re.sub('['+string.punctuation+']', ' ', text)
        return text_nopunct

    test_removepunct=[]
    for i in range(0,len(test_removenum)):
	    test_removepunct.append(remove_punct(test_removenum[i]))
    
    result['removepunct'] = ' '.join(list(map(lambda x: str(x), test_removepunct)))
    removepunct = result['removepunct']
   

    def open_kamus_prepro(x):
        kamus={}
        with open(x,'r') as file :
            for line in file :
                slang=line.replace("'","").split(':')
                kamus[slang[0].strip()]=slang[1].rstrip('\n').lstrip()
        return kamus

    kamus_slang = open_kamus_prepro('Kamus spelling_word.txt')

    def slangword(text):
        sentence_list = text.split()
        new_sentence = []
        
        for word in sentence_list:
            for candidate_replacement in kamus_slang:
                if candidate_replacement == word:
                    word = word.replace(candidate_replacement, kamus_slang[candidate_replacement])
            new_sentence.append(word)
        return " ".join(new_sentence)

    test_slangword=[]
    for i in range(0,len(test_removepunct)):
        test_slangword.append(slangword(test_removepunct[i]))

    slangword_ = test_slangword

    result['hasil_token'] = [word_tokenize(sen) for sen in test_slangword]
    hasil_token = result['hasil_token']

    kamus_stopword=[]
    with open('Kamus stopword.txt','r') as file :
        for line in file :
            slang=line.replace("'","").strip()
            kamus_stopword.append(slang)

    def remove_stop_words(tokens):
        return [word for word in tokens if word not in kamus_stopword]

    stopword= [remove_stop_words(sen) for sen in hasil_token] 

    result['remove_stop_words'] = ' '.join(list(map(lambda x: str(x), stopword)))
    remove_stop_words = result['remove_stop_words']


    factory = StemmerFactory()
    stemmer = factory.create_stemmer()

    def stemming(tokens):  
        data_stem =[]
        for i in tokens:
            kata = stemmer.stem(i)
            data_stem.append(kata)
        return data_stem

    stem=[]
    for i in range(0,len(stopword)):
        stem.append(stemming(stopword[i]))

    result['stemming'] = ' '.join(list(map(lambda x: str(x), stem)))
    stemming_ = result['stemming']

    kamus_qe = open_kamus_prepro('Kamus QE.txt')

    def qe(text):  
        sentence_list = text
        new_sentence = []
        for word in sentence_list:
            for candidate_replacement in kamus_qe:
                if candidate_replacement == word:
                    word = word.replace(candidate_replacement, kamus_qe[candidate_replacement])
            new_sentence.append(word)
        return new_sentence

    test_qe=[]
    for i in range(0,len(stem)):
        test_qe.append(qe(stem[i]))

    qe_ = test_qe

    result['qe'] = ' '.join(list(map(lambda x: str(x), test_qe)))
    qe_ = result['qe']

    text_final = [' '.join(sen) for sen in test_qe]

    result['text_final'] = [' '.join(sen) for sen in test_qe]
    text_final_ = result['text_final']


    vectorizer = pickle.load(open("model_tfidf_5.pickle",'rb'))
    loaded_model = pickle.load(open("model_svm_5.pickle", 'rb'))

    vect = vectorizer.transform(text_final)[0]
    prediksisvm = loaded_model.predict(vect)[0]

    result['probabilitassvm']= loaded_model.predict_proba(vect)[0]
    probabilitassvm_ = result['probabilitassvm']

    result['probabilitassvm_new'] = "[Negatif : {:.2f}] -- \n[Positif : {:.2f}] -- \n[Netral : {:.2f}]".format(probabilitassvm_[0], probabilitassvm_[-1], probabilitassvm_[1])
    probabilitassvmm = result['probabilitassvm_new']

    result['predict'] = 'Negatif' if prediksisvm == -1 else 'Positif' if prediksisvm == 1 else 'Netral'
    hasil_kelas = result['predict']

    vectorizer_nonqe = pickle.load(open("nonqe_model_tfidf_1.pickle",'rb'))
    loaded_model_nonqe = pickle.load(open("nonqe_model_svm_1.pickle", 'rb'))

    vect_nonqe = vectorizer_nonqe.transform(text_final)[0]
    prediksisvm_nonqe = loaded_model_nonqe.predict(vect_nonqe)[0]

    result['probabilitassvm_nonqe']= loaded_model_nonqe.predict_proba(vect_nonqe)[0]
    probabilitassvm_nonqe_ = result['probabilitassvm_nonqe']

    
    result['probabilitassvmnonqe'] = "[Negatif : {:.2f}] -- \n[Positif : {:.2f}] -- \n[Netral : {:.2f}]".format(probabilitassvm_nonqe_[0], probabilitassvm_nonqe_[-1], probabilitassvm_nonqe_[1])
    probabilitassvmnonqe_ = result['probabilitassvmnonqe']

    result['predict_nonqe'] = 'Negatif' if prediksisvm_nonqe == -1 else 'Positif' if prediksisvm_nonqe == 1 else 'Netral'
    hasil_kelas_nonqe = result['predict_nonqe']


    return render_template("hasiluji.html", 
                                subject = subject,
                                casefolding = casefolding, 
                                removepunct = removepunct,
                                removenum = removenum,
                                slangword_ = slangword_,
                                hasil_token = hasil_token,
                                remove_stop_words = remove_stop_words,
                                stemming_ = stemming_,
                                qe_ = qe_,
                                text_final_ = text_final_,
                                probabilitassvmm = probabilitassvmm,
                                hasil_kelas = hasil_kelas,
                                probabilitassvm_nonqe_ = probabilitassvm_nonqe_,
                                probabilitassvmnonqe_ = probabilitassvmnonqe_,
                                hasil_kelas_nonqe = hasil_kelas_nonqe
                                ) 

if __name__ == "__main__":
    app.run(debug= True)