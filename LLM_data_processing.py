import os
import pandas as pd
"""
1.合并总表
2.添加学科
3.逐行判断，判断项目编号是否重复出现
无法判断的进行归类
"""
def merge_excel(input_excel, output_file,column_name):
    #将不同的excel合并到同一个excel中
    consolidated_data = pd.DataFrame()
    for file_name, columns in input_excel.items():
        base_path = r"D:\\大模型项目20241026\\12.11\\12.11工作表\\任务2\\纵向"
        file_path = os.path.join(base_path, file_name)
        print("columns:",columns)
        try:
            # 读取所有工作表
            all_sheets = pd.read_excel(file_path, sheet_name=None)
            # 遍历每个工作表
            for sheet_name, df in all_sheets.items():
                r_df = df[columns].reindex(columns=columns, fill_value=None)
                r_df.rename(columns={columns[0]: column_name[0],
                                     columns[1]: column_name[1],
                                     columns[2]: column_name[2],
                                     columns[3]: column_name[3],
                                     columns[4]: column_name[4]}, inplace=True)
                consolidated_data = pd.concat(
                    [consolidated_data, r_df[column_name]], ignore_index=True
                )

                print(f"当前合并数据的行数: {consolidated_data.shape[0]} 行")

        except Exception as e:
            print(f"读取文件 {file_name} 时出错: {e}")
    # 保存最终的汇总表
    consolidated_data.to_excel(output_file, index=False)
    print(f"汇总完成，已保存到: {output_file}")


if __name__ == '__main__':
    # 输入文件及需要保留的列
    input_excel = {
        "2020-2024年纵向科研项目--其他国家级项目.xls": ["负责人", "院系", "项目名称", "项目编号", "项目类型"],
        "2020年-2021年国家和部委级项目汇总（纵向）.xlsx": ["姓名", "学院名称", "课题名称", "项目批准号", "项目级别"],
    }
    column_name=["负责人", "院系", "项目名称", "项目编号", "项目类型"] #合并后格列的名称
    # 输出文件路径
    output_file = r"D:\大模型项目20241026\12.11\12.11工作表\任务2\纵向\汇总表.xlsx" #合并路径
    # 执行函数
    merge_excel(input_excel, output_file,column_name) #将同一项目进行合并


