import nltk
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from nltk.tokenize import word_tokenize
from os import listdir
from os.path import join
import numpy as np

def tokenize(msg):
    msg = word_tokenize(msg)
    return(msg)

def tokenize_msglist(msglist):
    tokens = []
    for msg in msglist:
        print(tokenize(msg))
        tokens.append(tokenize(msg))
    return tokens

def sents_tokenize(msg):
    sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    sents = sent_tokenizer.tokenize(msg)
    return(sents)

def sents_tokenize_msglist(msglist):
    tokens = []
    sentsLen = []  #紀錄每篇文張有幾句
    for msg in msglist:
        # print(tokenize(msg))
        sents = sents_tokenize(msg)
        tokens.extend(sents)
        sentsLen.append(len(sents))
    return tokens,sentsLen

def readfile(path):
    files = listdir(path)
    textALL=[]
    filePath = []
    # print(files)
    # print(len(files))
    files = sorted(files)
    for f in files:

        fullpath = join(path, f)
        filePath.append(fullpath)
        with open(fullpath, 'rb') as file:
            content = file.read().decode("utf-8").lower()
            textALL.append(content)
    return textALL, files

def tf_idf(corpus):
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(corpus)
    word = vectorizer.get_feature_names()
    # print("文檔中的所有字 : ")
    # for i in range(len(word)):
    #     print(word[i],end=",")
    #     if i%10 == 0:
    #         print("")
    # print(word)
    # print(X.toarray())
    transformer = TfidfTransformer()
    tfidf = transformer.fit_transform(X)
    # print(tfidf.toarray())
    return tfidf.toarray()
def vectorizer(corpus):
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(corpus)
    word = vectorizer.get_feature_names()
    return word,X.toarray()

def similarMatrix(tfidfArray):
    tfidfArray = np.array(tfidfArray)
    SimMatrix = (np.dot(tfidfArray, tfidfArray.transpose()))
    return SimMatrix

def sortBySim(simList):
    simDic = {}
    for i in range(len(simList)):
        simDic[i] = simList[i]
    simDic =sorted(simDic.items(), key=lambda d: d[1],reverse=True)
    return  simDic

def printAppearWord(num,corpus):
    word, X = vectorizer(corpus)
    wordIndex = []
    print("~~~~~~~~~~~~~~~~~~~~~Appear Count "+str(num)+"~~~~~~~~~~~~~~~~~~~")
    for i in range(len(X[num])):
        if X[num][i] != 0:
            wordIndex.append(i)

    # for i in wordIndex:
    #     print("Word : ", end="")
    #     print(word[i], end="  ")
    #     print("appear count : ", end="")
    #     print(X[num][i])

    return wordIndex

def cor_appear(num1,num2,wordIndex1,wordIndex2,corpus):
    corIndex = []
    word, X = vectorizer(corpus)
    print("~~~~~~~~~~~~~~~~~~~~~corAppear Count " + str(num1) +" and "+str(num2)+ "~~~~~~~~~~~~~~~~~~~")

    for i in wordIndex1:
        if i in wordIndex2:
            corIndex.append(i)
    print(len(corIndex))
    for i in corIndex:
        print("Word : ", end="")
        print(word[i])
        print("text1 word appear count : ", end="")
        print(X[num1][i])
        print("text2 word appear count : ", end="")
        print(X[num2][i])

if __name__ == "__main__":
    mypath = "text_pre"
    corpus,fullPath = readfile(mypath)
    # tokenize_msglist(textALL)
    # print(len(textALL))

    # ~~~~~~~~~~~~第一種算TFIDF和相似度~~~~~~~~~~~~~~~~~
    tfidfArray = np.array(tf_idf(corpus))
    print(tfidfArray)
    SimMatrix = similarMatrix(tfidfArray)
    print(SimMatrix)

    # ~~~~~~~~~~~~~第二種算TFIDF相似度  SENTENCE~~~~~~~~~~~~~~~~
    sentsCorpus,sentsLen = sents_tokenize_msglist(corpus)  #斷句後做為新的corpus
    # 先算sents的TFIDF再將同篇文章的TFIDF加起來
    tfidfarray_sents = np.array(tf_idf(sentsCorpus))
    tfidfArray_sents = []
    sentnum = -1
    docindex = -1
    temptfidf = []
    # 將同篇文章的TFIDF加起來
    for sentindex in range(len(tfidfarray_sents)+1):
        if(sentnum>=1):
            temptfidf += tfidfarray_sents[sentindex]
            sentnum-=1
        else:
            if(docindex!=-1):
                tfidfArray_sents.append(temptfidf)
            if(sentindex == len(tfidfarray_sents)):
                break
            docindex+=1
            sentnum = sentsLen[docindex]-1
            temptfidf = tfidfarray_sents[sentindex]

    # 正規化
    for sentindex in range(len(tfidfArray_sents)):
        tfidfArray_sents[sentindex]/= sentsLen[sentindex]
    # print(len(tfidfArray))
    tfidfArray_sents = np.array(tfidfArray_sents)
    print(tfidfArray_sents)

    SimMatrix_sents = similarMatrix(tfidfArray_sents)
    print(SimMatrix_sents)

    # ~~~~~~~~~~~~~~~~~~~~~第三種算TFIDF相似度 前面兩種加起來~~~~~~~~~~~~~~~~~~~~~~~~~~
    tfidfArray_third = (tfidfArray_sents + tfidfArray)/2
    print(tfidfArray_third)
    SimMatrix_sents = similarMatrix(tfidfArray_third)
    print(SimMatrix_sents)


    #case study
    print(sortBySim(SimMatrix_sents[1]))
    print("原本文檔出現字數統計:")
    print(fullPath[1])
    print(corpus[1])
    wordIndex1 = printAppearWord(1,corpus)
    print("最相似文檔出現字數統計:")
    print(fullPath[24])
    print(corpus[24])
    wordIndex2 = printAppearWord(24,corpus)
    print("最不相似文檔出現字數統計:")
    print(fullPath[40])
    print(corpus[40])
    wordIndex3 = printAppearWord(40,corpus)

    cor_appear(1,24,wordIndex1,wordIndex2,corpus)
    cor_appear(1,40,wordIndex1,wordIndex3,corpus)











