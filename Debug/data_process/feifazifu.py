import chardet

# 检测文件编码
file_path = 'D:\桌面\毕业论文\ChatKBQA-main\ChatKBQA-main\LLMs\data\CCKS_NQ_test\examples.json'
# 从文件中读取内容并输出


# 尝试用 UTF-8 读取，处理编码问题
try:
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        print(content)
except UnicodeDecodeError:
    print("UTF-8 解码失败，尝试检测文件编码...")

    # 自动检测文件编码
    import chardet
    with open(file_path, 'rb') as file:
        raw_data = file.read()
        detected_encoding = chardet.detect(raw_data)['encoding']
        print(f"检测到的文件编码：{detected_encoding}")

    # 使用检测到的编码重新读取文件
    with open(file_path, 'r', encoding=detected_encoding, errors='replace') as file:
        content = file.read()
        print(content)

