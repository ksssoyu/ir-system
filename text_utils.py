from nltk import pos_tag
from nltk.corpus import stopwords, words, wordnet
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer
import json


# === nltk 리소스 다운로드 (최초 1회만 실행하면 됨) ===
import nltk
nltk.download('punkt')                           # 토크나이저용 데이터
nltk.download('stopwords')                       # 영어 불용어 리스트
nltk.download('words')                           # 영어 단어 사전
nltk.download('wordnet')                         # 표제어 추출용 WordNet 사전
nltk.download('omw-1.4')                         # WordNet 보조 언어 자원
nltk.download('averaged_perceptron_tagger_eng')  # POS 태깅을 위한 모델 (pos_tag 함수에서 사용됨)

# === 전역 리소스 초기화 (한 번만 설정하면 모든 문서에 재사용 가능) ===
stop_words = set(stopwords.words('english')) | {
    'would', 'could', 'should', 'might', 'must', 'may', 'also', 'shall'
}  # 기본 불용어 + 조동사 등 커스텀 단어 추가

tokenizer = RegexpTokenizer(r'\w+')            # 단어 토크나이저 (특수문자 제거)
english_vocab = set(words.words())             # 유효한 영어 단어 집합
lemmatizer = WordNetLemmatizer()               # 표제어 추출 도구

# ------------------------------------------------------------
# 품사(POS) 태그를 WordNet용으로 변환
# ------------------------------------------------------------
def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN

# ------------------------------------------------------------
# 텍스트(문서, 쿼리) 전처리 함수 (POS 기반 lemmatization 포함)
# ------------------------------------------------------------
def preprocess_text(text):
    """
    문자열 또는 section dict를 받아 전처리된 토큰 리스트를 반환
    (lowercasing, tokenizing, stopword 제거, POS 기반 lemmatization 포함)
    """
    # dict라면 값들을 결합
    if isinstance(text, dict):
        combined_text = ' '.join(v for v in text.values() if v)
    else:
        combined_text = text

    # 소문자화 + 토큰화
    tokens = tokenizer.tokenize(combined_text.lower())

    # 불용어 및 알파벳 필터링
    filtered_tokens = [t for t in tokens if t not in stop_words and t.isalpha()]

    # 품사 태깅 + 표제어 추출
    tagged_tokens = pos_tag(filtered_tokens)
    lemmatized_tokens = [
        lemmatizer.lemmatize(token, get_wordnet_pos(pos))
        for token, pos in tagged_tokens
    ]

    # 실제 영어 단어만 필터링
    return [t for t in lemmatized_tokens if t in english_vocab]


# ------------------------------------------------------------
# dictionary.json, doc_id_map.json 파일 로드
# ------------------------------------------------------------
def load_index_and_docmap(dict_path="index/dictionary.json", doc_map_path="index/doc_id_map.json"):
    with open(dict_path, "r", encoding="utf-8") as f:
        index = json.load(f)
    with open(doc_map_path, "r", encoding="utf-8") as f:
        doc_id_map = json.load(f)
    return index, doc_id_map
