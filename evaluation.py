import os
from query import process_boolean_query
from text_utils import load_index_and_docmap
import json

# --------------------------
# Precision, Recall, F-beta 계산 함수
# --------------------------
def evaluate_precision_recall(query, index, total_doc_ids, doc_id_map, ground_truth_filenames, beta=1):
    # 문서 이름 → doc_id 변환
    filename_to_id = {v: int(k) for k, v in doc_id_map.items()}
    ground_truth_ids = set(
        filename_to_id[name] for name in ground_truth_filenames if name in filename_to_id
    )

    result_ids = process_boolean_query(query, index, total_doc_ids)
    result_set = set(result_ids)
    true_positives = result_set & ground_truth_ids

    precision = len(true_positives) / len(result_set) if result_set else 0
    recall = len(true_positives) / len(ground_truth_ids) if ground_truth_ids else 0

    if precision + recall > 0:
        f_beta = (1 + beta**2) * (precision * recall) / ((beta**2 * precision) + recall)
    else:
        f_beta = 0.0

    print(f"\n📌 Query: {query}")
    print(f"✔️ Retrieved: {len(result_set)} docs")
    print(f"✔️ Relevant (Ground Truth): {len(ground_truth_ids)} docs")
    print(f"✔️ True Positives: {len(true_positives)}")
    print(f"🎯 Precision: {precision:.4f}")
    print(f"🎯 Recall:    {recall:.4f}")
    print(f"⭐ F{beta}-score:  {f_beta:.4f}")

    print("📄 Matched Docs:")
    for doc_id in sorted(true_positives):
        print(f"- {doc_id_map[str(doc_id)]}")

    return precision, recall, f_beta


# --------------------------
# 평가 실행 함수
# --------------------------
def evaluate():
    index, doc_id_map = load_index_and_docmap()
    total_doc_ids = list(map(int, doc_id_map.keys()))

    # ground_truth 폴더에 있는 파일 목록 확인
    ground_dir = "ground_truth"
    available_queries = [f for f in os.listdir(ground_dir) if f.endswith(".txt")]

    while True:
        print("\n평가 실행: Boolean Model")
        print("종료하려면 'q' 입력")
        print("\n📂 Ground Truth 파일 목록:")
        for i, file in enumerate(available_queries, 1):
            print(f"{i}. {file}")

        selected = input("\n평가할 Ground Truth 파일 번호를 선택하세요: ").strip()
        if selected == "q":
            print("✅ 종료합니다.")
            break
        if not selected.isdigit() or int(selected) < 1 or int(selected) > len(available_queries):
            print("❌ 유효하지 않은 선택입니다.")
            return

        filename = available_queries[int(selected) - 1]
        filepath = os.path.join(ground_dir, filename)

        with open(filepath, "r", encoding="utf-8") as f:
            gt_filenames = json.load(f)

        query_text = filename.replace(".txt", "").replace("_", " ").replace(" and ", " AND ").replace(" or ", " OR ").replace(" not ", " NOT ")

        # 평가 실행
        evaluate_precision_recall(query_text, index, total_doc_ids, doc_id_map, gt_filenames, beta=0.5)


# --------------------------
# 실행
# --------------------------
if __name__ == "__main__":
    evaluate()
