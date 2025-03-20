# -*- coding: utf-8 -*-
import pyltp 
import os
LTP_DATA_DIR = '/Users/heqianpei/Downloads/The-Dream-of-the-Red-Chamber-main/QA/ltp_data_v3.4.0'  # ltp模型目录的路径. you can download it from http://model.scir.yunfutech.com/model/ltp_data_v3.4.0.zip


def cut_words(words):
    seg_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')
    segmentor = pyltp.Segmentor(seg_model_path)
    words = segmentor.segment(words)
    array_str="|".join(words)
    array=array_str.split("|")
    segmentor.release()
    return array


def words_mark(array):
    # 词性标注模型路径，模型名称为`pos.model`
    pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')
    postagger = pyltp.Postagger(pos_model_path)  # 初始化实例
    postags = postagger.postag(array)  # 词性标注
    pos_str=' '.join(postags)
    pos_array=pos_str.split(" ")
    postagger.release()  # 释放模型
    return pos_array

def get_target_array(words):
    target_pos=['nh','n']
    target_array=[]
    seg_array=cut_words(words)
    pos_array = words_mark(seg_array)
    for i in range(len(pos_array)):
        if pos_array[i] in target_pos:
            target_array.append(seg_array[i])
    target_array.append(seg_array[1])
    return target_array





