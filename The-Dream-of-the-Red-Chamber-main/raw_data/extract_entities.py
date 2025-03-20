# read excel
import pandas as pd
df = pd.read_excel('./raw_data.xlsx', sheet_name='Sheet1')
# extract entities
all_entities = []
for i in range(len(df)):
    all_entities.append(df.iloc[i, 0])
with open('entities.txt', 'w', encoding='utf-8') as f:
    for t in all_entities:
        f.write(t.strip() + '\n')