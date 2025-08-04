đây là notebook về quá trình tìm hiểu và thực hiện dự án đọc tài liệu 

## LayoutReader: Pre-training of Text and Layout
-> bài báo này độ chính xác cực cao nhưng chỉ dành cho văn bản tiếng anh 
khuyết điểm: 
- là mình phải train lại từ đầu bằng văn bản tiếng việt 

## [VGT (Vision Grid Transformer for Document Layout Analysis)](https://github.com/AlibabaResearch/AdvancedLiterateMachinery/tree/main/DocumentUnderstanding/VGT)
-> chưa biết được vì cái này chưa biết nó có support tiếng việt hay không nhưng mình nghĩ là có vì do mấy thằng pháp sư trung hoa làm nên chắc nó cũng base trên mô hình qwen và vì nó của alibaba 

## Vấn đề được đặt ra 
![[Pasted image 20250519160758.png]]
![[Pasted image 20250519160808.png]]


## Đề xuất kết quả 
#### Sử dụng VQA opensource hiệu quả cao áp dụng được ngay lập tức
điểm yếu: tốn tài nguyên rất nhiều và không làm chủ được công nghệ cũng như tốc độ đầu ra chậm

#### Sử dụng VQA opensource quantize hiệu quả cao áp dụng được ngay lập tức
điểm yếu: tốn tài nguyên rất nhiều và không làm chủ được công nghệ cũng như tốc độ đầu ra chậm 

#### Sử dụng Bounding box như bình thường và làm thủ công 
điểm yếu: không thể đọc thông tin phức tạp ví dụ không thể đọc được đúng những khu vực có tiêu đề cũng như là dữ liệu loại bảng và những kiểu dữ liệu tiêu đề 

#### Sử dụng Bounding box kết hợp với mô hình LLM để xử lý theo kiểu quy luật 
điểm mạnh: làm chủ được công nghệ, đầu tư khúc đầu rất nhiều nhưng về sau thì không cần đầu tư 
điểm yếu: không thể phân tích được những dữ liệu dạng bản

#### Sử dụng VQA tự thiết kế 
điểm mạnh: làm chủ công nghệ, đầu tư khúc đầu rất nhiều về sau thì không cần đầu tư nx, cũng như đầu ra được tối ưu về mặt hiệu suất lẫn tốc độ 
<font color="#f79646">điểm yếu: tốn rất nhiều thời gian </font>



## Note 
-> có thể sử dụng thử MedGemma để dùng cho OCR cũng được 

paddle ocr
ds4sd/SmolDocling-256M-preview

-> Vì Model quá bé nên nó tự hiểu là nó sẽ bắt đầu tóm tắt những nội dung dài

-> vì thế ta sẽ chia ra làm hai loại một là nội dung trích xuất (hay còn gọi là nội dung phi cấu trúc) và nội dung có cấu trúc 