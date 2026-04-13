# Báo Cáo Nhóm — Lab Day 08: Full RAG Pipeline

**Tên nhóm:** ___________  
**Thành viên:**
| Tên | Vai trò | Email |
|-----|---------|-------|
| ___ | Tech Lead | ___ |
| ___ | Retrieval Owner | ___ |
| ___ | Eval Owner | ___ |
| Đàm Lê Văn Toàn | Documentation Owner | damtoan321@gmail.com|

**Ngày nộp:** 2026-04-13  
**Repo:** https://github.com/AnhPham0411/day08-a1-c401 

**Độ dài khuyến nghị:** 600–900 từ

---

> **Hướng dẫn nộp group report:**
>
> - File này nộp tại: `reports/group_report.md`
> - Deadline: Được phép commit **sau 18:00** (xem SCORING.md)
> - Tập trung vào **quyết định kỹ thuật cấp nhóm** — không trùng lặp với individual reports
> - Phải có **bằng chứng từ code, scorecard, hoặc tuning log** — không mô tả chung chung

---

## 1. Pipeline nhóm đã xây dựng (150–200 từ)

> Mô tả ngắn gọn pipeline của nhóm:
> - Chunking strategy: size, overlap, phương pháp tách (by paragraph, by section, v.v.)
> - Embedding model đã dùng
> - Retrieval mode: dense / hybrid / rerank (Sprint 3 variant)

**Chunking decision:**
Nhóm dùng chunk_size=400 tokens (~1600 ký tự) và overlap=80 tokens, thực hiện tách theo section headers (Heading-based) cho những phần có cấu trúc rõ ràng, rồi mới tiếp tục tách nhỏ qua paragraph. Điều này giúp tránh bị ngắt đoạn câu khiến cho thiếu hụt ngữ cảnh nhưng duy trì được độ dài chunk tối ưu.

**Embedding model:**
OpenAI `text-embedding-3-small`.

**Retrieval variant (Sprint 3):**
Nhóm chọn sử dụng kết hợp Hybrid Retrieval với thuật toán Reciprocal Rank Fusion (RRF). Việc dùng hybrid giúp kết hợp ưu điểm của dense embedding (bắt nghĩa) và sparse BM25 (bắt từ khoá chính xác). Do giới hạn về tokenizer tiếng Việt gán whitespace trong BM25 tạo nhiễu cực mạnh, nhóm đã quyết định điều chỉnh bù trừ trọng số RRF về `dense_weight=0.8` và `sparse_weight=0.2`.

---

## 2. Quyết định kỹ thuật quan trọng nhất (200–250 từ)

> Chọn **1 quyết định thiết kế** mà nhóm thảo luận và đánh đổi nhiều nhất trong lab.
> Phải có: (a) vấn đề gặp phải, (b) các phương án cân nhắc, (c) lý do chọn.

**Quyết định:** Chuyển đổi chiến lược Retrieval từ Dense thuần tuý sang mô hình Hybrid có hiệu chỉnh trọng số phân tử RRF (`dense_weight=0.8`, `sparse_weight=0.2`).

**Bối cảnh vấn đề:**
BM25 tokenizer mặc định tách dãy từ theo khoảng trắng thông thường (whitespace), khiến các từ vựng tiếng Việt bị tách ra rời rạc. Những từ không chứa ngữ nghĩa chính quan trọng như "xu", "ly", "la" trong một câu query bị nhận dạng tương đồng xuất hiện ở hầu hết tất cả chunk, đẩy điểm sparse BM25 sai lầm lên khiến chunk chứa nhiễu được đưa lên vị trí rất cao làm lạc điểm Retrieval.

**Các phương án đã cân nhắc:**

| Phương án | Ưu điểm | Nhược điểm |
|-----------|---------|-----------|
| Dùng Dense Retrieval Thuần | Tránh tuyệt đối được nhiễu do tách từ ngữ sai từ thư viện | Dễ tuột các câu query chứa mã code hoặc danh từ riêng biệt |
| Thêm underthesea tokenizer vào pipeline BM25 | Xử lý gốc rễ nguyên nhân và chia morpheme tiếng Việt chuẩn | Tốn bộ nhớ RAM, thời gian chạy quá lâu cho pipeline |
| Dùng Hybrid RRF với `dense_weight` ở mức áp đảo | Cân bằng lợi ích của việc giữ mapping keyword BM25 nhưng điểm dense giữ vai trò chính | Phải tuning và tinh chỉnh weight tốn nhiều session |

**Phương án đã chọn và lý do:**
Nhóm đặt cấu hình Hybrid RRF hạ trọng số `sparse_weight` về mức nhỏ `0.2` và nâng `dense_weight` lên `0.8`. Biện pháp này mang lại một sự cải tiết tiết kiệm đáng kể về tài nguyên hệ thống, giúp xoá ảnh hưởng tiêu cực của thư viện phân tích tiếng Việt yếu kém nhưng vẫn đạt được recall cực kỳ tốt nếu prompt hỏi một từ khoá hiếm. 

**Bằng chứng từ scorecard/tuning-log:**
Quan sát rõ rệt từ file `docs/tuning-log.md` sau khi chạy debug, cho thấy chunk dính lỗi (như đoạn `Phần 5: Lịch sử phiên bản`) thường xuyên sai chiếm vị trí 1 do nhiễu, nhưng sau khi cập nhật tỷ lệ `dense_weight` nó đã bị giảm xuống và kết quả phù hợp nhất `Phần 2: SLA theo mức độ ưu tiên` đã chiếm được rank 1 hoàn hảo.

---

## 3. Kết quả grading questions (100–150 từ)

> Sau khi chạy pipeline với grading_questions.json (public lúc 17:00):
> - Câu nào pipeline xử lý tốt nhất? Tại sao?
> - Câu nào pipeline fail? Root cause ở đâu (indexing / retrieval / generation)?
> - Câu gq07 (abstain) — pipeline xử lý thế nào?

**Ước tính điểm raw:** Dao động mức ~90/98 (Dựa vào metrics trung bình sau biến thể variant).

**Câu tốt nhất:** ID: gq05 — Lý do: Đây là câu hỏi pipeline variant phát huy hoàn hảo tác dụng. Cấu hình ban đầu của Dense gặp sự cố thiếu context gây cản trở và đã bỏ qua trả lời (Abstain). Việc bổ sung thuật toán Hybrid ưu việt giúp lấy đủ Chunk chứa điều kiện cấp Admin cho Contractor gán vào top và trả lời đầy đủ 100%.

**Câu fail:** ID: gq07 — Root cause: "Công ty sẽ phạt bao nhiêu nếu team IT vi phạm cam kết SLA P1?". Fail do hệ thống "từ chối trả lời" (Abstain). Thực tế, RAG làm đúng chức trách nhạy bén vì Context không hề có thông tin giải quyết phạt tài chính. Vấn đề có thể nằm ở Generation (Không hướng dẫn user tại sao hoặc prompt chưa đủ độ bám sát giải thích cụ thể cho trường hợp Missing Data).

**Câu gq07 (abstain):** Hệ thống trả về: "Tôi không có đủ dữ liệu trong tài liệu nội bộ để trả lời câu hỏi này." Hành vi này phản ánh rất chuẩn và hạn chế triệt để triệu chứng Hallucination của LLM.

---

## 4. A/B Comparison — Baseline vs Variant (150–200 từ)

> Dựa vào `docs/tuning-log.md`. Tóm tắt kết quả A/B thực tế của nhóm.

**Biến đã thay đổi (chỉ 1 biến):** Tham số `dense_weight` và `sparse_weight` trong chế độ RRF Retrieval.

| Metric | Baseline | Variant | Delta |
|--------|---------|---------|-------|
| Faithfulness | 0.80 | 0.90 | +0.10 |
| Answer Relevance | 0.80 | 0.90 | +0.10 |
| Context Recall | 5.00 | 5.00 | +0.00 |

**Kết luận:**
Variant thể hiện biểu đồ tăng trưởng tốt hơn ở Faithfulness và Answer Relevance (10% cải thiện). Điểm Recall đã rất ổn tại baseline (5.0), nhưng thiết lập Hybrid Variant bù lại khiếm khuyết keyword matching của Dense. Điển hình, ở câu `gq05` mô hình thay vì lúng túng abstain đã truy cập được thông tin Contractor và đưa chuỗi văn bản chính xác nhất.

---

## 5. Phân công và đánh giá nhóm (100–150 từ)

> Đánh giá trung thực về quá trình làm việc nhóm.

**Phân công thực tế:**

| Thành viên | Phần đã làm | Sprint |
|------------|-------------|--------|
| TODO (Tên TL) | Triển khai hàm Embedding & Upsert vector lên DB. Thực hiệm eval hệ thống. | Sprint 1, 4 |
| TODO (Tên RO) | Preprocess text data, xây dựng logic cho bộ Chunking `_split_by_size`. | Sprint 1, 2 |
| Đàm Lê Văn Toàn | Phụ trách Documentation (Overview Architecture, Tuning Log, Individual Report), kiểm soát chất lượng metrics. | Sprint 4 |
| TODO (Tên TV4) | Xử lý Prompt tuning & LLM Generation (Groundedness check). | Sprint 3 |

**Điều nhóm làm tốt:**
Làm theo chu trình rõ ràng, chia tách chức năng độc lập thay vì thao tác chung lên một hệ thống cùng lúc. Nhóm rất sát sao việc A/B Testing, nhìn điểm log để bóc tách các điểm yếu thay vì cố đoán thông qua phỏng đoán mù.

**Điều nhóm làm chưa tốt:**
Quản lý cấu hình Dependency nội bộ các package Python chưa đồng nhất. Còn thiếu sót nhiều về việc giải quyết gốc rễ của tiễng Việt tokenizer do rào cản nền tảng từ thư viện BM25 truyền thống tạo ra.

---

1. Tích hợp `underthesea` Tokenizer: Do hiểu rõ BM25 tách các cụm tiếng Việt (vd: "xử", "lý") dẫn đến Sparse Search rơi vào "nhiễu từ vựng". Một tokenizer NLP tốt sẽ tạo lợi thế nhảy vọt về điểm Recall thông qua exact-level query logic.
2. Tối ưu lại prompt trả lời Abstain: Từ điểm fail gq07, hệ thống có thể kết hợp thêm Query Expansion để rà soát rõ ngữ cảnh (vd: Penalty của SLA), từ đó LLM có thể trả về thông báo từ chối tốt hơn.

---

*File này lưu tại: `reports/group_report.md`*  
*Commit sau 18:00 được phép theo SCORING.md*
