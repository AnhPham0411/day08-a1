# Tuning Log — RAG Pipeline (Day 08 Lab)

> Template: Ghi lại mỗi thay đổi và kết quả quan sát được.
> A/B Rule: Chỉ đổi MỘT biến mỗi lần.

---

## Baseline (Sprint 2)

**Ngày:** 2024-04-13  
**Config:**
```
retrieval_mode = "dense"
chunk_size = 512 tokens
overlap = 50 tokens
top_k_search = 10
top_k_select = 3
use_rerank = False
llm_model = qwen/qwen3-next-80b-a3b-instruct:free
```

**Scorecard Baseline:**
| Metric           | Average Score |
| ---------------- | ------------- |
| Faithfulness     | 0.8 /1        |
| Answer Relevance | 0.7 /1        |
| Context Recall   | 0.6 /1        |
| Completeness     | 0.75 /1       |

**Câu hỏi yếu nhất (điểm thấp):**
- q07 (Approval Matrix) - context recall = 0 vì dense bỏ lỡ alias "Approval Matrix" → "Access Control SOP".
- q09 (ERR-403-AUTH) - faithfulness = 0 vì hallucination khi không có context.

**Giả thuyết nguyên nhân (Error Tree):**
- [x] Retrieval: Dense bỏ lỡ exact keyword / alias
- [ ] Indexing: Chunking cắt giữa điều khoản
- [ ] Indexing: Metadata thiếu effective_date
- [ ] Retrieval: Top-k quá ít → thiếu evidence
- [ ] Generation: Prompt không đủ grounding
- [ ] Generation: Context quá dài → lost in the middle

---

## Variant 1 (Sprint 3)

**Ngày:** 2024-04-13  
**Biến thay đổi:** retrieval_mode = "hybrid" (dense + BM25 RRF)  
**Lý do chọn biến này:**
Chọn hybrid vì q07 (alias query) và q09 (mã lỗi ERR-403) đều thất bại với dense. Corpus có cả ngôn ngữ tự nhiên (policy) lẫn tên riêng/mã lỗi (ticket code, SLA label).

**Config thay đổi:**
```
retrieval_mode = "hybrid"   # biến duy nhất thay đổi
# Các tham số còn lại giữ nguyên như baseline
```

**Scorecard Variant 1:**
| Metric           | Baseline | Variant 1 | Delta  |
| ---------------- | -------- | --------- | ------ |
| Faithfulness     | 80.0%    | 85.0%     | +5.0%  |
| Answer Relevance | 70.0%    | 75.0%     | +5.0%  |
| Context Recall   | 60.0%    | 80.0%     | +20.0% |

**Nhận xét:**
Variant 1 cải thiện đáng kể ở context recall (+20%), đặc biệt cho q07 (Approval Matrix alias). Faithfulness và relevance cũng tăng nhẹ do context tốt hơn.

**Kết luận:**
Variant 1 tốt hơn baseline, đặc biệt ở retrieval. Bằng chứng: context recall tăng 20%, cải thiện cho alias queries.

---

## A/B Comparison — 2024-04-13

**Baseline:** Baseline (Dense) (dense)
**Variant:** Variant (Hybrid RRF) (hybrid)

**Scorecard Comparison:**

| Metric         | Baseline | Variant | Delta  |
| -------------- | -------- | ------- | ------ |
| faithfulness   | 80.0%    | 85.0%   | +5.0%  |
| relevance      | 70.0%    | 75.0%   | +5.0%  |
| context_recall | 60.0%    | 80.0%   | +20.0% |

**Kết luận:**
Variant tốt hơn ở faithfulness (+5.0%)
Variant tốt hơn ở relevance (+5.0%)
Variant tốt hơn ở context_recall (+20.0%)

---

## Tóm tắt học được

1. **Lỗi phổ biến nhất trong pipeline này là gì?**
   Retrieval với dense embedding bỏ lỡ exact matches và aliases, dẫn đến context recall thấp.

2. **Biến nào có tác động lớn nhất tới chất lượng?**
   > _____________

3. **Nếu có thêm 1 giờ, nhóm sẽ thử gì tiếp theo?**
   > _____________
