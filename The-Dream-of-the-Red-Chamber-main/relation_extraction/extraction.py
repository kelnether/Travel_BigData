import re
import sys, json
import torch
import os
import numpy as np
import opennre
from opennre import encoder, model
import argparse
import pandas as pd
import itertools

# 导入关系抽取模型

parser = argparse.ArgumentParser()
parser.add_argument('--mask_entity', action='store_true', help='Mask entity mentions')
args = parser.parse_known_args()[0]

root_path = '.'
sys.path.append(root_path)
if not os.path.exists('ckpt'):
    os.mkdir('ckpt')
ckpt = 'ckpt/people_chinese_bert_softmax.pth.tar'

rel2id = json.load(open(os.path.join(root_path, 'benchmark/people-relation/people-relation_rel2id.json'), encoding='utf-8'))

sentence_encoder = opennre.encoder.BERTEncoder(
    max_length=80, 
    pretrain_path=os.path.join(root_path, 'pretrain/chinese_wwm_pytorch'),
    mask_entity=args.mask_entity
)

model = opennre.model.SoftmaxNN(sentence_encoder, len(rel2id), rel2id)
model.load_state_dict(torch.load(ckpt)['state_dict'])

with open("data/hong.txt", "r", encoding="utf-8") as f:
    total_lines = [line.strip() for line in f.readlines()]

total_lines = [line for line in total_lines if line != '']

# 分句
cutLineFlag = ["？", "！", "。", "!", "“", "”", "：", "；"]
sentenceList = []
for words in total_lines:
    oneSentence = ""
    for word in words:
        if word not in cutLineFlag:
            oneSentence = oneSentence + word
        else:
            oneSentence = oneSentence + word
            if oneSentence.__len__() > 4:
                sentenceList.append(oneSentence.strip())
            oneSentence = ""

# 获取所有的实体

with open("data/entities.txt", "r", encoding="utf-8") as f:
    total_id = list(set([line.strip() for line in f.readlines()]))

print("共有实体：", len(total_id))


new_data = []
for sentence in sentenceList:
    id_loc = []
    id_list = []
    for id in total_id:
        if id in sentence:
            loc = [(item.start(), item.end()-1) for item in re.finditer(id, sentence)]
            id_list.append(id)
            id_loc.append(loc[0])
            # print(id_loc)
        
    if len(id_loc) >= 2:
        permute = list(itertools.combinations(range(len(id_list)), 2))
        # print(len(permute))
        for idx in permute:
            if id_list[idx[0]] not in id_list[idx[1]] and id_list[idx[1]] not in id_list[idx[0]]:
                new_data.append({'text':sentence, 'h': {'pos': id_loc[idx[0]]}, 't': {'pos': id_loc[idx[1]]}})

print("共构造数据集:", len(new_data))

print(new_data[0])
print(new_data[1])
print(new_data[2])

from tqdm import tqdm
relation_list = []
for data in tqdm(new_data):
    text = data['text']
    t_pos = data['t']['pos']
    h_pos = data['h']['pos']
    rela = model.infer(data)
    relation_list.append([text[t_pos[0]:t_pos[1]+1], text[h_pos[0]:h_pos[1]+1], rela])


relation_df = pd.DataFrame(relation_list)
relation_df.to_csv("data/relation_infer.csv", header=False, index=False)

obj_list = {}

for item in relation_list:
    if item[2][0] != 'unknown' and item[2][1] > 0.95:
        if (item[0], item[1]) not in obj_list.keys():
            obj_list[(item[0], item[1])] = {'relation': [item[2][0]], 'prob': [item[2][1]]}
        else:
            if item[2][0] not in obj_list[(item[0], item[1])]['relation']: # 合并重复的实体对，以及其所有的候选关系
                obj_list[(item[0], item[1])]['relation'].append(item[2][0])
                obj_list[(item[0], item[1])]['prob'].append(item[2][1])

new_relation_list = []
for key, value in obj_list.items():
    new_relation_list.append([key[0], key[1], value['relation'][np.argmax(value['prob'])]])

relation_df = pd.DataFrame(new_relation_list)
relation_df.to_csv("data/relation_raw.csv", header=False, index=False)
