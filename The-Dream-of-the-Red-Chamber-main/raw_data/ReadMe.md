### **实体及关系数据获取**

我们选择《红楼梦人物列表》维基百科网站中的表格数据文本作为数据爬取的目标。如图所示，我们提取的到表格中的姓名数据作为实体，提取得到表格中的人物简介，并对半结构化数据进行分析，从中抽取出人物关系三元组。最终我们可以得到包含两个实体一个关系的三元组格式，作为后续深度关系抽取技术结果的补充和比对。

* 网站表格数据获取操作指令

```shell
Input: ./raw_relation.html
Output: ./raw_data.xlsx
cd raw_data
python extract_raw_data.py
```

* 实体获取操作指令

```shell
Input: ./raw_data.xlsx
Output: ./entities.txt
cd raw_data
python extract_entities.py
```

* 人物关系三元组获取操作指令

```shell
Input: ./raw_data.xlsx
Output: ./raw_relations.txt
cd raw_data
python extract_relations.py
```

* 人物关系三元组清理操作指令

```shell
Input: ./raw_relations.txt
Output: ./relations.txt
cd raw_data
python clean_relations.py
```
