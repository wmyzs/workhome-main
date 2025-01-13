# -*- coding: utf-8 -*-
# @Time    : 2023/4/18 16:06
# @Author  : Zhang Jinzhao
# @Email   : zhangjinzhao2021@163.com
# @File    : process_train_sparql.py
# @Software: PyCharm

import re
import pickle
from tqdm import tqdm


def extract_entity(text):
    pattern1 = re.compile(pattern=r"<(.*?)>")  # 提取<实体>
    pattern2 = re.compile(pattern=r"\"(.*?)\"")  # 提取"实属性值"
    try:
        text1 = re.findall(pattern1, text)
        text2 = re.findall(pattern2, text)
    except IndexError:
        print(text)
    else:
        return text1+text2

def remove_fre(sparql):
    vals=''
    regex=''
    if "FILTER REGEX" in sparql:
        regex=re.findall(r'FILTER REGEX\((.*)\)',sparql)[0]
        sparql=sparql.replace('FILTER REGEX('+regex+') .','')
        ent=re.findall('\"(.*)"',regex)[0]
        val=re.findall(r'\?\w*',regex)[0]
        sparql=sparql.replace(val, '"'+ent+'"')
        print(sparql)
    if "filter regex" in sparql:
        regex=re.findall(r'filter regex\((.*)\)',sparql)[0]
        sparql = sparql.replace('filter regex('+regex+') .', '')
        ent = re.findall('\"(.*)"', regex)[0]
        val = re.findall(r'\?\w*', regex)[0]
        sparql=sparql.replace(val, '"'+ent+'"')
        print(sparql)
    return sparql

def remove_fitter_re(datasets):

    questions = []
    sparqls = []
    answers=[]
    question=''
    i = 0
    for line in tqdm(datasets):
        if i % 4 == 0:#question,still
            question=line
            questions.append(line)
        if i % 4 == 1:
            sparql=remove_fre(line)
            sparqls.append(sparql)
        if i % 4 == 2:
            answers.append(line)
        i=i+1
    assert len(questions)==len(sparqls)==len(answers)
    after_train=open('origin\\remove_re_train.txt', 'a', encoding='utf8')
    for i in range(len(questions)):
        line=questions[i]+sparqls[i]+answers[i]+'\n'
        after_train.write(line)

def normalization_sparql(question,sparql,entity2mention):
    #todo 规范化sparql语句，统一以查询?x为准
    #去掉filter regex 该函数可以用实体链接解决
    #先小写常见语法
    sparql=sparql.replace('SELECT','select').replace('WHERE','where').replace('WHERE','where')
    xory = re.findall(r"\?(.*?)\s", sparql)[0].split('{')[0]
    if xory !='x':
        #先替换?x 为?xx
        sparql=sparql.replace('?x','?xx')
        sparql = sparql.replace('?{}'.format(xory), '?x')

    #替换SPARQL语句中的实体，换成问题中出现过的mention
    entities=extract_entity(sparql)
    for entity in entities:
        if entity in question:
            continue
        else:
            mentions=entity2mention[entity]
            for mention in mentions:
                if mention in question:
                    if '<'+entity+'>' in sparql:
                        sparql=sparql.replace('<'+entity+'>','<'+mention+'>')
                    elif '"' + entity + '"' in sparql:
                        sparql=sparql.replace('"'+entity+'"','"'+mention+'"')
    return sparql

def preprocess_train(dataset,entity2mention):
    #target:还原sparql。
    '''
    a group data is
    question+'\n'+sparql+'\n'+answer+'\n'+'\n'
    '''
    questions = []
    sparqls = []
    answers=[]
    question=''
    i = 0
    for line in tqdm(dataset):
        if i % 4 == 0:#question,still
            question=line
            questions.append(line)
        if i % 4 == 1:
            sparql=normalization_sparql(question,line,entity2mention)
            sparqls.append(sparql)
        if i % 4 == 2:
            answers.append(line)
        i=i+1
    assert len(questions)==len(sparqls)==len(answers)
    after_train=open('after_train.txt', 'a', encoding='utf8')
    for i in range(len(questions)):
        line=questions[i]+sparqls[i]+answers[i]+'\n'
        after_train.write(line)

if __name__ == '__main__':
    #datasets = open('manual_train.txt', 'r', encoding='utf8').readlines()
    # f = open('entity2mention.pkl', 'rb')
    # entity2mention = pickle.load(f)  # 加载索引文件
    # preprocess_train(dataset,entity2mention)
    #remove_fitter_re(datasets)
    sparql='select distinct ?x where { ?replace <中文名> "美丽人生" . ?replace <导演> ?y . ?y <妻子> ?z . ?z <国籍> ?x . }'
    print(remove_fre(sparql))




