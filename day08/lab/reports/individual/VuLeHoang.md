# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Vũ Lê Hoàng 
**Vai trò trong nhóm:** Tech Lead / Retrieval Owner / Eval Owner / Documentation Owner  
**Ngày nộp:** 13/4/2026 
**Độ dài yêu cầu:** 500–800 từ

---

## 1. Tôi đã làm gì trong lab này? (100-150 từ)

Tôi đã đảm nhận vai trò Prompt Engineer, tập trung vào việc thiết kế và tối ưu hóa các prompt cho hệ thống RAG. Tôi đã thử nghiệm với nhiều biến thể của prompt để cải thiện hiệu suất của mô hình trong việc trả lời các câu hỏi phức tạp. Ngoài ra, tôi cũng tham gia vào quá trình đánh giá kết quả bằng cách sử dụng scorecard và phân tích các lỗi để xác định nguyên nhân gốc rễ. Tôi đã làm việc chặt chẽ với các thành viên khác trong nhóm để đảm bảo rằng các phần indexing, retrieval và generation hoạt động hiệu quả và đồng bộ.

_________________

---

## 2. Điều tôi hiểu rõ hơn sau lab này (100-150 từ)

Tôi đã hiểu rõ hơn về cách hoạt động của RAG pipeline, đặc biệt là cách các thành phần indexing, retrieval và generation tương tác với nhau. Tôi nhận ra rằng việc thiết kế prompt không chỉ đơn giản là đưa ra câu hỏi mà còn phải cân nhắc đến ngữ cảnh và cách thức mà mô hình sẽ xử lý thông tin. Tôi cũng học được rằng việc đánh giá kết quả không chỉ dựa trên điểm số mà còn phải phân tích sâu về lỗi để cải thiện hệ thống. Điều này giúp tôi có cái nhìn toàn diện hơn về quá trình phát triển và tối ưu hóa một hệ thống RAG.

_________________

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn (100-150 từ)

Tôi cảm thấy ngạc nhiên về mức độ phức tạp của việc thiết kế prompt hiệu quả. Ban đầu, tôi nghĩ rằng chỉ cần đưa ra câu hỏi rõ ràng là đủ, nhưng thực tế cho thấy rằng cách thức trình bày và cấu trúc của prompt có thể ảnh hưởng lớn đến kết quả. Tôi cũng gặp khó khăn trong việc phân tích lỗi, đặc biệt là khi xác định liệu lỗi nằm ở indexing, retrieval hay generation. Điều này đòi hỏi một sự hiểu biết sâu sắc về từng thành phần của pipeline và cách chúng tương tác với nhau, điều mà tôi vẫn đang học hỏi và cải thiện.

_________________

---

## 4. Phân tích một câu hỏi trong scorecard (150-200 từ)


**Câu hỏi:** Question 06: "Ticket P1 không được phản hồi sau 10 phút. Hệ thống tự động làm gì?"


**Phân tích:**

Tôi cảm thấy question 06 khá là thú vị khi mà nó liên quan đến một tình huống thực tế trong quản lý sự cố. Câu hỏi này yêu cầu hệ thống phải hiểu và áp dụng quy tắc SLA một cách chính xác, đồng thời phải biết cách tích hợp với các công cụ như Slack và PagerDuty để thông báo khi có sự cố xảy ra. Điều này đòi hỏi hệ thống không chỉ phải có khả năng truy xuất thông tin từ tài liệu SLA mà còn phải hiểu được ngữ cảnh của tình huống và hành động phù hợp. Việc tự động escalate ticket P1 lên Senior Engineer nếu không có phản hồi trong 10 phút là một quy tắc quan trọng để đảm bảo rằng các sự cố nghiêm trọng được xử lý kịp thời, và việc gửi thông báo tới các kênh liên quan giúp đảm bảo rằng tất cả các bên liên quan đều được cập nhật về tình hình.

_________________

---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì? (50-100 từ)

Nếu có thêm thời gian, tôi sẽ tập trung vào việc tối ưu hóa prompt hơn nữa bằng cách thử nghiệm với các cấu trúc và ngữ cảnh khác nhau để xem cách chúng ảnh hưởng đến kết quả. Tôi cũng muốn đào sâu vào việc phân tích lỗi để hiểu rõ hơn về nguyên nhân gốc rễ của các vấn đề và tìm cách khắc phục chúng một cách hiệu quả hơn. Ngoài ra, tôi sẽ dành thời gian để nghiên cứu thêm về các công cụ và kỹ thuật mới trong lĩnh vực RAG để cải thiện hiệu suất của hệ thống.
_________________

---

