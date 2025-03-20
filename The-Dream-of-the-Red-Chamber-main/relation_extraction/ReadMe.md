### 实体标注与关系抽取

#### 训练模型
在训练之前需要下载预训练模型和数据并放在pretrain(下载地址：https://github.com/ymcui/Chinese-BERT-wwm)，然后调用train.py进行训练。
```commandline
python train.py
```

#### 关系抽取
调用extraction.py进行基于匹配的实体标注和关系抽取。
```commandline
python extraction.py
```