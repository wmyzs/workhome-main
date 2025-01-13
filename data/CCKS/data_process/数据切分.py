# -*- coding: utf-8 -*-
# @Time    : 2023/4/11 17:43
# @Author  : Zhang Jinzhao
# @Email   : zhangjinzhao2021@163.com
# @File    : 数据切分.py
# @Software: PyCharm

import random

# 读取原始文本文件
with open('D:\桌面\毕业论文\ChatKBQA-main\ChatKBQA-main\data\CCKS\origin\\train.txt', 'r', encoding='utf8') as f:
    lines = f.readlines()

# 打乱文本行的顺序
grouped_data = [lines[i:i+4] for i in range(0, len(lines), 4)]
random.shuffle(grouped_data)

train_size = int(0.8* len(grouped_data))
val_size = int(0.2 * len(grouped_data))
test_size = len(grouped_data) - train_size - val_size
# 计算切分比例
num_lines = len(lines)
train_data = grouped_data[:train_size]
test_data = grouped_data[train_size:]
print(test_data[0])
# 将文本行写入文件
with open('D:\桌面\毕业论文\ChatKBQA-main\ChatKBQA-main\data\CCKS\origin\\CCKS_train.txt', 'w',encoding='utf8') as f:
    for items in train_data:
        f.writelines(items)

with open('D:\桌面\毕业论文\ChatKBQA-main\ChatKBQA-main\data\CCKS\origin\CCKS_test.txt', 'w',encoding='utf8') as f:
    for items in test_data:
        f.writelines(items)

