import pickle
import re
import pandas as pd
import string
from nltk.corpus import stopwords
from nltk import word_tokenize
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

def case_folding(tokens): 
    return tokens.lower()

def remove_punct(text):
	text_nopunct = ''
	text_nopunct = re.sub('['+string.punctuation+']', ' ', text)
	return text_nopunct

def remove_num(text):  
    text_nonum = ''
    text_nonum = re.sub(r'\d+',' ', text)
    return text_nonum

def open_kamus_prepro(x):
	kamus={}
	with open(x,'r') as file :
		for line in file :
			slang=line.replace("'","").split(':')
			kamus[slang[0].strip()]=slang[1].rstrip('\n').lstrip()
	return kamus

def slangword(text):
    sentence_list = text.split()
    new_sentence = []
    
    for word in sentence_list:
      for candidate_replacement in kamus_slang:
        if candidate_replacement == word:
          word = word.replace(candidate_replacement, kamus_slang[candidate_replacement])
      new_sentence.append(word)
    return " ".join(new_sentence)

def remove_stop_words(tokens):
    return [word for word in tokens if word not in kamus_stopword]

def stemming(tokens):  
    data_stem =[]
    for i in tokens:
      kata = stemmer.stem(i)
      data_stem.append(kata)
    return data_stem

import sys
import json
import base64

if __name__ == '__main__':

    result = {}

    inputWord = sys.argv[1]
    inputWordDecode = base64.b64decode(inputWord)
    data = json.loads(inputWordDecode)
    result['status'] = data.get('data')
    token = [data.get('data')]
    # print(json.dumps(token))
    # sys.exit()
    # token =["pelayanan cepat, untuk rasa lumayanlah"]

    
    test_casefolding = []
    
    for i in range(0, len(token)):
        test_casefolding.append(case_folding(token[i]))

    result['case_folding'] = ' '.join(list(map(lambda x: str(x), test_casefolding)))

    test_removepunct=[]
    for i in range(0,len(test_casefolding)):
      test_removepunct.append(remove_punct(test_casefolding[i]))

    result['remove_punct'] = ' '.join(list(map(lambda x: str(x), test_removepunct)))

    test_removenum=[]
    for i in range(0,len(test_removepunct)):
        test_removenum.append(remove_num(test_removepunct[i]))

    result['remove_num'] = ' '.join(list(map(lambda x: str(x), test_removenum)))
    
    kamus_slang=open_kamus_prepro('D:/InstagramScraper-master/Kamus Preprocessing/Kamus spelling_word.txt')

    test_slangword=[]
    for i in range(0,len(test_removenum)):
        test_slangword.append(slangword(test_removenum[i]))

    hasil_token = [word_tokenize(sen) for sen in test_slangword]

    result['slangword'] = ' '.join(list(map(lambda x: str(x), test_slangword)))

    result['hasil_token'] = hasil_token

    kamus_stopword=[]
    with open('D:/InstagramScraper-master/Kamus Preprocessing/Kamus stopword.txt','r') as file :
        for line in file :
            slang=line.replace("'","").strip()
            kamus_stopword.append(slang)

    stopword= [remove_stop_words(sen) for sen in hasil_token] 

    result['remove_stop_words'] = ' '.join(list(map(lambda x: str(x), stopword)))

    factory = StemmerFactory()
    stemmer = factory.create_stemmer()

    stem=[]
    for i in range(0,len(stopword)):
      stem.append(stemming(stopword[i]))

    result['stemming'] = ' '.join(list(map(lambda x: str(x), stem)))

    text_final = [' '.join(sen) for sen in stem]

    result['text_final'] = ' '.join(list(map(lambda x: str(x), text_final)))

    vectorizer = pickle.load(open("D:/InstagramScraper-master/Jupyter/vectorizer_sentimennetral.pickle",'rb'))

    loaded_model = pickle.load(open("D:/InstagramScraper-master/Jupyter/sentimenmodels_svmnetral.pickle", 'rb'))
    prediksisvm = loaded_model.predict(vectorizer.transform(text_final))[0]
    probabilitassvm = loaded_model.predict_proba(vectorizer.transform(text_final))[0]

    result['probabilitassvm'] = "Negatif : {:.3f} \nPositif : {:.3f} \nNetral : {:.3f}".format(probabilitassvm[0], \
        1-probabilitassvm[0])

    kelasSvm = ""
    if prediksisvm == 1 :
        kelasSvm = "Positif"
    if prediksisvm == -1 :
        kelasSvm = "Negatif"
    if prediksisvm == 0:
        kelasSvm = "Netral"

    result['prediksisvm'] = kelasSvm

    print(json.dumps(result))
