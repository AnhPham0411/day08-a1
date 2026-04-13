# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Đàm Lê Văn Toàn  
**Vai trò trong nhóm:** Documentation Owner  
**Ngày nộp:** 2026-04-13  
**Độ dài yêu cầu:** 500–800 từ

---

## 1. Tôi đã làm gì trong lab này? (100-150 từ)

Trong nhóm, tôi đảm nhận vai trò **Documentation Owner**, tập trung đóng góp vào **Sprint 4**. Nhiệm vụ chính của tôi là vận hành phân tích dữ liệu qua file `scorecard`, tổng hợp metric (Faithfulness, Relevance, Recall) tạo báo cáo A/B Testing trong `tuning-log.md`. Dựa vào việc đối chiếu log giữa variant và baseline, tôi giúp truy xuất các root cause dẫn đến sự sai lệch và từ đó tham gia đề xuất cập nhật Architecture Report (điển hình việc cập nhật tham số `dense_weight=0.8`). Công việc này kết nối trực tiếp đến cấu hình code và luồng review chất lượng của Eval Owner/Tech Lead, đem lại dữ liệu đánh giá trung thực cho mọi bước cải tiến pipeline hiện hành.

---

## 2. Điều tôi hiểu rõ hơn sau lab này (100-150 từ)

Khái niệm để lại trong tôi ấn tượng nhất là sự điều phối giữa **Hybrid Retrieval và Reciprocal Rank Fusion (RRF)**. Trước Lab, tôi lầm tưởng tìm kiếm dữ liệu qua Vector (Dense) mặc nhiên bao quát toàn bộ ngữ nghĩa tối ưu nhất. Nhưng với một môi trường chứa quá nhiều đặc tả công nghệ và mã số phức tạp, cấu trúc Sparse (BM25) lại cho thấy tầm quan trọng bắt buộc phải có cho trường phái Exact-Match keywords. Thông qua thao tác điều chỉnh sự bù trừ Weight của RRF, tôi hình dung việc dung hòa hai cỗ máy tìm kiếm mang lại kết quả "kéo – thả" (như việc ép Sparse nhẹ hơn tránh nhiễu do Tokenizer từ điển Tiếng Việt) vừa giữ được semantic vừa giữ được keyword chuyên ngành.

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn (100-150 từ)

Tôi dành một thời gian dài lúng túng với **vấn đề nhiễu khi thiết lập cấu hình thuộc về Sparse (BM25)** bằng tiếng Việt. Suy nghĩ ban đầu của tôi cho rằng cứ bật Hybrid thì Recall tự nhiên tăng cao ngay lập tức. Tuy vậy, thực tế chạy log chỉ ra mô hình bị "lạc đường" đối với tài liệu gốc so với Baseline.

Qúa trình đào sâu bóc tách Retrieval Debug Top K đã giúp tôi khai sáng nguyên nhân: BM25 bị tách từ cơ bản bằng khoảng trắng đơn thuần, biến một cụm từ ghép ("lịch sử", "hoàn tiền") vỡ vụn thành các từ độc lập, khiến tỷ lệ mapping xuất hiện ảo trên diện rộng. Kết quả thay vì tốt hơn, hệ thống nhầm lẫn kéo file sai lên trên cùng. Nhờ đó, tôi nghiệm ra rằng bài toán xử lý NLP với Tiếng Việt bắt buộc cần can thiệp Tokenizer, hoặc bù trừ bằng tinh chỉnh `weight` chênh lệch như cấu hình cuối cùng.

---

## 4. Phân tích một câu hỏi trong scorecard (150-200 từ)

**Câu hỏi:** gq05 - "Contractor từ bên ngoài công ty có thể được cấp quyền Admin Access không? Nếu có, cần bao nhiêu ngày và có yêu cầu đặc biệt gì?"

**Phân tích:**
- **Baseline Dense trả lời:** "Abstain" (Từ chối đưa đáp án do không trích xuất đủ ngữ cảnh), tự động kéo điểm Relevance và Faithfulness về mức 0/0.
- **Phân loại lỗi:** Triệu chứng này đặc trưng của tiến trình **Retrieval**. Vector Embedding thuần túy hiểu nghĩa tổng quát nhưng không ghép nối đủ tín hiệu từ những từ vựng chuyên ngành hoặc danh từ phân lớp cụ thể như: "Day", "Admin Access", "Contractor", khiến Chunk chứa các tham số quan trọng trong "access_control_sop" trượt ra ngoại vi Top k.
- **Sự cải thiện của Variant:** Variant đã khắc phục gọn gàng. Thuật toán Hybrid với cấu trúc BM25 đánh trúng các Keyword rễ vào đúng file SOP, và nhờ được bù đắp thêm `dense_weight`, dữ liệu không bị "nhiễu token". Từ đoạn Text Context đã lọt Top, hệ Generation tự tin sinh đủ các yêu cầu chi tiết của Admin Access đối với Vendor.

---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì? (50-100 từ)

1. Tôi muốn cấu trúc hóa lại phương pháp thiết lập **Indexing (Chunking Strategy)**. Theo log, quy trình hiện tại có phần cơ học. Cấu hình cấu trúc dữ liệu theo phân cấp Semantic Metadata có lẽ sẽ là giải pháp tối thượng cho đoạn text dài.
2. Thử nghiệm thay thế tokenizer của BM25 sang công cụ `underthesea` dành riêng cho tiếng Việt để vá lỗ hổng "trích xuất rác" ở kết quả truy vấn Sparse kéo dài từ Sprint 2 như đã phân tích.

---

*Lưu file này với tên: `reports/individual/[ten_ban].md`*
*Ví dụ: `reports/individual/nguyen_van_a.md`*
