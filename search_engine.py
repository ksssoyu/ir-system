import json
import math
from collections import defaultdict
from text_utils import preprocess_text
import re

# --------------------------
# Boolean 연산 함수들
# --------------------------
def boolean_and(set1, set2):
    return set1 & set2

def boolean_or(set1, set2):
    return set1 | set2

def boolean_not(target_set, total_set):
    return total_set - target_set

# --------------------------
# Boolean Query 파싱 (괄호, NOT, AND, OR 지원)
# --------------------------
def process_boolean_query(query, index, total_doc_ids):
    total_docs = set(total_doc_ids)

    print("\n📥 Raw Query Input:", query)

    # 1. 단어 추출 + 전처리
    raw_words = re.findall(r'\b\w+\b', query)
    processed_words = preprocess_text(' '.join(raw_words))
    print("🔍 Raw words found:", raw_words)
    print("🧹 Processed tokens:", processed_words)

    # 2. 쿼리 구조 파싱 (괄호 + 연산자 포함)
    tokens = re.findall(r'\w+|AND|OR|NOT|\(|\)', query)
    logical_ops = {"AND", "OR", "NOT"}
    normalized = []

    word_idx = 0
    for token in tokens:
        upper_token = token.upper()
        if upper_token in logical_ops or token in {"(", ")"}:
            normalized.append(upper_token)
        else:
            if word_idx < len(processed_words):
                normalized.append(processed_words[word_idx])
                word_idx += 1
            else:
                normalized.append("__NULL__")

    print("🧱 Normalized tokens (structure preserved):", normalized)

    # 3. Shunting Yard: 중위 → 후위 표기법 변환
    precedence = {"NOT": 3, "AND": 2, "OR": 1}
    output = []
    stack = []
    for token in normalized:
        if token in precedence:
            while stack and stack[-1] != "(" and precedence.get(stack[-1], 0) >= precedence[token]:
                output.append(stack.pop())
            stack.append(token)
        elif token == "(":
            stack.append(token)
        elif token == ")":
            while stack and stack[-1] != "(":
                output.append(stack.pop())
            if stack:
                stack.pop()
        else:
            output.append(token)
    while stack:
        output.append(stack.pop())

    print("📤 Postfix expression:", output)

    # 4. 후위 표기법 계산
    eval_stack = []
    for token in output:
        if token == "AND":
            right = eval_stack.pop()
            left = eval_stack.pop()
            result = left & right
            print(f"🔧 AND operation: {len(left)} ∩ {len(right)} → {len(result)}")
            eval_stack.append(result)
        elif token == "OR":
            right = eval_stack.pop()
            left = eval_stack.pop()
            result = left | right
            print(f"🔧 OR operation: {len(left)} ∪ {len(right)} → {len(result)}")
            eval_stack.append(result)
        elif token == "NOT":
            operand = eval_stack.pop()
            result = total_docs - operand
            print(f"🔧 NOT operation: {len(total_docs)} - {len(operand)} → {len(result)}")
            eval_stack.append(result)
        else:
            if token == "__NULL__":
                print(f"⚠️ Token '{token}' not found → empty set")
                eval_stack.append(set())
            else:
                docs = set(map(int, index.get(token, {}).get("postings", {}).keys()))
                print(f"📄 Token '{token}' found in {len(docs)} documents")
                eval_stack.append(docs)

    final_result = sorted(eval_stack[0]) if eval_stack else []
    print(f"\n✅ Final matched documents: {len(final_result)}\n")
    return final_result


# --------------------------
# Vector Space 유사도 계산
# --------------------------
def compute_cosine_similarity(query_tokens, index, N):
    tf_query = defaultdict(int)
    for token in query_tokens:
        tf_query[token] += 1

    print(f"\n🔎 Query Tokens: {query_tokens}")

    # IDF 계산
    idf = {}
    for token in tf_query:
        df = index.get(token, {}).get("df", 0)
        idf[token] = math.log2(N / df) if df > 0 else 0
        print(f"📊 Token '{token}': TF={tf_query[token]}, DF={df}, IDF={idf[token]:.4f}")

    # 쿼리 벡터 가중치 계산
    query_weights = {
        token: tf_query[token] * idf[token]
        for token in tf_query
    }
    print(f"\n🧮 Query TF-IDF Weights: {query_weights}")

    scores = defaultdict(float)
    term_contributions = defaultdict(list)

    # 문서별 점수 누적
    for token, q_weight in query_weights.items():
        postings = index.get(token, {}).get("postings", {})
        for doc_id_str, tf in postings.items():
            doc_id = int(doc_id_str)
            tfidf = tf * idf[token]
            scores[doc_id] += q_weight * tfidf
            term_contributions[doc_id].append((token, tf, idf[token]))

    # 벡터 정규화
    query_norm = math.sqrt(sum(w ** 2 for w in query_weights.values()))
    ranked_results = []

    for doc_id, score in scores.items():
        doc_weight_sum = 0
        for token, entry in index.items():
            tf = entry.get("postings", {}).get(str(doc_id), 0)
            if tf == 0:
                continue
            df = entry["df"]
            idf_val = math.log2(N / df) if df > 0 else 0
            tfidf = tf * idf_val
            doc_weight_sum += tfidf ** 2
        doc_norm = math.sqrt(doc_weight_sum)

        if doc_norm > 0 and query_norm > 0:
            cosine_sim = score / (query_norm * doc_norm)
            ranked_results.append((doc_id, cosine_sim, term_contributions[doc_id]))

    ranked_results.sort(key=lambda x: x[1], reverse=True)
    print(f"\n✅ Total Matched Documents: {len(ranked_results)}")
    return ranked_results


# --------------------------
# 검색기 실행 함수
# --------------------------
def run_search_engine():
    with open("index/dictionary.json", "r", encoding="utf-8") as f:
        index = json.load(f)
    with open("index/doc_id_map.json", "r", encoding="utf-8") as f:
        doc_id_map = json.load(f)

    total_doc_ids = list(map(int, doc_id_map.keys()))
    N = len(total_doc_ids)

    print("\n검색기 실행: Boolean 또는 Vector Space Model 선택 가능")
    print("종료하려면 'q' 입력")

    while True:
        mode = input("\n검색 모드를 선택하세요 (boolean / vector): ").strip().lower()
        if mode == "q":
            print("✅ 종료합니다.")
            break
        if mode not in ("boolean", "vector"):
            print("❌ 'boolean' 또는 'vector'만 입력 가능")
            continue

        query = input("\n검색어를 입력하세요:\n> ").strip()
        if query == "q":
            print("✅ 종료합니다.")
            break

        if mode == "boolean":
            result_ids = process_boolean_query(query, index, total_doc_ids)
            if result_ids:
                print("\n검색 결과 문서:")
                for doc_id in result_ids:
                    print(f"- {doc_id_map[str(doc_id)]}")
            else:
                print("❌ 일치하는 문서가 없습니다.")

        elif mode == "vector":
            tokens = preprocess_text(query)
            results = compute_cosine_similarity(tokens, index, N)
            if results:
                print("\n유사도 기반 랭킹 결과 (상위 10개):")
                for rank, (doc_id, score, contribs) in enumerate(results[:10], start=1):
                    print(f"\n{rank}. {doc_id_map[str(doc_id)]} (유사도: {score:.4f})")
                    print(f"   ➤ 해당 문서에서의 단어 등장:")
                    for token, tf, _ in contribs:
                        print(f"     - '{token}': {tf}회")
            else:
                print("❌ 관련 문서가 없습니다.")


# --------------------------
# 실행
# --------------------------
if __name__ == "__main__":
    run_search_engine()