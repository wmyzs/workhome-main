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

parser.add_argument('--original_data_file', type=str, help='Original data file path', default="D:\桌面\毕业论文\ChatKBQA-main\ChatKBQA-main\Debug\Data\Web_data\SM\\beam_test_top_k_predictions_sm.json")
parser.add_argument('--target_data_file', type=str, help='Processed file path', default="D:\桌面\毕业论文\ChatKBQA-main\ChatKBQA-main\Debug\Data\LJXS2nl\\target_data.json")

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
    print(len(data))
    for i, entry in enumerate(tqdm(data, desc="Processing")):
        # 动态构造 prompt 字符串
        prompt = (
            "你现在的任务是将给定的查询语句（以逻辑形式表示）翻译成自然语言问题。请注意，查询语句可能非常相似，因此你需要特别关注并准确地翻译其中的细微差异。请参考以下示例进行操作：\n\n"

            "#### 示例：\n\n"
            "逻辑形式：\n"
            "L1: ( JOIN ( R [ location, location, time zones ] ) [ Louisiana ] )\n"
            "L2: ( JOIN ( R [ location, location, timezones ] ) [ Louisiana ] ) [ time zone ]\n"
            "L3: ( JOIN ( R [ location, location, location contained by ] ) [ Louisiana ] )\n\n"
            "输出：\n"
            "Q1: What are the time zones for Louisiana?\n"
            "Q2: What are the time zones for Louisiana?\n"
            "Q3: What is Louisiana contained by?\n\n"

            "#### 输入：\n\n"
            "逻辑形式：\n"
        )

        # 遍历 predictions 列表，并将每个查询语句添加到 prompt 中
        for query in entry['predictions']:
            prompt += f"{query}\n"
        # 输出构造的 prompt
        prompt+=(
            "输出：\n"
            "请根据输入的逻辑形式翻译成自然语言问题:\n"
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
            new_datum = {
                'metaphor_id': i,
                'predictions': entry['predictions'],
                "gen_label":entry['gen_label']

            }
            prediction = response.choices[0].message.content
            new_datum["question"] = prediction
            new_data.append(new_datum)
            if len(new_data) % 100 == 0:
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
                new_datum = {
                    'metaphor_id': i,
                    'predictions': entry['predictions'],
                    "gen_label": entry['gen_label']

                }
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
                new_datum = {
                    'metaphor_id': i,
                    'predictions': entry['predictions'],
                    "gen_label": entry['gen_label']

                }
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