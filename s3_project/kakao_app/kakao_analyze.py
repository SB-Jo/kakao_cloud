import re
from eunjeon import Mecab
from wordcloud import WordCloud
from collections import Counter
import matplotlib.pyplot as plt
import os

def read_file(file):
    f = open(file, 'r', encoding='UTF8')
    lines = f.readlines()
    f.close()

    p = re.compile(r'(\d+[:]\d+)')
    time = 0
    talk_dic = {}
    for line in lines:
        m = p.search(line)
        if line.startswith('---------------'):
            time = line[16:line.find('---------------', 1)]
        elif m is not None and line.find('[') == 0:
            talker = line[1:line.find(']')]
            talk = line[m.end() + 1:].strip()
            hour = line[line.find('[', line.find('[')+1)+1 : line.find(']', line.find(']')+1)]
            if talker not in talk_dic:
                talk_dic[talker] = [(time+hour, talk)]
            else:
                talk_dic[talker].append((time+hour, talk))
    return talk_dic

def message_cleaning(docs):
    '''
    1. Photo, Emoticon은 내용 알 수 없으므로 제거
    2. 자음/모음 표현 처리
    3. http://로 시작하는 하이퍼링크 제거
    4. 특수문자 제거
    '''

    pattern1 = re.compile("이모티콘")
    docs = pattern1.sub("", docs)    
    
    pattern2 = re.compile("[ㄱ-ㅎ]*|[ㅏ-ㅢ]*")
    docs = pattern2.sub("", docs) 
    
    pattern3 = re.compile(r"\b(https?:\/\/)?([\w.]+){1,2}(\.[\w]{2,4}){1,2}(.*)")
    docs = pattern3.sub("", docs) 
    
    pattern4 = re.compile("[\{\}\[\]\/?.,;:|\)*-`!^\-_+<>@\#$&\\\=\(\'\"]")
    docs = pattern4.sub("", docs) 
    
    return docs

def define_stopwords(path):
    SW = set()
    # 불용어 추가 방법 Sw.add("있다") or stopwords-ko.txt에 직접 추가
    with open(path, encoding='utf-8') as f:
        for word in f:
            SW.add(word)
    words = ['이랑', '웅웅', '아서', '시반', '~~~', '~~~~']
    for word in words:
        SW.add(word)
    return SW

def tokenize(talk_dic):
    SW = define_stopwords("./stopwords-ko.txt")
    mecab= Mecab()
    total = {}
    for k, v in talk_dic.items():
        total_sub = []
        for idx, talk_set in enumerate(v):
            time, talk = talk_set
            clean_talk = message_cleaning(talk)
            tokenized_talk = [word for word in mecab.morphs(clean_talk) if word not in SW and len(word) > 1]
            talk_dic[k][idx] = (time, talk, tokenized_talk)
            total_sub.extend(tokenized_talk)
        total[k] = total_sub
    return total


def get_count(total):
    word_counts = []
    for k, v in total.items():
        count = Counter(v)
        wc = count.most_common(50)
        word_counts.append(wc)
        if not os.path.isfile(f'./kakao_app/static/wordcloud_{k}.png'):
            wordcloud = WordCloud(font_path = './kakao_app/static/malgun.ttf',
                            relative_scaling=0.2,
                            background_color = 'white',
                            ).generate_from_frequencies(dict(wc))
            fig = plt.figure(figsize=(16,8))
            plt.imshow(wordcloud)
            plt.axis("off")
            plt.close()
            fig.savefig(f'./kakao_app/static/wordcloud_{k}.png')
            # plt.figure(figsize=(16,8))
            # plt.imsave(f'./static/wordcloud_{k}.png', wordcloud)
            #fig.savefig(f'./static/wordcloud_{k}.png', dpi=300)
    return word_counts