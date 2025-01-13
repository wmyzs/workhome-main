from tqdm import tqdm
import re
from collections import defaultdict
import json

def dump_json(obj, fname, indent=4, mode='w' ,encoding="utf8", ensure_ascii=False):
    if "b" in mode:
        encoding = None
    with open(fname, "w", encoding=encoding) as f:
        return json.dump(obj, f, indent=indent, ensure_ascii=ensure_ascii)
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
    new_datalist=[]
    i = 0
    for line in tqdm(dataset):
        if i % 4 == 0:
            parts = line.rstrip("？?\n")
            parts=parts.rstrip("\n")
        if i % 4 == 1:
            sparqls=line.rstrip("\n")
        if i % 4 == 2:
            answer=line
        if i % 4 == 2:
            gen_NQ_train(new_datalist,parts,sparqls)



        i=i+1
    return new_datalist

def gen_NQ_train(new_datalist,Question,Sparql):
    new_datalist.append(
        {

            "instruction": "根据问题生成一个逻辑形式查询，以检索与所给问题相对应的信息。 \n",
            "input": Question,
            "output": Sparql,
            "history": []}
    )

def gen_NQ_Web_train(Question, Sparql):
    new_datalist.append({
        "QuestionId": parts[0],
        "RawQuestion": parts[1],
        "Sparql": sparqls,
        "Answer": answer
        })

if __name__ == '__main__':
    # new_datalist=read_data("D:\桌面\毕业论文\ChatKBQA-main\ChatKBQA-main\data\CCKS\origin\CCKS_train.txt")
    # dump_json(new_datalist, "D:\桌面\毕业论文\ChatKBQA-main\ChatKBQA-main\data\CCKS\Sexper\CCKS_train_Sexper", indent=4)
    # new_datalist=read_data("D:\桌面\毕业论文\ChatKBQA-main\ChatKBQA-main\data\CCKS\origin\CCKS_test.txt")
    # dump_json(new_datalist, "D:\桌面\毕业论文\ChatKBQA-main\ChatKBQA-main\data\CCKS\Sexper\CCKS_test_Sexper", indent=4)
    new_datalist=read_data("D:\桌面\毕业论文\ChatKBQA-main\ChatKBQA-main\data\CCKS\Sexper\\test_mtk.txt")
    dump_json(new_datalist, "D:\桌面\毕业论文\ChatKBQA-main\ChatKBQA-main\LLMs\data\CCKS_NQ_test\examples.json", indent=4)
