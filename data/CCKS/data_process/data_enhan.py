# -*- coding: utf-8 -*-
# @Time    : 2023/5/17 11:28
# @Author  : Zhang Jinzhao
# @Email   : zhangjinzhao2021@163.com
# @File    : data_enhan.py
# @Software: PyCharm

from collections import Counter
from tqdm import tqdm
import re
#平衡数据
def work1(sparql):
    pattern1 = re.compile(pattern=r"\{([^']+)\}")#找到最外层花括号的内容
    triples=re.findall(pattern1,sparql)[0]
    alltriples=[]
    for t in triples.strip().split('.'):
        if t!='':
            alltriples.append(t)
    return len(alltriples)

def data_count(dataset):
    # target:还原sparql。
    '''
    a group data is
    question+'\n'+sparql+'\n'+answer+'\n'+'\n'
    '''
    questions = []
    sparqls = []
    answers = []

    question_classes=[]

    i = 0
    for line in tqdm(dataset):
        if i % 4 == 0:  # question,still
            questions.append(line)
        if i % 4 == 1:
            sparqls.append(line)
        if i % 4 == 2:
            answers.append(line)
        i = i + 1
    assert len(questions) == len(sparqls) == len(answers)
    after_train = open('otigin\\train_after_enhance.txt', 'a', encoding='utf8')
    for i in range(len(questions)):
        if work1(sparqls[i])>3:
            line = questions[i] + sparqls[i] + answers[i] + '\n'
            line=line*5
        else:
            line = questions[i] + sparqls[i] + answers[i] + '\n'
        after_train.write(line)
if __name__ == '__main__':
    dataset=open(r'remove_re_train.txt', 'r', encoding='utf8').readlines()
    data_count(dataset)

    #print(work1('select ?x  where { <故宫博物院（故宫）> <附近> ?cvt. ?cvt <实体名称> ?x. ?cvt <距离值> ?distance. ?x <类型> <酒店>. ?x <平均价格> ?price. filter(?distance <= 5). } ORDER BY asc(?price) LIMIT 1'))