# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Phạm Tuấn Anh  
**Vai trò trong nhóm:** Tech Lead  
**Ngày nộp:** 13/04/2026  

---

## 1. Em đã làm gì trong lab này?

Với vai trò Tech Lead, em chịu trách nhiệm thiết lập nền tảng và điều phối luồng dữ liệu end-to-end theo đúng Checklist:

- **Khởi tạo hệ thống:** Thiết lập `requirements.txt` (`chromadb`, `openai`, `rank-bm25`) và cấu hình môi trường `.env`.
- **Indexing Pipeline (`index.py`):** Triển khai hàm `get_embedding` sử dụng `text-embedding-3-small` và hoàn thiện `build_index` để embed/upsert thành công **30 chunks** vào ChromaDB (cosine space).
- **Generation Pipeline (`rag_answer.py`):** Triển khai `call_llm` kết nối model `qwen/qwen3-next-80b` (`temperature=0`). Thiết kế **Grounded Prompt** (~800 tokens) với các nguyên tắc: `[GROUNDING]`, `[ABSTAIN]` chống Hallucination và quy trình `[TRÍCH DẪN]` nguồn `[1][2]`.
- **Điều phối Pipeline:** Xây dựng hàm `rag_answer` đóng vai trò nhạc trưởng, kết nối kết quả từ các module Hybrid Search của Retrieval Owner thành luồng phản hồi hoàn chỉnh.

---

## 2. Điều em hiểu rõ hơn sau lab này

Em hiểu sâu sắc tầm quan trọng của **Cấu trúc dữ liệu trung gian (Internal API)**. Việc thống nhất định dạng metadata (`source`, `section`, `effective_date`) giữa bước xử lý của Retrieval Owner và bước sinh văn bản của em là yếu tố tiên quyết để trích dẫn chính xác đến từng Section tài liệu.

Thứ hai, em nhận ra **Prompt Engineering là chốt chặn cuối cùng** của tính tin cậy. Dù Retriever lấy đúng context, nếu Prompt không đủ chặt chẽ trong quy tắc `Abstain`, mô hình vẫn có xu hướng suy diễn. Việc kiểm soát LLM cần thiết lập một hệ thống quy tắc logic (Frame-of-reference) để mô hình bám sát dữ liệu gốc tuyệt đối.

---

## 3. Thách thức kỹ thuật và Phân tích hiệu năng

Thách thức lớn nhất là **độ trễ (Latency)**. Theo `grading_run_variant.json`, latency trung bình dao động từ **10 - 12 giây** mỗi câu hỏi. Độ trễ này đến từ hai nguồn:
1.  **Prompt Overhead:** Bộ prompt bọc thép (~800 tokens) khiến thời gian generation lâu hơn.
2.  **Reasoning Time:** Model cần đối chiếu nhiều đoạn context phức tạp để tuân thủ quy tắc trích dẫn.

Tuy nhiên, em chấp nhận sự đánh đổi này để lấy tính an toàn. Thực tế các câu gq01, gq09 đều trả kết quả chuẩn xác với trích dẫn đầy đủ, chứng minh pipeline vận hành ổn định.

---

## 4. Phân tích Metric và Case Study gq07

**Câu hỏi:** `[gq07] Công ty sẽ phạt bao nhiêu nếu team IT vi phạm cam kết SLA P1?`

**Kết quả:** Hệ thống trả lời Abstain: *"Tôi không có đủ dữ liệu trong tài liệu nội bộ để trả lời câu hỏi này."* 

**Phân tích sâu:** Scorecard chấm **Faithfulness=0** và **Relevance=0**. Dưới góc độ Tech Lead, đây là một **"Safety Win"**. Trong tài liệu không có quy định về phạt tiền. Nếu hệ thống đưa ra con số, đó sẽ là lỗi Hallucination nghiêm trọng. Việc LLM nhận diện thiếu hụt thông tin và kích hoạt kịch bản `Abstain` là minh chứng thành công của bộ Prompt Engineering em thiết kế.

---

## 5. Định hướng cải tiến trong thực tế kinh doanh

Để vận hành thực tế hiệu quả và kinh tế, em đề xuất:

1.  **Tối ưu Chi phí (Token Efficiency):** Prompt 800 tokens gây chi phí lớn. Em sẽ nghiên cứu **Few-shot Prompting** tối giản hoặc **Prompt Compression** để giảm 30-40% token đầu vào mà vẫn giữ nguyên ràng buộc logic.
2.  **Tích hợp Business Workflows:** Hệ thống cần tích hợp trực tiếp với **Slack/Jira**. Khi gặp case "Abstain", hệ thống tự động gửi thông báo đến bộ phận Knowledge Management cập nhật tài liệu thiếu, tạo hệ sinh thái tri thức được hoàn thiện tự động.
�ng cho sự thành công của bộ Prompt Engineering mà em đã thiết kế.

---


