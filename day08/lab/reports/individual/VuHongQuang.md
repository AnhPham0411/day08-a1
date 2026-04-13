# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Vũ Hồng Quang   
**Vai trò trong nhóm:** Eval Owner A  
**Ngày nộp:** 13/04/2026  
**Độ dài yêu cầu:** 500–800 từ

---

## 1. Tôi đã làm gì trong lab này? (100-150 từ)

Trong lab này, tôi chủ yếu làm việc ở Sprint 3 và Sprint 4 với vai trò Eval Owner A. Nhiệm vụ chính của tôi là triển khai các function đánh giá trong file eval.py chịu trách nhiệm chạy pipeline với bộ test questions, xuất log kết quả (grading_run.json) đúng format trước deadline. Công việc của tôi kết nối trực tiếp với Retrieval Owner (cung cấp input test để kiểm tra retrieval quality) và Eval Owner B (cung cấp dữ liệu đầu vào cho scorecard và A/B comparison). Điều này giúp nhóm có một evaluation loop rõ ràng và đo được hiệu quả của từng thay đổi trong pipeline.
_________________

---

## 2. Điều tôi hiểu rõ hơn sau lab này (100-150 từ)

Sau lab này, tôi hiểu rõ hơn về evaluation loop trong RAG. Trước đây tôi nghĩ evaluation chỉ là “chấm điểm output”, nhưng thực tế nó là một vòng lặp liên tục: thiết kế câu hỏi → chạy pipeline → đo metrics → phân tích lỗi → điều chỉnh hệ thống → lặp lại. Nếu thiết kế câu hỏi kém (quá dễ hoặc không có expected source rõ ràng), toàn bộ evaluation sẽ mất giá trị.

Ngoài ra, tôi hiểu sâu hơn về sự khác biệt giữa faithfulness và answer relevance. Một câu trả lời có thể đúng về mặt nội dung (relevant) nhưng lại không grounded vào context (không faithful), tức là LLM có thể “bịa”. Điều này rất nguy hiểm trong RAG, vì mục tiêu không phải là trả lời đúng bằng mọi giá, mà là trả lời đúng dựa trên dữ liệu đã retrieve.
_________________

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn (100-150 từ)

Điều khiến tôi bất ngờ nhất là việc Context Recall luôn đạt 5.0, không có sự khác biệt rõ ràng giữa hệ thống của chúng tôi và hệ thống kiểm tra đánh giá. Có lẽ là do dữ liệu này không quá phức tạp và các trường hợp thử nghiệm không quá khó.
_________________

---

## 4. Phân tích một câu hỏi trong scorecard (150-200 từ)

**Câu hỏi:** [gq09] ERR-403-AUTH là lỗi gì và cách xử lý?

**Kết quả quan sát:** Baseline trả lời đúng: "Tôi không có đủ dữ liệu trong tài liệu nội bộ để trả lời câu hỏi này". Điếm số là Faithful: 5 | Relevant: 1 | Recall: None | Complete: 1. Ở variant không có sự cải thiện, kết quả ý hệt với baseline. Nguyên nhân là do không hề tồn tại tài liệu liên quan đến câu hỏi.

**Phân tích:** 
- Faithful 5: hệ thống của chúng tôi đã trả lời trung thực, tài liệu không đề cập đến vấn đề này.
- Revelant 1: Đây là điều dễ hiểu, hệ thống không trả lời được câu hỏi nên mức dộ liên quan tới câu hỏi gần như không có
- Recall None: hệ thống không tìm được bất cứ tài liệu nào, bằng chứng nào liên quan đến câu hỏi
-Complete 1: hệ thống không trả lời câu hỏi nên nhận điểm số là 1.
Tất cả những điểm số này đều là kết quả của việc không có tài liệu liên quan.
_________________

---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì? (50-100 từ)

Nếu có thêm thời gian, tôi sẽ thiết kế bộ evaluation questions theo hướng nhiều câu hỏi hơn khó hơn, bao phủ nhiều trường hợp hơn đặc biệt là multi-hop reasoning và negative queries (câu hỏi không có trong tài liệu). Điều này giúp phân biệt rõ hơn giữa pipeline tốt và pipeline trung bình.
_________________

---

*Lưu file này với tên: `reports/individual/[ten_ban].md`*
*Ví dụ: `reports/individual/nguyen_van_a.md`*
