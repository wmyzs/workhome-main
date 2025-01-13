import re
#执行run_generator_final.py时，由于空格无法匹配因此进行格式的统一
def keep_spaces_between_words_only(lst):
    #去除符号之间的空格
    cleaned_list = []
    for s in lst:
        # 去除符号与字母之间的空格
        s = re.sub(r'\s+([.,()\[\]])', r'\1', s)  # 删除符号前的空格
        s = re.sub(r'([.,()\[\]])\s+', r'\1', s)  # 删除符号后的空格

        # 保留两个英文单词之间的空格，删除其他地方的空格
        s = re.sub(r'(\b\w+\b)\s+(\b\w+\b)', r'\1 \2', s)  # 只保留两个英文单词间的空格

        cleaned_list.append(s)
    return cleaned_list
def keep_spaces_between_words(s):

    s = re.sub(r'\s+([.,()\[\]])', r'\1', s)  # 删除符号前的空格
    s = re.sub(r'([.,()\[\]])\s+', r'\1', s)  # 删除符号后的空格
        # 保留两个英文单词之间的空格，删除其他地方的空格
    s = re.sub(r'(\b\w+\b)\s+(\b\w+\b)', r'\1 \2', s)  # 只保留两个英文单词间的空格

    return s
def replace_space_list(list): #将列表里的字元素进行替换
    cleaned_list = []
    for s in list:
        # 去除符号与字母之间的空格
        output_string = re.sub(r'\[.*?\]', '[ ]', s)
        cleaned_list.append(output_string)
    return cleaned_list

def replace_space_str(s):
    output_string = re.sub(r'\[.*?\]', '[ ]', s)

    return output_string
def replace_space_chinese(text):


    # 步骤1: 按空格切分字符串
    parts = text.split()
    # 步骤2: 替换带有汉字的元素
    # 使用正则表达式来匹配带汉字的元素
    parts = [part if not re.search(r'[\u4e00-\u9fa5]', part) else '[占位符]' for part in parts]
    # 步骤3: 重新拼接成字符串
    result = ' '.join(parts)
    return result
def replace_space_chinese_list(list):
    cleaned_list = []
    for text in list:
        # 去除符号与字母之间的空格
        parts = text.split()
        # 步骤2: 替换带有汉字的元素
        # 使用正则表达式来匹配带汉字的元素
        parts = [part if not re.search(r'[\u4e00-\u9fa5]', part) else '[占位符]' for part in parts]
        # 步骤3: 重新拼接成字符串
        result = ' '.join(parts)
        cleaned_list.append(result)
    return cleaned_list
    # 步骤1: 按空格切分字符串
if __name__=='__main__':
    input="( AND ( JOIN [ base, biblioness, bibs location, loc type ] [Country] ) ( JOIN ( R [ location, location, containedby ] ) [ Greenland ] ) )"
    text = "JOIN (R 项目短描述) (JOIN 类型_故宫博物院（故宫）)"
    out_put=replace_space_chinese(text)
    print(out_put)