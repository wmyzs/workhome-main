# -*- coding: utf-8 -*-
# @Time    : 2023/5/8 9:29
# @Author  : Zhang Jinzhao
# @Email   : zhangjinzhao2021@163.com
# @File    : sparql2sexp.py
# @Software: PyCharm

from tqdm import tqdm
import re
from collections import defaultdict

'''
问题：
奥森公园附近5km内最贵的酒店是哪一家？

sparql：
select ?y  where { 
<奥林匹克森林公园> <附近> ?cvt. 
?cvt <实体名称> ?y. 
?cvt <距离值> ?distance. 
?y <类型> <酒店>. 
?y <平均价格> ?price. 
filter(?distance <= 5). }
ORDER BY desc(?price) 
LIMIT 1

s-表达式：
(ARGMAX (AND (JOIN (R 附近) 奥林匹克森林公园)  (le 距离值 5)) 平均价格)

{J:JOIN,A:AND,R:R,L:REL,X:ARGMAX,N:ARGMIN,}
'''
def split_t(text):#单个三元组中，获取三元组和变量名
    text=text.strip()
    #vals = re.findall(r'\?(.*?)<|\?(.*)', text)
    vals = re.findall(r'\?\w*', text)
    entities = re.findall(r"<(.*?)>|\"(.*?)\"", text)
    triple =''
    rval=[]

    if len(vals) == 1:
        #val = vals[0][0] if vals[0][0] != '' else vals[0][1]
        val = vals[0] if vals[0] != '' else vals[1]
        val = val.replace(' ', '').replace('\t', '')
        #rval.append('?'+val)
        rval.append(val)
        entity1 = entities[0][0] if entities[0][0] != '' else entities[0][1]
        entity2 = entities[1][0] if entities[1][0] != '' else entities[1][1]
        if text.startswith('?'):
            #triple=['?' + val, entity1, entity2]
            triple=[val, entity1, entity2]
        elif text.endswith(val):
            #triple=[entity1, entity2, '?' + val]
            triple=[entity1, entity2, val]
        else:#查询关系<ent ?x ent>
            #triple=[entity1, '?' + val, entity2]
            triple=[entity1, val, entity2]
    elif len(vals) == 2:#还有<?x,?a ent>待处理
        val1 = vals[0]
        val1 = val1.replace(' ', '').replace('\t', '')
        #rval.append('?'+val1)
        rval.append(val1)
        #val2 = vals[1][0] if vals[1][0] != '' else vals[1][1]
        val2 = vals[1]
        val2 = val2.replace(' ', '').replace('\t', '')
        #rval.append('?'+val2)
        rval.append(val2)
        entity = entities[0][0] if entities[0][0] != '' else entities[0][1].replace(' ', '').replace('\t', '')
        #triple=['?'+val1, entity, '?'+val2]

        val1_index=text.index(val1)
        val2_index=text.index(val2)
        ent_index=text.index(entity)
        if ent_index < val1_index:
            triple=[entity,val1,val2]
        elif ent_index > val2_index:
            triple = [val1,val2,entity]
        else:
            triple=[val1, entity, val2]#<?x,?a,ent>#<?x,ent,?a>#<?ent,?x,?a>
    elif len(vals)==3:#?z ?x ?replace
       return vals,vals
    return rval,triple

def cluset(sexp_list):#将s表达式的列表合并
    final=sexp_list[0]
    if len(sexp_list)==1:
        return sexp_list[0]
    else:
        for i in range(1,len(sexp_list)):
            temp='AND ({}) ({})'.format(sexp_list[i],final)
            final=temp
    return  final

def get_core_entity(triples):#得到实体出现的顺序['?x', '?b', '?c']
    core_entity=['?x']
    split_vals=[]
    lenvars=set()
    for t in triples:
        if 'filter' in t:continue#如果存在filter，则暂时跳过
        var,triple = split_t(t)
        split_vals.append(var)
        for v in var:
            lenvars.add(v)
    temp_entity = '?x'
    tag=True
    watch_dog=0
    while tag:
        watch_dog+=1
        if watch_dog>100:
            break
        for var in split_vals:
            if len(core_entity) == len(lenvars):
                tag = False
                break
            if len(var)<=1:continue
            elif len(var)==2:
                if '?x' in var:
                    other = var[0] if var[0] != '?x' else var[1]
                    if other in core_entity: continue
                    temp_entity=other
                    core_entity.append(other)
                elif temp_entity in var:
                    temp_entity=var[0] if var[0]!=temp_entity else var[1]
                    if temp_entity in core_entity:continue
                    core_entity.append(temp_entity)
            elif len(var)==3:
                for v in var:
                    if v !='?x':
                        core_entity.append(v)
    return core_entity

def generate_operator(triple):#?cvt <距离值> ?distance. filter(?distance <= 2) -> AND (?cvt) (LE 距离值 2)
    #compare_var='?'+re.findall(r'\?(.*?)\s*[<>=]+\s*',triple)[0]
    compare_var=re.findall(r'\?\w*',triple)[0]
    compare_operator=re.findall(r'(?<=\s)[<>]=?(?=\s)',triple)[0]
    operator_mapper = {'<': 'LT', '<=': 'LE', '>': 'GT', ">=": "GE"}
    compare_value=re.findall('\d',triple)[0]
    return  [operator_mapper[compare_operator],compare_var,compare_value]

def process_sp(tris):#
    '''
    <五金> <五种指> ?replace. ?x <中文名> ?replace. ?x <应用> <油漆>.
    select ?x where { <萧远山> <冤家> ?replace. ?y <中文名> ?replace. ?y <武功> ?x. }
    '''
    temp_triples=[]
    triples=[]
    if len(tris)==1:return tris
    cn_e1=''
    cn_e2=''
    for t in tris:
        e1,r,e2=t.split(' ')
        if r=='<中文名>':cn_e1,cn_e2=e1,e2
        else:temp_triples.append(t)

    for t1 in temp_triples:
        t1 = t1.replace(cn_e2, cn_e1)
        if '?' not in t1:return tris
        triples.append(t1)
    # print(tris)
    # print(triples)
    return triples

def sparql2sexp(sparql):
    order_val=''
    order_opreator=''
    order_argmax=re.findall(r'order by desc.*', sparql.lower())
    order_argmin=re.findall(r'order by asc.*', sparql.lower())
    if len(order_argmax)!=0:
        order_val=re.findall('\?\w*',order_argmax[0])[0]
        order_opreator='ARGMAX'
    elif len(order_argmin)!=0:
        order_val = re.findall('\?\w*', order_argmin[0])[0]
        order_opreator = 'ARGMIN'

    temp_tar_join=defaultdict(list)#{顺序，join}
    pattern1 = re.compile(pattern=r"\{([^']+)\}")#找到最外层花括号的内容
    tris=re.findall(pattern1,sparql)[0].strip().split('.')
    tris=[t.strip() for t in tris  if t !='']
    # if '<中文名>' in sparql:
    #     triples=process_sp(tris)
    # else:triples=tris
    triples = tris
    entity_sequence=get_core_entity(triples)#得到实体出现的顺序['?x', '?b', '?c']
    operator_dic=[]
    for triple in triples:
        if 'filter' in triple:
            operator_dic.append(generate_operator(triple))#{?distance:LE}#['LE', '?distance', '5']
            continue#如果存在filter，则另处理
        vars,triple=split_t(triple)#得到单个三元组中的变量和{实体、<?x rel ent>}
        if len(vars)==1:#如果只有一个实体，那么默认为核心实体，合成问题后面再解决。
            core_entity = vars[0]
            if triple[0]==core_entity:#<?x rel ent>
                temp='JOIN {0} {1}'.format(triple[1],triple[-1])
                temp_tar_join[core_entity].append(temp)
            elif triple[-1]==core_entity:#<ent rel ?x>
                temp = 'JOIN (R {0}) {1}'.format(triple[1], triple[0])
                temp_tar_join[core_entity].append(temp)
            elif triple[1]==core_entity:#<ent ?x ent>即寻找关系
                temp='REL {0} {1}'.format(triple[0],triple[-1])
                temp_tar_join[core_entity].append(temp)
        elif len(vars)==2:#如果有两个实体，则按照实体顺序来确定核心实体
            # ['?x <主要病因>?b', '?b <并发症>?c', '?c<传染性> "无"']-->['?x', '?b', '?c']
            # JOIN 时优先保留后面的实体，因为求x要JOIN b，求b 要JOIN c
            #所以，在字典中，关键字为前面的，值为后面的，例如{?x:JOIN ?b,?b:JOIN ?c}
            v0=entity_sequence.index(vars[0])#第一个实体在seq中出现的位置
            v1=entity_sequence.index(vars[1])#第二个实体在seq中出现的位置
            core_entity=vars[0] if v0 < v1 else vars[1]
            other=vars[1] if v0 < v1 else vars[1]
            if triple[0]==core_entity and triple[1]!=other:#若<?x rel ?y>
                temp='JOIN {0} {1}'.format(triple[1],vars[1])#最终要将变量嵌入
                temp_tar_join[core_entity].append(temp)
            elif triple[0]==core_entity and triple[1]==other:#若<?x ?y ent>
                temp='JOIN {0} {1}'.format(other,triple[-1])#
                temp_tar_join[core_entity].append(temp)
            elif triple[-1]==core_entity and triple[1]!=other:#若<?y rel ?x>
                temp='JOIN (R {0}) {1}'.format(triple[1],vars[0])#最终要将变量嵌入
                temp_tar_join[core_entity].append(temp)
            elif triple[-1]==core_entity and triple[1]==other:#若<ent ?y ?x>
                temp='JOIN (R {0}) {1}'.format(other,triple[0])#最终要将变量嵌入
                temp_tar_join[core_entity].append(temp)
            elif triple[1]==core_entity and triple[0]==other :#<?y ?x ent >
                temp = 'REL {0} {1}'.format(other, triple[-1])  # 最终要将变量嵌入
                temp_tar_join[core_entity].append(temp)
            elif triple[1]==core_entity and triple[-1]==other :#< ent ?x ?y >
                temp = 'REL {0} {1}'.format(triple[0],other)  # 最终要将变量嵌入
                temp_tar_join[core_entity].append(temp)
        elif len(vars) == 3:  # 如果有两个实体，则按照实体顺序来确定核心实体
            v0 = entity_sequence.index(vars[0])  # 第一个实体在seq中出现的位置
            v1 = entity_sequence.index(vars[1])  # 第二个实体在seq中出现的位置
            v2 = entity_sequence.index(vars[2])  # 第二个实体在seq中出现的位置
            min_v=min(v0,v1,v2)
            core_entity='?x'
            if min_v==v0:
                core_entity=vars[0]
            elif min_v==v1:
                core_entity=vars[1]
            elif min_v==v2:
                core_entity=vars[2]
            if triple[0]==core_entity:
                temp = 'JOIN {0} {1}'.format(triple[1], triple[-1])  # 最终要将变量嵌入
                temp_tar_join[core_entity].append(temp)
            elif triple[1]==core_entity:
                temp = 'REL {0} {1}'.format(triple[0], triple[-1])  # 最终要将变量嵌入
                temp_tar_join[core_entity].append(temp)
            elif triple[-1]==core_entity:
                temp = 'JOIN {0} {1}'.format(triple[0], triple[-1])  # 最终要将变量嵌入
                temp_tar_join[core_entity].append(temp)

    final_tar_join={}

    #将filter 部分插入到该变量对应的词典里，也就是temp_tar_join，{?distance: op <关系> 值
    #找到

    for operator in operator_dic:
        if len(operator_dic)<1:break
        compare_operator, compare_var, compare_value=operator[0],operator[1],str(operator[2])
        rel=''
        if compare_var in temp_tar_join.keys():#select ?x where { <柳州丽笙酒店> <平均价格> ?x.  filter(?x < 600)}
            itemlist=temp_tar_join[compare_var][0].split(' ')
            if len(itemlist)==4:
                rel=itemlist[2].replace(')','')
            elif len(itemlist)==3:
                rel=itemlist[1]
            temp_tar_join[compare_var].append(compare_operator+' '+rel+' '+compare_value)
        else:
            for ks,vs in temp_tar_join.items():
                for v in vs:
                    if compare_var in v:
                        rel=v.split(' ')[1]
                        temp_tar_join[ks].append(compare_operator+' '+rel+' '+compare_value)
                        temp_tar_join[ks].remove(v)
    #print(temp_tar_join)
    #变量在key中时，获取关系，保留value
    #变量在value中时，获取关系，删除value
    order_rel=''
    if order_val in temp_tar_join.keys():
        itemlist=temp_tar_join[order_val][0].split(' ')
        if len(itemlist) == 4:
            order_rel = itemlist[2].replace(')', '')
        elif len(itemlist) == 3:
            order_rel = itemlist[1]
    elif len(order_val)!=0:
        for ks, vs in temp_tar_join.items():
            for v in vs:
                if order_val in v:
                    order_rel=v.split(' ')[1]
                    temp_tar_join[ks].remove(v)
    # if len(order_val)!=0:

#JOIN 平均价格 柳州丽笙酒店'
    for key,val in temp_tar_join.items():
        final_tar_join[key]=cluset(val)

    if final_tar_join=={}:
        return ""
    final_sexp=final_tar_join['?x']#初始为?x

    for item in entity_sequence:
        if item not in final_tar_join.keys():continue
        if item in final_sexp:
            if item=='?x':continue
            final_sexp=final_sexp.replace(item,'('+final_tar_join[item]+')')
    if order_rel!='':
        final_sexp=order_opreator+' ('+final_sexp+f') {order_rel}'
    return final_sexp

def read_data(file_path):
    '''
    问题：i%4=0
    Sparql：i%4=1
    答案：i%4=2
    分割：i%4=3
    '''
    dataset=open(file_path,'r',encoding='utf8').readlines()
    questions = []
    sparqls = []
    answers=[]
    i = 0
    for line in tqdm(dataset):
        if i % 4 == 0:
            q_id = re.findall('q\d*:', line)
            try:
                len(q_id) > 0
            except Exception:
                print(line)
                continue
            else:
                questions.append(line.replace(q_id[0], ''))
        if i % 4 == 1:
            sparqls.append(line)
        if i % 4 == 2:
            answers.append(line)
        i=i+1
    sexp_train = open('D:\桌面\毕业论文\ChatKBQA-main\ChatKBQA-main\data\CCKS\Sexper\\test_mtk.txt', 'a', encoding='utf8')
    error_sexp_train = open('D:\桌面\毕业论文\ChatKBQA-main\ChatKBQA-main\data\CCKS\Sexper\\error_sexp_train.txt', 'a', encoding='utf8')
    num=0
    for i in tqdm(range(len(questions))):
        question = questions[i]
        #print(question)
        if 'union' in sparqls[i]:
            line = questions[i] + sparqls[i] + answers[i] + '\n'
            # error_sexp_train.write(line)
            print(line)
            continue
        if 'UNION' in sparqls[i]:
            line = questions[i] + sparqls[i] + answers[i] + '\n'
            # error_sexp_train.write(line)
            print(line)
            continue
        if 'max' in sparqls[i]:
            line = questions[i] + sparqls[i] + answers[i] + '\n'
            # error_sexp_train.write(line)
            print(line)
            continue
        if 'count' in sparqls[i]:
            line = questions[i] + sparqls[i] + answers[i] + '\n'
            # error_sexp_train.write(line)
            print(line)
            continue
        if '大明神' in sparqls[i]:
            line = questions[i] + sparqls[i] + answers[i] + '\n'
            # error_sexp_train.write(line)
            print(line)
            continue#MINUS {
        if 'MINUS {' in sparqls[i]:
            line = questions[i] + sparqls[i] + answers[i] + '\n'
            # error_sexp_train.write(line)
            print(line)
            continue#MINUS {
        if '(avg(?replace) as ' in sparqls[i]:
            line = questions[i] + sparqls[i] + answers[i] + '\n'
            # error_sexp_train.write(line)
            print(line)
            continue#MINUS {
        if 'filter(?y < ?z)' in sparqls[i]:
            line = questions[i] + sparqls[i] + answers[i] + '\n'
            # error_sexp_train.write(line)
            print(line)
            continue#MINUS {
        if 'ter(?time < "18:00"^^<' in sparqls[i]:
            line = questions[i] + sparqls[i] + answers[i] + '\n'
            # error_sexp_train.write(line)
            print(line)
            continue#MINUS {
        if 'here { ?乔·布莱恩特	<中文名>	' in sparqls[i]:
            line = questions[i] + sparqls[i] + answers[i] + '\n'
            # error_sexp_train.write(line)
            print(line)
            continue#MINUS {
        if 'e_y where { <' in sparqls[i]:
            line = questions[i] + sparqls[i] + answers[i] + '\n'
            # error_sexp_train.write(line)
            print(line)
            continue#MINUS {
        try:
            sexp = sparql2sexp(sparqls[i])
            sexp=re.sub(r"(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff]+)", "_", sexp)
            num = num + 1
        except Exception:
            line = questions[i] + sparqls[i] + answers[i] + '\n'
            error_sexp_train.write(line)
            print(line)
        else:
            line = question + sexp+'\n' + answers[i] + '\n'
            #print(line)
            sexp_train.write(line)

if __name__ == '__main__':
    file_path= r'D:\桌面\毕业论文\ChatKBQA-main\ChatKBQA-main\data\CCKS\origin\CCKS_test.txt'
    read_data(file_path)
    # sparql='select ?x where { ?Y <毕业院校> <中国地质大学_（中国地质大学武汉校部）>. ?Y <中文名> "魏文博". ?Y <民族> ?x. } '
    # sexp=sparql2sexp(sparql)
    # print(sexp)
