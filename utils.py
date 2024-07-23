import jieba
from pypinyin import lazy_pinyin


def jaccard_similarity(text1, text2):
    words1 = set(jieba.lcut("".join(lazy_pinyin(text1))))
    words2 = set(jieba.lcut("".join(lazy_pinyin(text2))))
    intersection = len(words1 & words2)
    union = len(words1 | words2)
    if words2 in words1:
        return 1
    return intersection / union
