import pandas as pd
import openpyxl

def append_excel(data,excelname,sheetname,insert_type):
    original_file = pd.DataFrame(pd.read_excel(excelname, sheet_name=sheetname))  # 读取原数据文件和表
    original_row = original_file.shape[0]  # 获取原数据的行数
    if insert_type=='w':       #选择写入excel数据方式，w为覆盖模式，a+为追加模式
        startrow=1
    elif insert_type=='a+':
        startrow=original_row + 1
    book = openpyxl.load_workbook(excelname)
    writer = pd.ExcelWriter(excelname, engine='openpyxl')
    writer.book = book
    writer.sheets = dict((ws.title, ws) for ws in book.worksheets)

    # 将data数据写入Excel中
    data.to_excel(writer, sheet_name=sheetname, startrow=startrow, index=False, header=False)
    writer.save()
    
    
if __name__ == '__main__':
    df = pd.read_html("./raw_relation.html", encoding='utf-8', header=0)
    num = len(df)
    for i in range(num-4):
        append_excel(df[i], './raw_data.xlsx', 'Sheet1', 'a+')
