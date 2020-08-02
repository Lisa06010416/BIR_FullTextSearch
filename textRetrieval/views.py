from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.forms.models import model_to_dict
import re
import json
import ast
import math
import numpy as np
from textblob import Word
from textRetrieval.models import Search, Text
from PorterStemmer import PorterStemmer
import NLP_preprocess
import preprocess
from django.views.decorators.csrf import ensure_csrf_cookie
import hashlib

# ~~~~~~~~~~~~~~~~~Zip Distribution~~~~~~~~~~~~~~~~~~~
def ZipDistribution(request):
    return render(request, 'ZipDistribution.html', {})


def ZipDistribution_Query(request):
    ALL_wordCounts = 0
    Twitter_wordcounts = 0
    Pubmed_counts = 0
    AllText = Text.objects.all()
    for i in AllText:
        ALL_wordCounts += i.wordnum
        if i.filetype == 'pubmed':
            Pubmed_counts += i.wordnum
        else:
            Twitter_wordcounts += i.wordnum

    # TF  all
    ALL_TF_chart = [['word', 'ALL_TF']]
    ALL_TF_chart2 = [['word', 'ALL_TF']]
    ALL_word = Search.objects.all()

    for i in ALL_word.order_by('-countallfiles'):
        TF_chart_data = []
        TF_chart_data.append(i.word)
        TF_chart_data.append(1 + math.log(i.countallfiles, 10))

        TF_chart_data2 = []
        TF_chart_data2.append(i.word)
        TF_chart_data2.append(i.countallfiles / (Pubmed_counts + Twitter_wordcounts))
        ALL_TF_chart.append(TF_chart_data)
        ALL_TF_chart2.append(TF_chart_data2)

    # TF on pudmed
    Pubmed_TF_chart = [['word', 'Pubmed_TF']]
    Pubmed_TF_chart2 = [['word', 'Pubmed_TF']]
    for i in ALL_word.order_by('-countpudmedfiles'):
        if i.countpudmedfiles != 0:
            TF_chart_data = []
            TF_chart_data.append(i.word)
            TF_chart_data.append(1 + math.log((i.countpudmedfiles), 10))

            TF_chart_data2 = []
            TF_chart_data2.append(i.word)
            TF_chart_data2.append(i.countpudmedfiles / Pubmed_counts)
            Pubmed_TF_chart.append(TF_chart_data)
            Pubmed_TF_chart2.append(TF_chart_data2)

    # TF on twitter
    Twitter_TF_chart = [['word', 'Twitter_TF']]
    Twitter_TF_chart2 = [['word', 'Twitter_TF']]
    for i in ALL_word.order_by('-counttwitterfiles'):
        if i.counttwitterfiles != 0:
            TF_chart_data = []
            TF_chart_data.append(i.word)
            TF_chart_data.append(1 + math.log((i.counttwitterfiles), 10))

            TF_chart_data2 = []
            TF_chart_data2.append(i.word)
            TF_chart_data2.append(i.counttwitterfiles / Twitter_wordcounts)

            Twitter_TF_chart.append(TF_chart_data)
            Twitter_TF_chart2.append(TF_chart_data2)

    # print(model_to_dict(ALL_word.order_by('-countallfiles')))
    # print(model_to_dict(ALL_word.order_by('-countpudmedfiles')))
    # print(model_to_dict(ALL_word.order_by('-counttwitterfiles')))

    data = {
        'ALL': ALL_TF_chart,
        'ALL2': ALL_TF_chart2,
        'Pubmed': Pubmed_TF_chart,
        'Pubmed2': Pubmed_TF_chart2,
        'Twitter': Twitter_TF_chart,
        'Twitter2': Twitter_TF_chart2
    }
    print("~~~~ALL~~~~~")
    for i in ALL_TF_chart[0:30]:
        print(i[0],end="、")
    print("~~~~Pubmed~~~~~")
    for i in Pubmed_TF_chart[0:30]:
        print(i[0],end="、")
    print("~~~~Twitter~~~~~")
    for i in Twitter_TF_chart[0:30]:
        print(i[0],end="、")

    return HttpResponse(json.dumps(data), content_type="application/json")


# ~~~~~~~~~~~~~~~~~~~~preprocess~~~~~~~~~~~~~~~~~~~~~~
def Preprocess(request):
    return render(request, 'preprocess.html', {})

def Preprocess_Query(requess):
    searchresults = []
    preprocess.preprocess()
    results = Text.objects.filter().all()

    for i in results:
        searchresult = []
        with open(i.content, 'rb') as f:
            text = f.read().decode("utf-8")
            text = re.sub(r'\n', "<br>", text)
            searchresult.append(text)
            searchresult.append(i.sentencenum)
            searchresult.append(i.wordnum)
            searchresult.append(i.characternum)
        searchresults.append(searchresult)
    return JsonResponse(searchresults, safe=False)

def Preprocess_spimi_Query(requess):
    searchresults = []
    preprocess.preprocess_spimi()
    results = Text.objects.filter().all()

    for i in results:
        searchresult = []
        with open(i.content, 'rb') as f:
            text = f.read().decode("utf-8")
            text = re.sub(r'\n', "<br>", text)
            searchresult.append(text)
            searchresult.append(i.sentencenum)
            searchresult.append(i.wordnum)
            searchresult.append(i.characternum)
        searchresults.append(searchresult)
    return JsonResponse(searchresults, safe=False)

# ~~~~~~~~~~~~~~~~~~~~~~~SEARCH  Sentence~~~~~~~~~~~~~~~~~~~~~~~
def sentsSearch(request):
    return render(request, 'textSimlar.html', {})
@ensure_csrf_cookie
def sentsSearch_Query(request):

    input = request.POST
    print(input)
    sent = input['input']
    print(sent)
    corpus, fullPath = NLP_preprocess.readfile(r"D:\work\Class\1.BIR\BIR_textRetrieval\text_pre")
    corpus.append(sent)
    fullPath.append("userInput")
    tfidfArray = np.array(NLP_preprocess.tf_idf(corpus))

    SimMatrix = NLP_preprocess.similarMatrix(tfidfArray)
    sentSim = NLP_preprocess.sortBySim(SimMatrix[len(SimMatrix)-1])

    print(SimMatrix)
    print(sentSim)
    searchresults = []
    for i in sentSim:
        searchresult={}
        index = i[0]
        searchresult["sim"] = i[1]
        searchresult["text"] = corpus[index]
        searchresults.append(searchresult)
    print(searchresults)
    return HttpResponse(json.dumps(searchresults), content_type="application/json")
# ~~~~~~~~~~~~~~~~~~~~~~~SEARCH~~~~~~~~~~~~~~~~~~~~~~~
def FullTextSearch(request):
    return render(request, 'search.html', {})

def FullTextSearch_Query(request):
    keyword = request.GET.get('intput')
    All_textIndex = []  # 所有有關建字文章的編號
    All_original_word = []  # 所有poter後對應到一樣詞幹的字
    searchresults = []  # 最後回傳的List
    # [  {'msg':correct_KW or Non},
    #    {文章 字數 ,句數 ,字元數 ,文章內容},
    #      ...
    # ]

    # 判斷是否要更正
    is_correct_msg = {}
    correct_KW = Word(keyword).spellcheck()[0][0]
    if keyword != correct_KW:  # 更正後的字和輸入的關鍵字不一樣 可能要更正
        is_correct_msg['msg'] = correct_KW
    else:  # 不用更正
        is_correct_msg['msg'] = 'Non'

    print('更正後: ' + correct_KW + ' 原本: ' + keyword)
    print(is_correct_msg)
    # porter
    p = PorterStemmer()
    keyword_porter = p.stem(keyword, 0, len(keyword) - 1)

    # 用poter後的關鍵字進DB查對應關鍵字的資料
    hash_object = hashlib.sha1(keyword_porter.encode("utf-8"))
    SearchAnswer = Search.objects.filter(word=hash_object.hexdigest())
    if len(SearchAnswer) == 0:  # 如果沒有含有該字的文章
        print('NO DATA')
        searchresults.insert(0, is_correct_msg)
        return HttpResponse(json.dumps(searchresults), content_type="application/json")

    for i in SearchAnswer:
        # 找出所有有keyword出現的檔案編號
        textIndex = i.fileindex[1:-1].split(',')
        for j in textIndex:
            if int(j) not in All_textIndex:
                All_textIndex.append(int(j))

        # 找出所有poter後結果一樣的字
        original_word = ast.literal_eval(i.word_original)
        for j in original_word:
            if j not in All_original_word:
                All_original_word.append(j)
    print('相似字:' + str(All_original_word))

    # 用textIndex逐一去查出每篇文件
    for Index in All_textIndex:
        TextAnswer = Text.objects.filter(fileindex=Index)
        with open(TextAnswer[0].content, 'rb') as f:
            text = f.read().decode("utf-8")

            # 算TF來排序文章的重要性
            wordnum = text.split()
            keywordNum = 0
            for i in wordnum:
                if i in All_original_word:
                    if i == keyword:
                        keywordNum += 2
                    else:
                        keywordNum += 1
            tf = 1 + math.log(keywordNum, 10)

            text = re.sub(r'\n', "<br>", text)
            # 完全比對正確 把字改為紅色
            text = re.sub(" " + keyword + " ", r" <font color='#FF0000'>" + keyword + r"</font> ", text)
            # 部分比對正確 把字改為藍色
            for original_word in All_original_word:
                text = re.sub(" " + original_word + " ", r" <font color='#0044BB'>" + original_word + r"</font> ", text)
                text = re.sub("." + original_word + " ", r" .<font color='#0044BB'>" + original_word + r"</font> ", text)
            searchresult = model_to_dict(TextAnswer[0])
            searchresult['text'] = text
            searchresult['TF'] = tf

        searchresults.append(searchresult)


    searchresults = sorted(searchresults, key=lambda e: e.__getitem__('TF'), reverse = True)
    searchresults.insert(0, is_correct_msg)
    print(searchresults[0])

    return HttpResponse(json.dumps(searchresults), content_type="application/json")
