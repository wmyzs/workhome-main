# -*- coding: utf-8 -*-
# @Time    : 2023/4/27 9:11
# @Author  : Zhang Jinzhao
# @Email   : zhangjinzhao2021@163.com
# @File    : 数据集切分.py
# @Software: PyCharm
import os
import argparse
import re_data
import json
import random
"""
切割数据集
"""

def dump_json(obj, fname, indent=4, mode='w' ,encoding="utf8", ensure_ascii=False):
    if "b" in mode:
        encoding = None
    with open(fname, "w", encoding=encoding) as f:
        return json.dump(obj, f, indent=indent, ensure_ascii=ensure_ascii)

def prepare_dataloader(file_name):  #按行读取数据集
    print('Loading data from:', file_name)
    with open(file_name, 'r', encoding='utf-8') as f:
        # 读取每一行并转换为字典
        data = [json.loads(line) for line in f]
    print(f'Dataset len: {len(data)}')
    return data
def read_json(file_name):  #正常读取json
    with open(file_name, 'r', encoding='utf-8') as file:
        data = json.load(file)  # 使用 json.load() 解析 JSON 文件
    print(f'Dataset len: {len(data)}')
    return data
def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_file_name',
                        default='../../Reading/Web_data/evaluation_beam/generated_predictions.jsonl')
    parser.add_argument('--data_test_name',
                        default='../../data/WebQSP/generation/merged/WebQSP_test.json')

    args = parser.parse_args()
    return args

def run_merge(args,A_test_dataloader, Q_test_dataloader , output_dir, output_predictions=True):#把问题与标签合并
    numbers_0=0
    numbers_1=0
    numbers_2=0
    number_all=[]#统计0，1，2的数量
    output_list = []
    for i, pred in enumerate(A_test_dataloader):
        predictions = pred['predict']
        gen_label = pred['label']

        if gen_label==Q_test_dataloader[i]["normed_sexpr"]:
            question=Q_test_dataloader[i]["question"]
        predictions_re = re_data.keep_spaces_between_words_only(predictions)  # 去除预测数据列表里的空格
        gen_label_re = re_data.keep_spaces_between_words(gen_label)  # 去除标签字符串的空格

        predictions_re_sm=re_data.replace_space_list(predictions_re)
        gen_label_re_sm=re_data.replace_space_str(gen_label_re)

        if predictions_re_sm[0].lower() == gen_label_re_sm.lower():
            lable="First_True"
            numbers_0 = numbers_0+1
        elif any([x.lower() == gen_label_re_sm.lower() for x in predictions_re_sm]):
            lable="Contains_True"
            numbers_1 = numbers_1+1
        else:
            lable="Error"
            numbers_2 = numbers_2+1
        output_list.append({
            'question':question,
            'predictions': predictions,
            'gen_label': gen_label,
            'label':lable
        })
    number_all={
        "First_True": numbers_0,
        "Contains_True": numbers_1,
        "Error": numbers_2
    }
    return output_list,number_all
def split(output_list,number_all):  #切分数据集
    print("Straing split")
    random.shuffle(output_list)

    # 计算切分比例
    num_lines = len(output_list)
    train_ratio = 0.8

    # 计算切分点
    train_split = int(num_lines * train_ratio)
    # 切分文本行
    train_lines = output_list[:train_split]
    test_lines = output_list[train_split:]
    dump_json(train_lines, "../Data/Web_data/classifier/three_type/Web_train_split.json", indent=4)
    dump_json(test_lines ,"../Data/Web_data/classifier/three_type/Web_test.json_split",indent=4)
    number_all["train_lines"]=len(train_lines)
    number_all["test_lines"]=len(test_lines)
    print(number_all)
    dump_json(number_all, "../Data/Web_data/classifier/three_type/gen_statistics_split.json", indent=4)

if __name__ == '__main__':
    args = _parse_args()

    A_test_dataloader = prepare_dataloader(args.data_file_name)
    Q_test_dataloader = read_json(args.data_test_name)

    merge_line,number_all=run_merge(args, A_test_dataloader, Q_test_dataloader ,output_dir=os.path.dirname(args.data_file_name), output_predictions=True)#纯骨架的
    split(merge_line,number_all)#目前是三种标签，会尝试两中

