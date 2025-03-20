from QA.query_graph import *
from QA.ltp import *

examples = [
    '贾宝玉的爷爷是谁？',
]

print('示例:')
q = examples[0]
print('Q:%s'%(q))
array = get_target_array(q)
res = get_KGQA_answer(array)
print('A:',end ="")
for i in res:
    print(i[0])
print()

print('请提问')
while True:
    q = input('Q:')
    array = get_target_array(q)
    res = get_KGQA_answer(array)
    print('A:',end ="")
    for i in res:
        print(i[0])
    print()
