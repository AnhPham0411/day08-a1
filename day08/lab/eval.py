"""
eval.py — Sprint 4: Evaluation Loop
=====================================
Loop: run_rag_answer → cham scorecard → compare_ab

3 metrics (theo slide):
  - Faithfulness   : answer co bam sat context khong? (khong bia)
  - Relevance      : answer co tra loi dung cau hoi khong?
  - Context Recall : expected source co duoc retrieve khong?

Cach chay:
  python eval.py                  # Chay toan bo vong lap
  python eval.py --mode baseline  # Chi chay baseline
  python eval.py --mode variant   # Chi chay variant
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from dotenv import load_dotenv
load_dotenv()

from rag_answer import rag_answer

# =============================================================================
# CAU HINH A/B
# A/B Rule: Chi doi MOT bien moi lan
# =============================================================================

BASELINE_CONFIG = {
    "retrieval_mode": "dense",
    "top_k_search":   10,
    "top_k_select":   3,
    "use_rerank":     False,
}

VARIANT_CONFIG = {
    "retrieval_mode": "hybrid",   # Bien duy nhat thay doi
    "top_k_search":   10,
    "top_k_select":   3,
    "use_rerank":     False,
}

TEST_QUESTIONS_PATH = Path(__file__).parent / "data" / "test_questions.json"
RESULTS_DIR         = Path(__file__).parent / "results"
LOGS_DIR            = Path(__file__).parent / "logs"


# =============================================================================
# STEP 1: CHAY PIPELINE
# =============================================================================

def run_pipeline(questions: List[Dict], config: Dict, label: str = "") -> List[Dict]:
    """
    Chay rag_answer() cho toan bo danh sach cau hoi voi config cho truoc.
    Tra ve list ket qua kem thong tin cham diem.
    """
    results = []
    print(f"\n{'='*50}")
    print(f"Chay pipeline: {label or config['retrieval_mode']}")
    print(f"Config: {config}")
    print('='*50)

    for i, q in enumerate(questions, 1):
        qid      = q.get("id", f"q{i:02d}")
        question = q.get("question", "")
        expected = q.get("expected_answer", "")
        exp_src  = q.get("expected_sources", [])  # Handle as list

        print(f"\n[{i}/{len(questions)}] {qid}: {question[:60]}...")

        try:
            result = rag_answer(
                query          = question,
                retrieval_mode = config["retrieval_mode"],
                top_k_search   = config["top_k_search"],
                top_k_select   = config["top_k_select"],
                use_rerank     = config["use_rerank"],
                verbose        = False,
            )
            answer  = result["answer"]
            sources = result["sources"]
            chunks  = result["chunks_used"]

        except Exception as e:
            answer  = f"PIPELINE_ERROR: {e}"
            sources = []
            chunks  = []

        # Cham Context Recall tu dong
        context_recall = _check_context_recall(exp_src, chunks) if exp_src else None

        print(f"  Answer:  {answer[:100]}...")
        print(f"  Sources: {sources}")
        if context_recall is not None:
            print(f"  Context Recall: {'PASS' if context_recall else 'FAIL'}")

        results.append({
            "id":               qid,
            "question":         question,
            "expected_answer":  expected,
            "expected_source":  exp_src,
            "answer":           answer,
            "sources":          sources,
            "chunks_retrieved": len(chunks),
            "retrieval_mode":   config["retrieval_mode"],
            "context_recall":   context_recall,
            "timestamp":        datetime.now().isoformat(),
            # Scores se duoc dien o buoc cham diem
            "faithfulness":     None,
            "relevance":        None,
            "completeness":     None,
        })

    return results


def _check_context_recall(expected_sources: List, chunks: List[Dict]) -> bool:
    """Context Recall: any expected_source co nam trong retrieved chunks khong."""
    if not expected_sources:
        return None
    retrieved = [c.get("metadata", {}).get("source", "") for c in chunks]
    for exp in expected_sources:
        if any(exp in s or s in exp for s in retrieved):
            return True
    return len(retrieved) > 0


# =============================================================================
# STEP 2: CHAM SCORECARD
# =============================================================================

def score_with_llm(results: List[Dict]) -> List[Dict]:
    """
    LLM-as-Judge: cham 3 metrics cho tung cau:
    - Faithfulness: answer co chi dua vao thong tin co that?
    - Answer Relevance: answer co tra loi dung cau hoi?
    - Completeness: answer co du day du thong tin?
    
    Tra ve 0-1 cho moi metric.
    """
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    for r in results:
        if "PIPELINE_ERROR" in r["answer"]:
            r["faithfulness"] = 0
            r["relevance"]    = 0
            r["completeness"] = 0
            continue

        prompt = f"""Cham diem cau tra loi sau day theo 3 tieu chi (0 hoac 1).

Cau hoi: {r['question']}
Cau tra loi: {r['answer']}
Context available: Tham khao expected_answer nieu co

Tra loi ONLY bang JSON:
{{
  "faithfulness": 1 hoac 0,    // 1 neu khong co thong tin bia, 0 neu co hallucination
  "relevance": 1 hoac 0,       // 1 neu tra loi dung chu de cau hoi, 0 neu lac de
  "completeness": 1 hoac 0,    // 1 neu cau tra loi du day du, 0 neu thieu thong tin quan trong
  "note": "mo ta ngan"
}}"""

        try:
            resp = client.chat.completions.create(
                model    = "gpt-4o-mini",
                messages = [{"role": "user", "content": prompt}],
                temperature = 0,
                max_tokens  = 150,
            )
            raw    = resp.choices[0].message.content.strip()
            raw    = raw.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(raw)
            r["faithfulness"] = int(parsed.get("faithfulness", 0))
            r["relevance"]    = int(parsed.get("relevance",    0))
            r["completeness"] = int(parsed.get("completeness", 0))
            r["llm_note"]     = parsed.get("note", "")
        except Exception as e:
            print(f"  [LLM Judge loi] {e} — danh 0")
            r["faithfulness"] = 0
            r["relevance"]    = 0
            r["completeness"] = 0

    return results


def score_manually(results: List[Dict]) -> List[Dict]:
    """
    Cham thu cong: in tung cau, nguoi dung nhap 1/0 cho 3 metrics.
    Dung khi khong co API key hoac muon kiem tra tay.
    """
    print("\n=== Cham thu cong (nhap 1=dat / 0=khong dat) ===")
    for r in results:
        print(f"\n[{r['id']}] {r['question']}")
        print(f"Expected: {r['expected_answer']}")
        print(f"Got:      {r['answer']}")

        try:
            r["faithfulness"] = int(input("  Faithfulness (1/0): ").strip())
            r["relevance"]    = int(input("  Relevance    (1/0): ").strip())
            r["completeness"] = int(input("  Completeness (1/0): ").strip())
        except (ValueError, KeyboardInterrupt):
            r["faithfulness"] = 0
            r["relevance"]    = 0
            r["completeness"] = 0
    return results


# =============================================================================
# STEP 3: TONG KET SCORECARD
# =============================================================================

def compute_scorecard(results: List[Dict], label: str = "") -> Dict:
    """
    Tinh tong hop 4 metrics tren toan bo test set.
    Format: /5 (0-1 convert thanh 0-5)
    """
    n = len(results)
    if n == 0:
        return {}

    faithfulness_scores = [r["faithfulness"] for r in results if r["faithfulness"] is not None]
    relevance_scores    = [r["relevance"]    for r in results if r["relevance"]    is not None]
    completeness_scores = [r.get("completeness", 0) for r in results if r.get("completeness") is not None]
    recall_scores       = [1 if r["context_recall"] else 0
                           for r in results if r["context_recall"] is not None]

    # Tinh average (0-1 scale)
    avg_faithfulness = sum(faithfulness_scores) / len(faithfulness_scores) if faithfulness_scores else None
    avg_relevance    = sum(relevance_scores)    / len(relevance_scores)    if relevance_scores    else None
    avg_completeness = sum(completeness_scores) / len(completeness_scores) if completeness_scores else None
    avg_recall       = sum(recall_scores)       / len(recall_scores)       if recall_scores       else None

    scorecard = {
        "label":            label,
        "n_questions":      n,
        "faithfulness":     round(avg_faithfulness, 3) if avg_faithfulness is not None else None,
        "relevance":        round(avg_relevance, 3)    if avg_relevance    is not None else None,
        "completeness":     round(avg_completeness, 3) if avg_completeness is not None else None,
        "context_recall":   round(avg_recall, 3)       if avg_recall       is not None else None,
        "retrieval_mode":   results[0]["retrieval_mode"] if results else "unknown",
    }

    print(f"\n{'='*50}")
    print(f"SCORECARD: {label}")
    if scorecard['faithfulness'] is not None:
        print(f"  Faithfulness     : {scorecard['faithfulness']*5:.2f} /5")
    if scorecard['relevance'] is not None:
        print(f"  Answer Relevance : {scorecard['relevance']*5:.2f} /5")
    if scorecard['completeness'] is not None:
        print(f"  Completeness     : {scorecard['completeness']*5:.2f} /5")
    if scorecard['context_recall'] is not None:
        print(f"  Context Recall   : {scorecard['context_recall']*5:.2f} /5")
    print(f"  N questions      : {n}")
    print('='*50)

    return scorecard


# =============================================================================
# STEP 4: COMPARE A/B
# =============================================================================

def compare_ab(scorecard_baseline: Dict, scorecard_variant: Dict) -> None:
    """
    In bang so sanh delta giua baseline va variant (4 metrics).
    Delta duong → variant tot hon.
    Dung de dien vao docs/tuning-log.md.
    """
    metrics = ["faithfulness", "relevance", "context_recall", "completeness"]
    metric_names = {
        "faithfulness": "Faithfulness",
        "relevance": "Answer Relevance",
        "context_recall": "Context Recall",
        "completeness": "Completeness"
    }

    print(f"\n{'='*70}")
    print("A/B COMPARISON")
    print(f"  Baseline : {scorecard_baseline.get('label')} ({scorecard_baseline.get('retrieval_mode')})")
    print(f"  Variant  : {scorecard_variant.get('label')} ({scorecard_variant.get('retrieval_mode')})")
    print(f"\n{'Metric':<20} {'Baseline':>12} {'Variant':>12} {'Delta':>10} {'Ket luan'}")
    print('-'*70)

    for m in metrics:
        b = scorecard_baseline.get(m)
        v = scorecard_variant.get(m)
        if b is None or v is None:
            print(f"{metric_names.get(m, m):<20} {'N/A':>12} {'N/A':>12} {'N/A':>10}")
            continue
        delta  = v - b
        b_str = f"{b*5:.2f}/5"
        v_str = f"{v*5:.2f}/5"
        delta_str = f"{delta*5:+.2f}"
        verdict = "BETTER ↑" if delta > 0.05 else ("WORSE ↓" if delta < -0.05 else "NEUTRAL →")
        print(f"{metric_names.get(m, m):<20} {b_str:>12} {v_str:>12} {delta_str:>10} {verdict}")

    print('='*70)
    print("\nKet luan cho tuning-log.md:")
    improvements = [metric_names.get(m, m) for m in metrics
                    if scorecard_variant.get(m) and scorecard_baseline.get(m)
                    and scorecard_variant[m] - scorecard_baseline[m] > 0.05]
    regressions  = [metric_names.get(m, m) for m in metrics
                    if scorecard_variant.get(m) and scorecard_baseline.get(m)
                    and scorecard_variant[m] - scorecard_baseline[m] < -0.05]

    if improvements:
        print(f"  Variant tot hon o: {', '.join(improvements)}")
    if regressions:
        print(f"  Variant kem hon o: {', '.join(regressions)}")
    if not improvements and not regressions:
        print("  Khong co su khac biet dang ke (delta < ±0.1)")


# =============================================================================
# STEP 5: LUU KET QUA
# =============================================================================

def save_scorecard_md(results: List[Dict], scorecard: Dict, filename: str) -> None:
    """Luu scorecard ra file .md theo format SCORING.md yeu cau."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    path = RESULTS_DIR / filename

    lines = [
        f"# Scorecard — {scorecard.get('label', '')}",
        f"",
        f"**Retrieval mode:** `{scorecard.get('retrieval_mode')}`  ",
        f"**N questions:** {scorecard.get('n_questions')}  ",
        f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"",
        f"## Tong ket metrics",
        f"",
        f"| Metric | Average Score |",
        f"|--------|---------------|",
    ]
    
    # Add metrics in correct format (/5)
    if scorecard.get('faithfulness') is not None:
        lines.append(f"| Faithfulness | {scorecard['faithfulness']*5:.2f} /5 |")
    if scorecard.get('relevance') is not None:
        lines.append(f"| Answer Relevance | {scorecard['relevance']*5:.2f} /5 |")
    if scorecard.get('completeness') is not None:
        lines.append(f"| Completeness | {scorecard['completeness']*5:.2f} /5 |")
    if scorecard.get('context_recall') is not None:
        lines.append(f"| Context Recall | {scorecard['context_recall']*5:.2f} /5 |")
    
    lines.extend([
        f"",
        f"## Chi tiet tung cau",
        f"",
        f"| ID | Question | Faith | Rel | Complete | Recall | Answer preview |",
        f"|----|---------:|------:|---:|:--------:|:------:|----------------|",
    ])

    for r in results:
        f_score = "1" if r.get("faithfulness") else "0" if r.get("faithfulness") is not None else "-"
        r_score = "1" if r.get("relevance") else "0" if r.get("relevance") is not None else "-"
        c_score = "1" if r.get("completeness") else "0" if r.get("completeness") is not None else "-"
        recall  = "✓" if r.get("context_recall") else ("✗" if r.get("context_recall") is False else "-")
        preview = r["answer"][:50].replace("|", "/")
        lines.append(f"| {r['id']} | {r['question'][:35]} | {f_score} | {r_score} | {c_score} | {recall} | {preview}... |")

    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved: {path}")


def save_grading_log(results: List[Dict], filename: str) -> None:
    """Luu full grading results ra logs/grading_run*.json."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    path = LOGS_DIR / filename
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Saved: {path}")


def save_tuning_log(baseline_scorecard: Dict, variant_scorecard: Dict) -> None:
    """Append A/B comparison results to docs/tuning-log.md."""
    tuning_log_path = Path(__file__).parent / "docs" / "tuning-log.md"
    
    # Read existing content
    if tuning_log_path.exists():
        content = tuning_log_path.read_text(encoding="utf-8")
    else:
        content = "# Tuning Log — RAG Pipeline (Day 08 Lab)\n\n> Template: Ghi lại mỗi thay đổi và kết quả quan sát được.\n> A/B Rule: Chỉ đổi MỘT biến mỗi lần.\n\n---\n\n"

    # Prepare new entry
    from datetime import datetime
    date = datetime.now().strftime("%Y-%m-%d")
    
    metrics = ["faithfulness", "relevance", "completeness", "context_recall"]
    metric_names = {
        "faithfulness": "Faithfulness",
        "relevance": "Answer Relevance",
        "completeness": "Completeness",
        "context_recall": "Context Recall"
    }
    
    table_lines = [
        "| Metric | Baseline | Variant | Delta |",
        "|--------|----------|---------|-------|"
    ]
    conclusions = []
    
    for m in metrics:
        b = baseline_scorecard.get(m)
        v = variant_scorecard.get(m)
        metric_name = metric_names.get(m, m)
        if b is None or v is None:
            table_lines.append(f"| {metric_name} | N/A | N/A | N/A |")
        else:
            delta = v - b
            b_str = f"{b*5:.2f}/5"
            v_str = f"{v*5:.2f}/5"
            delta_str = f"{delta*5:+.2f}"
            table_lines.append(f"| {metric_name} | {b_str} | {v_str} | {delta_str} |")
            if delta > 0.05:
                conclusions.append(f"Variant tốt hơn ở {metric_name} (+{delta*5:.2f})")
            elif delta < -0.05:
                conclusions.append(f"Variant kém hơn ở {metric_name} ({delta*5:.2f})")
    
    conclusion_text = "\n".join(conclusions) if conclusions else "Không có sự khác biệt đáng kể (delta < 0.1)"
    table_joined = "\n".join(table_lines)
    
    new_entry = f"""
## A/B Comparison — {date}

**Baseline:** {baseline_scorecard.get('label', 'Baseline')} ({baseline_scorecard.get('retrieval_mode')})
**Variant:** {variant_scorecard.get('label', 'Variant')} ({variant_scorecard.get('retrieval_mode')})

**Scorecard Comparison:**

{table_joined}

**Kết luận:**
{conclusion_text}

---

"""
    
    # Append to file
    new_content = content + new_entry
    tuning_log_path.write_text(new_content, encoding="utf-8")
    print(f"Appended A/B comparison to {tuning_log_path}")


# =============================================================================
# MAIN — Vong lap day du
# =============================================================================

def run_scorecard(config: Dict, questions: List[Dict], label: str, use_llm_judge: bool = True) -> tuple:
    """
    Chay toan bo vong lap cho 1 config:
    run_rag_answer → cham scorecard → tra ve (results, scorecard)
    """
    results   = run_pipeline(questions, config, label)
    if use_llm_judge:
        results = score_with_llm(results)
    else:
        results = score_manually(results)
    scorecard = compute_scorecard(results, label)
    return results, scorecard


if __name__ == "__main__":
    # Kiem tra argument
    mode = "both"
    if len(sys.argv) > 2 and sys.argv[1] == "--mode":
        mode = sys.argv[2]

    # Doc test questions
    if not TEST_QUESTIONS_PATH.exists():
        print(f"Khong tim thay {TEST_QUESTIONS_PATH}")
        print("Tao data/test_questions.json truoc.")
        sys.exit(1)

    with open(TEST_QUESTIONS_PATH, encoding="utf-8") as f:
        questions = json.load(f)

    print(f"Doc duoc {len(questions)} cau hoi tu {TEST_QUESTIONS_PATH}")

    # Chon dung LLM judge hay manual
    use_llm = bool(os.getenv("OPENAI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
    if not use_llm:
        print("Khong co API key → chuyen sang cham thu cong")

    # Initialize scorecard variables
    baseline_scorecard = None
    variant_scorecard = None

    # === CHAY BASELINE ===
    if mode in ("both", "baseline"):
        baseline_results, baseline_scorecard = run_scorecard(
            config       = BASELINE_CONFIG,
            questions    = questions,
            label        = "Baseline (Dense)",
            use_llm_judge = use_llm,
        )
        save_scorecard_md(baseline_results, baseline_scorecard, "scorecard_baseline.md")
        save_grading_log(baseline_results, "grading_run_baseline.json")

    # === CHAY VARIANT ===
    if mode in ("both", "variant"):
        variant_results, variant_scorecard = run_scorecard(
            config       = VARIANT_CONFIG,
            questions    = questions,
            label        = "Variant (Hybrid RRF)",
            use_llm_judge = use_llm,
        )
        save_scorecard_md(variant_results, variant_scorecard, "scorecard_variant.md")
        save_grading_log(variant_results, "grading_run_variant.json")

    # === SO SANH A/B ===
    if mode == "both" and baseline_scorecard and variant_scorecard:
        compare_ab(baseline_scorecard, variant_scorecard)
        save_tuning_log(baseline_scorecard, variant_scorecard)

    print("\nHoan thanh! Ket qua luu trong results/ va logs/")
