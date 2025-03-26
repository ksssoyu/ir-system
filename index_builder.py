import os
import json
from collections import defaultdict
import matplotlib.pyplot as plt
from text_utils import preprocess_text

# ------------------------------------------------------------
# 텍스트 파일(.txt)을 읽고, title, summary, story로 구분해서 반환
# ------------------------------------------------------------
def load_txt_document(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    sections = {'title': '', 'summary': '', 'story': ''}
    current_section = None

    for line in lines:
        line = line.strip()
        if line.startswith('Title:'):
            current_section = 'title'
            sections[current_section] = line[len('Title:'):].strip()
        elif line.startswith('Summary:'):
            current_section = 'summary'
        elif line.startswith('Story Text:'):
            current_section = 'story'
        elif line.startswith('Book Info:'):
            break
        elif current_section:
            sections[current_section] += line + ' '

    for key in sections:
        if sections[key]:
            sections[key] = sections[key].strip()

    if sections['summary'] and sections['summary'].lower() == 'none':
        sections['summary'] = None

    return sections

# ------------------------------------------------------------
# 전체 문서에서 (token, docID) 수집 및 docID ↔ 파일명 매핑
# ------------------------------------------------------------
def collect_token_doc_pairs_with_ids(folder_path):
    token_doc_pairs = []
    doc_id_map = {}

    for doc_id, fname in enumerate(sorted(f for f in os.listdir(folder_path) if f.endswith('.txt')), start=1):
        full_path = os.path.join(folder_path, fname)
        data = load_txt_document(full_path)
        tokens = preprocess_text(data)

        doc_id_map[doc_id] = fname
        token_doc_pairs.extend((token, doc_id) for token in tokens)

    return token_doc_pairs, doc_id_map

# ------------------------------------------------------------
# (token, docID) 쌍 정렬
# ------------------------------------------------------------
def sort_token_doc_pairs(pairs):
    return sorted(pairs, key=lambda x: (x[0], x[1]))

# ------------------------------------------------------------
# 인덱스 구축: token → 문서 목록 + 빈도수
# ------------------------------------------------------------
def build_index(sorted_pairs):
    postings = defaultdict(lambda: defaultdict(int))

    for token, doc_id in sorted_pairs:
        postings[token][doc_id] += 1

    dictionary = {}
    for token, posting in postings.items():
        df = len(posting)
        doc_postings = {str(doc_id): tf for doc_id, tf in posting.items()}
        dictionary[token] = {
            "df": df,
            "postings": doc_postings
        }

    return dictionary

# ------------------------------------------------------------
# 인덱싱 전체 파이프라인
# ------------------------------------------------------------
def run_indexing(folder_path):
    token_doc_pairs, doc_id_map = collect_token_doc_pairs_with_ids(folder_path)
    print(f"✅ 총 {len(doc_id_map)}개의 문서를 처리했습니다.")
    print(f"✅ 총 {len(token_doc_pairs):,}개의 (token, docID) 쌍을 수집했습니다.")

    sorted_pairs = sort_token_doc_pairs(token_doc_pairs)
    index = build_index(sorted_pairs)
    print(f"✅ 고유 토큰 수: {len(index):,}")
    return index, doc_id_map

# ------------------------------------------------------------
# 인덱스 및 매핑 저장
# ------------------------------------------------------------
def save_index_to_files(index, doc_id_map, output_dir="./index"):
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "dictionary.json"), "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)
    with open(os.path.join(output_dir, "doc_id_map.json"), "w", encoding="utf-8") as f:
        json.dump(doc_id_map, f, indent=2)

# ------------------------------------------------------------
# 단어 빈도 시각화 (상위 N개만 표시)
# ------------------------------------------------------------
def visualize_top_words(index, top_n=30):
    total_frequencies = {
        token: sum(info['postings'].values())
        for token, info in index.items()
    }
    sorted_tokens = sorted(total_frequencies.items(), key=lambda x: x[1], reverse=True)[:top_n]

    words = [w for w, _ in sorted_tokens]
    freqs = [f for _, f in sorted_tokens]

    plt.figure(figsize=(12, 6))
    plt.bar(words, freqs)
    plt.xlabel("Word")
    plt.ylabel("Total Frequency")
    plt.title(f"Top {top_n} English Words by Frequency")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    print(f"✅ 시각화 완료 (상위 {top_n}개 토큰 표시됨)")

# ------------------------------------------------------------
# 메인 실행
# ------------------------------------------------------------
if __name__ == "__main__":
    folder_path = "./data"
    index, doc_id_map = run_indexing(folder_path)
    save_index_to_files(index, doc_id_map)
    print("✅ 인덱스 저장 완료!")

    visualize_top_words(index, top_n=30)