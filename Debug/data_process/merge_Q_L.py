import json

# 读取文件1

# 读取文件2
with open('D:\桌面\毕业论文\ChatKBQA-main\ChatKBQA-main\data\WebQSP\generation\merged\WebQSP_test.json', 'r', encoding='utf-8') as f1:
    file1_data = json.load(f1)
with open('D:\桌面\毕业论文\ChatKBQA-main\ChatKBQA-main\Debug\Data\LJXS2nl\\target_data.json', 'r', encoding='utf-8') as f2:
    file2_data = json.load(f2)
with open('D:\桌面\毕业论文\ChatKBQA-main\ChatKBQA-main\Debug\Data\Web_data\SM\\beam_test_top_k_predictions_sm.json', 'r', encoding='utf-8') as f3:
    file3_data = json.load(f3)
new_data=[]
# 遍历文件1的数据
print(len(file1_data),len(file2_data),len(file3_data))
j=0
for i in range(len(file1_data)):
    if file1_data[i]["normed_sexpr"]==file2_data[j]["gen_label"]:
        questions_list = file2_data[j]['question'].split('\n')
        # 去掉每个问题的 "Q1:", "Q2:" 等部分
        new_datum={
                     "metaphor_id": file2_data[j]['metaphor_id'],
                     "query":file1_data[i]["question"],
                     "predictions":file2_data[j]['predictions'],
                     "gen_label": file2_data[j]['gen_label'] ,
                     "question":questions_list
        }
        j=j+1
    elif file1_data[i]["normed_sexpr"]==file3_data[i]["gen_label"]:
        new_datum={
                     "metaphor_id": i,
                     "query":file1_data[i]["question"],
                     "predictions":file3_data[j]['predictions'],
                     "gen_label": file3_data[i]["gen_label"] ,
                     "question": "null",
        }
    else:
        print(i)
    new_data.append(new_datum)
# 保存新的文件2
with open('D:\桌面\毕业论文\ChatKBQA-main\ChatKBQA-main\Debug\Data\LJXS2nl\\merge.json', 'w', encoding='utf-8') as f_new:
    json.dump(new_data, f_new, ensure_ascii=False, indent=4)


"""
        "metaphor_id": 28,
        "query": "where is the galapagos islands located on a world map",
        "predictions": [
            "( JOIN ( R [ location, location, containedby ] ) [ Galápagos Islands ] )",
            "( AND ( JOIN [ common, topic, notable types ] [ Region ] ) ( JOIN ( R [ location, location, containedby ] ) [ Galápagos Islands ] ) )",
            "( JOIN ( R [ location, location, containedby ] ) [ Galapagos Islands ] )"
        ],
        "gen_label": "( JOIN ( R [ location , location , containedby ] ) [ Galápagos Islands ] )",
        "question": "Q1:相似度：{0.5}\nQ2:相似度：{0}\nQ3:相似度：{1}"
    },"""
print("文件已保存为 new_file2.json")
