# -*- coding: utf-8 -*-

import random
from openai import OpenAI
import openai
import time
import json
from tqdm import tqdm
import argparse

'''生成干扰选项'''

MAX_LENGTH = 2048

# Modify the api key with yours
client = OpenAI(api_key="sk-IPi2DJviCl2QFb3E3d593953Ae4c473b94C50602F7581fEe", base_url="https://api.expansion.chat/v1")

parser = argparse.ArgumentParser(description='Generate some error options')

parser.add_argument('--original_data_file', type=str, help='Original data file path', default="D:\桌面\毕业论文\ChatKBQA-main\ChatKBQA-main\Debug\Data\LJXS2nl\merge.json")
parser.add_argument('--target_data_file', type=str, help='Processed file path', default="D:\桌面\毕业论文\ChatKBQA-main\ChatKBQA-main\Debug\Data\LJXS2nl\\socure_data.json")

args = parser.parse_args()

original_data_file = args.original_data_file
target_data_file = args.target_data_file

def get_answer(messages):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        max_tokens=100,
        temperature=0.2,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        messages=messages
    )

    return response

with open(original_data_file, encoding="utf-8") as f:
    data = json.load(f)
    new_data = []
    index = 1
    for i, entry in enumerate(tqdm(data, desc="Processing")):

        # 动态构造 prompt 字符串
        prompt = (
            "你现在的任务是知识图谱问答。请根据原问题与生成问题得到的是否可以在知识图谱中获得同一个答案,是同一个答案返回相似度的分，区间为0-1，不是得分为0，并排序：\n\n"
            "#### 示例：\n\n"
            "原问题：what famous people came from delaware\n"
            "生成问题\n"
            "Q1: Who are notable individuals born in Delaware?\n"
            "Q2: Who was born in Delaware?\n"
            "Q3: Where was Person born?\n"
            "输出：\n"
            "Q1:相似度：{0.5}\n"
            "Q2:相似度：{1}\n"
            "Q3:相似度：{0}\n"
            "#### 输入：\n\n"
            f"原问题：{entry['query']}\n\n"
            "生成问题\n"
        )

        if len(entry["predictions"])==len(entry["question"]):
            print(entry['question'])
            for went in entry['question']:
                print(went)
                prompt += f"{went}\n"
            # 输出构造的 prompt
        else:
            prompt = (
                "你现在的任务是知识图谱问答。请根据原问题与逻辑形式判断是否可以根据逻辑形式在知识图谱中获得同一个答案，进行评价，是同一个答案返回可能性分，区间为0-1，不是得分为0，并排序：\n\n"
                "#### 示例：\n\n"
                "原问题：what famous people came from delaware\n"
                "逻辑形式\n"
                "L1:( JOIN ( R [ location, location, people born here ] ) [ Delaware ] )\n"
                "L2:( JOIN ( R [ people, place of birth, notable individuals ] ) [ Delaware ] )\n"
                "L3:( JOIN ( R [ people, person, place of birth ] ) [ Person ] )\n"
                "L4:(JOIN (R [ people, person, place of birth ]) [ Delaware ])\n"
                "输出：\n"
                "L1: 相似度：{1}"
                "L2:相似度：{0.9}\n"
                "L3:相似度：{0.7}\n"
                "L4:相似度：{0.2}\n"
                "#### 输入：\n\n"
                f"原问题：{entry['query']}\n\n"
                "逻辑形式\n"
            )
            j=0
            for went in entry['predictions']:
                print(went)
                prompt += f"L{j}:{went}\n"
        prompt+=(
            "输出：\n"
            "请排序并给出相似的得分:\n"
        )


        print("=====================================================================================")
        print(f"data-{i+1}, prompt:\n{prompt}")
        messages = [
            {
                "role": "system",
                "content": "你是一位熟知知识图谱问答的专家！"
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        try:
            response = get_answer(messages)
            print(f"response:\n{response.choices[0].message.content}")
            print("=====================================================================================")
            new_datum = entry
            prediction = response.choices[0].message.content
            new_datum["question"] = prediction
            new_data.append(new_datum)
            if len(new_data) % 10 == 0:
                json.dump(new_data,
                          open(f"D:\桌面\毕业论文\ChatKBQA-main\ChatKBQA-main\Debug\Data\LJXS2nl\\temp_data_{index + 1}.json", 'w', encoding="utf-8"),
                          indent=4, ensure_ascii=False)

                index += 1
        except openai.RateLimitError as e:
            print("遇到 RateLimitError，5s后尝试重连OpenAI...")
            # 等待一段时间，避免过于频繁地重试
            time.sleep(5)
            # 重新预测，继续捕获异常，看看会不会在此处仍发生异常
            try:
                response = get_answer(messages)
                print(f"response:\n{response.choices[0].message.content}")
                print("=====================================================================================")
                new_datum = entry
                prediction = response.choices[0].message.content
                new_datum["question"] = prediction
                new_data.append(new_datum)
                if len(new_data) % 100 == 0:
                    json.dump(new_data,
                              open(
                                  f"D:\桌面\毕业论文\ChatKBQA-main\ChatKBQA-main\Debug\Data\LJXS2nl\\temp_data_{index + 1}.json",
                                  'w', encoding="utf-8"),
                              indent=4, ensure_ascii=False)
                    index += 1
            except openai.RateLimitError as e:
                print("发送请求太频繁了！30s后尝试重连OpenAI...")
                time.sleep(30)
                response = get_answer(messages)
                new_datum = entry
                prediction = response.choices[0].message.content
                new_datum["question"] = prediction
                new_data.append(new_datum)
                if len(new_data) % 100 == 0:
                    json.dump(new_data,
                              open(
                                  f"D:\桌面\毕业论文\ChatKBQA-main\ChatKBQA-main\Debug\Data\LJXS2nl\\temp_data_{index + 1}.json",
                                  'w', encoding="utf-8"),
                              indent=4, ensure_ascii=False)
                    index += 1
            except Exception as e:
                json.dump(new_data, open(target_data_file, 'w', encoding="utf-8"), indent=4, ensure_ascii=False)
                print("遇到其他错误:", e)
        except Exception as e:
            # 若是遇到其他异常，立马保存已预测得到的数据
            json.dump(new_data, open(target_data_file, 'w', encoding="utf-8"), indent=4, ensure_ascii=False)
            print("遇到其他错误:", e)

    with open(target_data_file, "w") as f:
        json.dump(new_data, open(target_data_file, 'w', encoding="utf-8"), indent=4, ensure_ascii=False)