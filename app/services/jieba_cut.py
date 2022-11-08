import re

import jieba.analyse
import jieba.posseg as psg


def load_user_dict(s, user_dict_list):
    # 用户词典去重
    user_dict_list = list(set(user_dict_list))

    user_dict = []

    for word in user_dict_list:
        res = re.findall(word, s, re.I)

        if res:
            res = list(set(res))
            for i in res:
                user_dict.append(i)
        else:
            user_dict.append(word)

    user_dict = list(set(user_dict))

    for word in user_dict:
        jieba.add_word(word, freq=100000000, tag='nz')

    return user_dict


def gen_word_cloud_data(content, allow_pos=(), stop_words=None, similar_words=None, topk=100, min_word_count=1):
    # 加载停用词
    if stop_words is None:
        stop_words = []
    stop_words_list = []

    for stop_word in stop_words:
        stop_words_list.extend(re.findall(stop_word, content, re.I))

    # 加载相似词
    if similar_words is None:
        similar_words = {}

    for k, v in similar_words.items():
        content = re.sub(v, k, content, flags=re.I)

    # 分词生成list
    words = psg.cut(content)

    # 分词权重计算
    keywords_weight = jieba.analyse.extract_tags(
        content,
        topK=topk * 2,
        withWeight=True,
        allowPOS=allow_pos,
        # withFlag=True
    )
    keywords = dict(keywords_weight)

    keywords_count = dict()  # 词频以字典形式存储
    for word in words:
        word_s = word.word
        if len(word_s) == 1:
            continue
        elif word_s not in stop_words_list:
            if (word_s in keywords) and word_s.strip():
                keywords_count[word_s] = {'count': keywords_count.get(word_s, {'count': 0})['count'] + 1,
                                          'flag': word.flag,
                                          'weight': keywords.get(word_s, keywords[word_s])}

    # 最低词频过滤
    keywords_count = filter(lambda x: x[1]['count'] >= min_word_count, keywords_count.items())
    # 词频排序
    keywords_count = dict(sorted(keywords_count, key=lambda x: x[1]['count'], reverse=True)[:topk])

    return keywords_count
