import os
import argparse
import json
import re_data
def dump_json(obj, fname, indent=4, mode='w' ,encoding="utf8", ensure_ascii=False):
    if "b" in mode:
        encoding = None
    with open(fname, "w", encoding=encoding) as f:
        return json.dump(obj, f, indent=indent, ensure_ascii=ensure_ascii)

def prepare_dataloader(args):
    print('Loading data from:', args.data_file_name)
    with open(args.data_file_name, 'r', encoding='utf-8') as f:
        # 读取每一行并转换为字典
        data = [json.loads(line) for line in f]
    print(f'Dataset len: {len(data)}')
    return data


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_file_name',
                        default='D:\桌面\毕业论文\ChatKBQA-main\ChatKBQA-main\Debug\Data\CCKS\evaluation_beam\generated_predictions.jsonl')

    args = parser.parse_args()
    return args


def run_prediction(args, dataloader, output_dir, output_predictions=True):
    print()
    print('Start predicting ')
    Error_list=[]
    First_True_list=[]
    All_True_list=[]

    ex_cnt = 0
    contains_ex_cnt = 0
    output_list = []
    real_total = 0
    for i, pred in enumerate(dataloader):
        predictions = pred['predict']
        gen_label = pred['label']

        output_list.append({
            'predictions': predictions,
            'gen_label': gen_label,
        })
        predictions_re = re_data.keep_spaces_between_words_only(predictions)  # 去除预测数据列表里的空格
        gen_label_re = re_data.keep_spaces_between_words(gen_label)  # 去除标签字符串的空格
        if predictions_re[0].lower() == gen_label_re.lower():
            ex_cnt += 1
            First_True_list.append(pred)
        if any([x.lower() == gen_label_re.lower() for x in predictions_re]):
            contains_ex_cnt += 1
            All_True_list.append(pred)
        if gen_label_re.lower() != 'null':
            real_total += 1
        #统计错误的信息的

        if predictions_re[0].lower() == gen_label_re.lower():
            First_True_list.append(pred)
        elif any([x.lower() == gen_label_re.lower() for x in predictions_re]):
            All_True_list.append(pred)
        else:
            Error_list.append(pred)
    print(f"""total:{len(output_list)}, 
                    ex_cnt:{ex_cnt}, 
                    ex_rate:{ex_cnt / len(output_list)}, 
                    real_ex_rate:{ex_cnt / real_total}, 
                    contains_ex_cnt:{contains_ex_cnt}, 
                    contains_ex_rate:{contains_ex_cnt / len(output_list)}
                    real_contains_ex_rate:{contains_ex_cnt / real_total}
                    """)
    # 样本总数、完全匹配和部分匹配的数量及比例。然后有个问题是，有的因为真是标签是null就排除在外。

    if output_predictions:
        output_dir="Data\\CCKS\\norml"
        file_path = os.path.join(output_dir, f'beam_test_top_k_predictions.json')

        gen_statistics_file_path = os.path.join(output_dir, f'beam_test_gen_statistics.json')
        gen_statistics = {
            'total': len(output_list),
            'exmatch_num': ex_cnt,
            'exmatch_rate': ex_cnt / len(output_list),
            'real_exmatch_rate': ex_cnt / real_total,
            'contains_ex_num': contains_ex_cnt,
            'contains_ex_rate': contains_ex_cnt / len(output_list),
            'real_contains_ex_rate': contains_ex_cnt / real_total
        }
        data_path="Data\\CCKS\\norml"
        Error_list_path  = os.path.join(data_path, f'Error_list.json')
        First_True_list_path   = os.path.join(data_path, f'First_True_list.json')
        All_True_list_path   = os.path.join(data_path, f'All_True_list.json')
        dump_json(output_list, file_path, indent=4)
        dump_json(gen_statistics, gen_statistics_file_path, indent=4)
        dump_json(First_True_list, First_True_list_path, indent=4)
        dump_json(All_True_list, All_True_list_path , indent=4)
        dump_json(Error_list, Error_list_path, indent=4)
def run_SM(args, dataloader, output_dir, output_predictions=True):
    print()
    print('Start predicting ')
    Error_list=[]
    First_True_list=[]
    All_True_list=[]

    ex_cnt = 0
    contains_ex_cnt = 0
    output_list = []
    real_total = 0
    for i, pred in enumerate(dataloader):
        predictions = pred['predict']
        gen_label = pred['label']

        output_list.append({
            'predictions': predictions,
            'gen_label': gen_label,
        })

        predictions_re_sm=re_data.replace_space_chinese_list(predictions)

        gen_label_re_sm=re_data.replace_space_chinese(gen_label)
        if predictions_re_sm[0].lower() == gen_label_re_sm.lower():
            ex_cnt += 1
            First_True_list.append(pred)
        if any([x.lower() == gen_label_re_sm.lower() for x in predictions_re_sm]):
            contains_ex_cnt += 1
            All_True_list.append(pred)
        if gen_label_re_sm.lower() != 'null':
            real_total += 1
        #统计错误的信息的

        if predictions_re_sm[0].lower() == gen_label_re_sm.lower():
            First_True_list.append(pred)
        elif any([x.lower() == gen_label_re_sm.lower() for x in predictions_re_sm]):
            All_True_list.append(pred)
        else:
            Error_list.append(pred)
    print(f"""total:{len(output_list)}, 
                    ex_cnt:{ex_cnt}, 
                    ex_rate:{ex_cnt / len(output_list)}, 
                    real_ex_rate:{ex_cnt / real_total}, 
                    contains_ex_cnt:{contains_ex_cnt}, 
                    contains_ex_rate:{contains_ex_cnt / len(output_list)}
                    real_contains_ex_rate:{contains_ex_cnt / real_total}
                    """)
    # 样本总数、完全匹配和部分匹配的数量及比例。然后有个问题是，有的因为真是标签是null就排除在外。

    if output_predictions:
        data_path="Data\\CCKS\\SM"
        file_path = os.path.join(data_path, f'beam_test_top_k_predictions_sm.json')

        gen_statistics_file_path = os.path.join(data_path, f'beam_test_gen_statistics_sm.json')
        gen_statistics = {
            'total': len(output_list),
            'exmatch_num': ex_cnt,
            'exmatch_rate': ex_cnt / len(output_list),
            'real_exmatch_rate': ex_cnt / real_total,
            'contains_ex_num': contains_ex_cnt,
            'contains_ex_rate': contains_ex_cnt / len(output_list),
            'real_contains_ex_rate': contains_ex_cnt / real_total
        }
        Error_list_path  = os.path.join(data_path, f'Error_list.json')
        First_True_list_path   = os.path.join(data_path, f'First_True_list.json')
        All_True_list_path   = os.path.join(data_path, f'All_True_list.json')
        dump_json(output_list, file_path, indent=4)
        dump_json(gen_statistics, gen_statistics_file_path, indent=4)
        dump_json(First_True_list, First_True_list_path, indent=4)
        dump_json(All_True_list, All_True_list_path , indent=4)
        dump_json(Error_list, Error_list_path, indent=4)
if __name__ == '__main__':
    args = _parse_args()
    print(args)

    test_dataloader = prepare_dataloader(args)
    run_prediction(args, test_dataloader, output_dir=os.path.dirname(args.data_file_name), output_predictions=True)
    run_SM(args, test_dataloader, output_dir=os.path.dirname(args.data_file_name), output_predictions=True)#纯骨架的

    print('Prediction Finished')

