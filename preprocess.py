# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import json
from os import listdir
from os.path import join
import re
import xml.etree.cElementTree as ET
import hashlib
from keras.models import load_model
from keras import backend
import numpy as np
from textRetrieval.models import Search, Text
from django.db import models, connection
import  ast
from PorterStemmer import PorterStemmer


def remove_tag(text):
    string = re.sub('[\s+\.\!\/_\\,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）：:.,?$@%@()<>;]+', " ", text)
    return string


# ~~~~~~~~~~~~~~~~~~~~~~~~~~將文件由XML和json處理好存起來~~~~~~~~~~~~~~~~~~~~~~~~~
def preprocesstext():
    mypath = "text"
    files = listdir(mypath)
    for f in files:
        mypath = "text"
        writepath = "text_pre"
        fullpath = join(mypath, f)
        writepath = join(writepath, f)

        if (fullpath.endswith('xml')):
            pre_ncbi(fullpath, writepath)
        else:
            pre_twitter(fullpath, writepath)


def pre_twitter(fullpath, writepath):
    with open(fullpath, mode='rb') as f:
        result = json.loads(f.read())
        try:
            text = result['text']
            with open(writepath, mode='wb') as f:
                f.write(text.encode('utf-8'))
                f.write("\n".encode('utf-8'))
        except:
            num = 1
            for i in result:
                text = i['text']
                with open(writepath + str(num), mode='wb') as f:
                    f.write(text.encode('utf-8'))
                    f.write("\n".encode('utf-8'))
                num += 1


def pre_ncbi(fullpath, writepath):
    with open(fullpath, 'rb') as file:
        content = file.read().decode("utf-8")
        content = str(content)
        content = re.sub('<sup>.*?</sup>', ' ', content)
        content = re.sub('<sub>.*?</sub>', ' ', content)
        text = ""
        root = ET.fromstring(content)
        num = 1
        for child_of_root in root.iterfind('PubmedArticle/MedlineCitation/Article'):
            try:
                text += child_of_root.find('ArticleTitle').text
                text += "\n"
            except:
                text += ""
            for i in child_of_root.findall('Abstract/AbstractText'):
                try:
                    text += i.text
                except:
                    text += ""
            with open(writepath + str(num), 'wb') as f:
                f.write(text.encode('utf-8'))
            num += 1
            text = ""


# ~~~~~~~~~~~~~~~~~~~~~~~~~~EOS model~~~~~~~~~~~~~~~~~~~~~~~~~

def EOS(content):
    backend.clear_session()
    model = load_model('dot_model.h5')
    p = []
    DotSents = cutDot(content)
    for i in DotSents:
        t = []
        for j in i:
            t.append(ord(j) / 100)
        t.append(0.1)
        if (len(t) == 41):
            p.append(t)

    p = np.array(p)
    if len(p != 0):
        predict = model.predict_classes(p)

        print("\n\n")
        for i in range(len(DotSents)):
            print(DotSents[i])
            print("  predict:", predict[i])

        print("Sentence :", end='')
        if sum(predict) == 0:
            print(sum(predict) + 1)
            return sum(predict) + 1
        else:
            print(sum(predict))
            return sum(predict)
    else:
        return [1]


def cutDot(text):  # 將文章切成intput data
    L = 20
    DotSents = []
    for i in range(len(text)):
        if (i > L and i < len(text) - L):
            if (text[i] == '.'):
                DotSents.append(text[i - L:i + L])

        else:
            if (text[i] == '.'):
                padding = ""
                if (i < L):
                    for j in range(L - i):
                        padding += " "
                    DotSents.append(padding + text[:i + L])
                elif (len(text) - i < L):
                    for j in range(L - (len(text) - i)):
                        padding += " "
                    DotSents.append(text[i - L:] + padding)
    return DotSents


# ~~~~~~~~~~~~~~~~~~~~~~~~~~Search Dictionary~~~~~~~~~~~~~~~~~~~~~~~~~
def Word_appear_count(text, type, Word_count_pubmed, Word_count_twitter, Word_count_all):
    text = remove_tag(text)
    word = text.split()
    p = PorterStemmer()
    for i in word:
        i = p.stem(i, 0, len(i) - 1)  # porter

        # pubmed
        if i not in Word_count_pubmed.keys():
            Word_count_pubmed[i] = 0
            if type == 'pubmed':
                Word_count_pubmed[i] += 1
        elif i in Word_count_pubmed.keys() and type == 'pubmed':
            Word_count_pubmed[i] += 1

        # twitter
        if i not in Word_count_twitter.keys():
            Word_count_twitter[i] = 0
            if type == 'twitter':
                Word_count_twitter[i] += 1
        elif i in Word_count_twitter.keys() and type == 'twitter':
            Word_count_twitter[i] += 1

        # all
        if i not in Word_count_all.keys():
            Word_count_all[i] = 1
        elif i in Word_count_all.keys():
            Word_count_all[i] += 1

    return Word_count_pubmed, Word_count_twitter,Word_count_all


def search_dic(text, SearDic, original_word, index):
    text = remove_tag(text)
    word = text.split()
    p = PorterStemmer()
    for i in word:

        # poter_i = i
        poter_i = p.stem(i, 0, len(i) - 1)  # porter
        if poter_i not in SearDic.keys():
            SearDic[poter_i] = [index]
            original_word[poter_i] = [i]
        else:
            if index not in SearDic[poter_i]:
                SearDic[poter_i].append(index)
                if i not in original_word[poter_i]:
                    original_word[poter_i].append(i)
    return SearDic, original_word


def wordnum(text):
    wordnum = text.split()
    return len(wordnum)


def characternum(text):
    return len(text)


def word_count_all(i, Word_count_pubmed, Word_count_twitter):
    count = 0
    try:
        count += Word_count_pubmed[i]
    except:
        return Word_count_twitter[i], 0, Word_count_twitter[i]
    try:
        count += Word_count_twitter[i]
    except:
        return Word_count_pubmed[i], Word_count_pubmed[i], 0
    return count, Word_count_pubmed[i], Word_count_twitter[i]


def preprocess():
    print("~~~~~~~~~clean DB~~~~~~~~")
    cursor = connection.cursor()
    cursor.execute("TRUNCATE TABLE " + 'search')
    cursor = connection.cursor()
    cursor.execute("TRUNCATE TABLE " + 'text')

    print("~~~~~~~~~preprocess~~~~~~~~")
    preprocesstext()

    mypath = "text_pre"
    files = listdir(mypath)
    index = 1

    Word_count_pubmed = {}
    Word_count_twitter = {}
    Word_count_all = {}
    SearDic = {}
    original_word = {}

    for f in files:
        fullpath = join(mypath, f)
        with open(fullpath, 'rb') as file:
            content = file.read().decode("utf-8")
            # 判斷檔案格式
            if 'xml' in fullpath:
                texttype = 'pubmed'
            else:
                texttype = 'twitter'
            # 存text資料
            Text.objects.create(fileindex=index,
                                content=fullpath.replace('\\', '\\\\'),
                                sentencenum=EOS(content)[0],
                                wordnum=wordnum(content),
                                characternum=characternum(content),
                                filetype=texttype
                                ).save()

            Word_count_pubmed, Word_count_twitter, Word_count_all = Word_appear_count(content, texttype,Word_count_pubmed,Word_count_twitter,Word_count_all)  # 計算字出現次數
            SearDic, original_word = search_dic(content, SearDic, original_word, index)  # 建字典
            index = index + 1

    print("~~~~~~~~~Saving Data~~~~~~~~")

    #hash
    hash_objects = {}
    for i in SearDic:
        hash_object = hashlib.sha1(i.encode("utf-8"))
        hash_objects[i] = hash_object.hexdigest()

    for i in SearDic:
        Search.objects.create(word=hash_objects[i],
                              countallfiles=Word_count_all[i],
                              countpudmedfiles=Word_count_pubmed[i],
                              counttwitterfiles=Word_count_twitter[i],
                              fileindex=SearDic[i],
                              word_original=original_word[i]
                              ).save()

def preprocess_spimi():
    print("~~~~~~~~~clean DB~~~~~~~~")
    cursor = connection.cursor()
    cursor.execute("TRUNCATE TABLE " + 'search')
    cursor = connection.cursor()
    cursor.execute("TRUNCATE TABLE " + 'text')

    print("~~~~~~~~~preprocess~~~~~~~~")
    preprocesstext()

    mypath = "text_pre"
    files = listdir(mypath)
    index = 1

    Word_count_pubmed = {}
    Word_count_twitter = {}
    Word_count_all = {}
    SearDic = {}
    original_word = {}

    batch = 2  #一次要讀多少檔案
    b=0
    for f in files:
        b+=1
        fullpath = join(mypath, f)
        with open(fullpath, 'rb') as file:
            content = file.read().decode("utf-8")
            # 判斷檔案格式
            if 'xml' in fullpath:
                texttype = 'pubmed'
            else:
                texttype = 'twitter'
            # 存text資料
            Text.objects.create(fileindex=index,
                                content=fullpath.replace('\\', '\\\\'),
                                sentencenum=EOS(content)[0],
                                wordnum=wordnum(content),
                                characternum=characternum(content),
                                filetype=texttype
                                ).save()

            Word_count_pubmed, Word_count_twitter, Word_count_all = Word_appear_count(content, texttype,Word_count_pubmed,Word_count_twitter,Word_count_all)  # 計算字出現次數
            SearDic, original_word = search_dic(content, SearDic, original_word, index)  # 建字典
            index = index + 1

            if b==batch: # 處理的檔案數達到一定的量(batchsize)  先將資料存進DB
                b=0 #已讀檔案數歸0
                print("~~~~~~~~~Saving Data~~~~~~~~")
                # hash
                hash_objects = {}
                for i in SearDic:
                    hash_object = hashlib.sha1(i.encode("utf-8"))
                    hash_objects[i] = hash_object.hexdigest()

                for i in SearDic:
                    # 看之前是否已經有存過這個字
                    word = Search.objects.filter(word=hash_objects[i])
                    if len(word) == 0: #之前沒有這個字
                        Search.objects.create(word=hash_objects[i],
                                              countallfiles=Word_count_all[i],
                                              countpudmedfiles=Word_count_pubmed[i],
                                              counttwitterfiles=Word_count_twitter[i],
                                              fileindex=SearDic[i],
                                              word_original=original_word[i]
                                              ).save()
                    else:

                        SearDic[i].extend(ast.literal_eval(word[0].fileindex))
                        original_word[i].extend(ast.literal_eval(word[0].word_original))
                        original_word[i] = list({}.fromkeys(original_word[i]).keys())
                        word.update(countallfiles=word[0].countallfiles+Word_count_all[i],
                                       countpudmedfiles=word[0].countpudmedfiles+Word_count_pubmed[i],
                                       counttwitterfiles=word[0].counttwitterfiles+Word_count_twitter[i],
                                       fileindex=SearDic[i],
                                       word_original=original_word[i]
                                       )

                Word_count_pubmed = {}
                Word_count_twitter = {}
                Word_count_all = {}
                SearDic = {}
                original_word = {}