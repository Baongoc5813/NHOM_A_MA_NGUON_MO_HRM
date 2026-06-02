# 🚀 Dự án: Phát triển Phân hệ Quản trị Nguồn nhân lực (HRM) trên nền tảng Odoo 

> **Nhóm thực hiện:** Nhóm A (6 thành viên)
> **Nền tảng:** Mã nguồn mở Odoo (Open Source ERP)

Chào mừng các thành viên Nhóm A đến với không gian làm việc chính thức của dự án. Repository này được sử dụng để quản lý toàn bộ mã nguồn, tài liệu thiết kế và tiến độ triển khai các tính năng mới cho phân hệ HRM. Các thành viên lưu ý theo dõi bảng phân chia công việc dưới đây để đảm bảo hoàn thành tiến độ và thực hiện pull/push code đúng nhánh được giao.

---

## 📅 BẢNG PHÂN CHIA CÔNG VIỆC VÀ TIẾN ĐỘ CHI TIẾT (WBS & GANTT CHART)

Hiện tại, tất cả các hạng mục giai đoạn đầu và các tính năng cốt lõi đều đã đạt **100% tiến độ thiết kế/phân tích hệ thống**. Toàn đội bắt đầu chuyển trạng thái sang triển khai code và kiểm thử backend/frontend.

### Phase 1: Chuẩn bị Tài liệu & Xác định Đề tài (100%)
* **Nghiên cứu tài liệu tham khảo:** Toàn bộ thành viên tìm kiếm giải pháp và tổng quan đề tài.
* **Thực trạng triển khai:** Phân tích thực trạng doanh nghiệp, khảo sát quy trình vận hành thực tế để đưa ra bài toán tối ưu.

### Phase 2: Phân tích Doanh nghiệp & Thiết lập Quy trình (100%)
* **Khảo sát & Họp nhóm:** Định hình luồng nghiệp vụ của các phân hệ core.
* **Quy trình chi tiết:** Vẽ và mô tả chi tiết các sơ đồ BPMN cho các quy trình tuyển dụng, chấm công, tính lương.
* **Đánh giá lại hệ thống:** Họp rà soát và nghiệm thu bàn giao tài liệu chương 1 & chương 2.

### Phase 3: Thiết lập Hệ thống Master Data (100%)
* **Cài đặt & Cấu hình hệ thống:** Phân quyền người dùng, cấu hình ban đầu cho Odoo instance.
* **Import dữ liệu & Master Data:** Thiết lập danh mục phòng ban, chức vụ, danh sách ứng viên (Candidates), danh sách nhân viên, loại hợp đồng, hình thức chấm công (Attendance Methods).

---

## 🛠️ CHI TIẾT PHÂN CHIA NHIỆM VỤ PHÁT TRIỂN TÍNH NĂNG MỚI (PHASE 4)

Dưới đây là ma trận phân công thiết kế chi tiết (Use Case, High-level Design, Data Design) và triển khai lập trình cho các module mở rộng của HRM:

| Tên Tính Năng Mới | Nội Dung Thiết Kế & Phát Triển | Thành Viên Phụ Trách | Trạng Thái Thiết Kế |
| :--- | :--- | :---: | :---: |
| **Phân hệ Nhân Sự Tổng Quan (HRM Core)** | Mô tả sơ đồ BPMN từ quy trình T1 đến T6, phân quyền người dùng, vẽ Use Case chi tiết. | *Cả nhóm* | Done (100%) |
| **Talent Pool & Auto Re-engagement** | Thiết kế Use Case, giao diện người dùng, cấu hình backend và cơ sở dữ liệu để tự động tương tác lại với ứng viên tiềm năng. | *Phụ trách Module 1* | Done (100%) |
| **Interviews Scheduling & Tracking** | Thiết kế lịch hẹn phỏng vấn thông minh, theo dõi trạng thái ứng viên qua các vòng, đồng bộ hóa thông báo qua email. | *Phụ trách Module 2* | Done (100%) |
| **Hiring Workflow Automation** | Tự động hóa quy trình phê duyệt tuyển dụng, chuyển trạng thái từ hồ sơ ứng viên sang hồ sơ thử việc tự động. | *Phụ trách Module 3* | Done (100%) |
| **Candidate Portal** | Cổng thông tin dành riêng cho ứng viên (High-level & Data design cho giao diện web portal), giúp ứng viên cập nhật thông tin và theo dõi kết quả. | *Phụ trách Module 4* | Done (100%) |
| **Hybrid Work & WFH Management** | Module quản lý mô hình làm việc linh hoạt, đăng ký làm việc từ xa (WFH), tracking hiệu suất và đồng bộ chấm công. | *Phụ trách Module 5* | Done (100%) |
| **Smart Workload Balancing** | Tính năng tự động phân bổ khối lượng công việc, tối ưu hóa task dựa trên năng lực và lịch làm việc của nhân sự. | *Phụ trách Module 6* | Done (100%) |

---

## 💻 QUY ĐỊNH PHÁT TRIỂN & PULL/PUSH CODE (DÀNH CHO THÀNH VIÊN)

Để tránh xung đột mã nguồn (Code Conflict) khi làm việc nhóm trên Odoo, các thành viên tuyệt đối tuân thủ quy trình sau:

1. **Khởi tạo nhánh (Branching):**
   * Không push code trực tiếp lên nhánh `main`/`master`.
   * Mỗi thành viên tạo một nhánh riêng dựa trên tính năng mình phụ trách, ví dụ: `feature/talent-pool`, `feature/interview-schedule`, `feature/hybrid-work`,...

2. **Quy trình cập nhật mã nguồn:**
   * Trước khi bắt đầu viết code mới: Luôn chạy lệnh `git pull origin main` để cập nhật các thay đổi mới nhất từ các thành viên khác.
   * Sau khi hoàn thành tính năng trên local: Tiến hành `git push origin feature/ten-tinh-nang`.

3. **Tạo Pull Request (PR):**
   * Tạo PR từ nhánh tính năng của bạn về nhánh chính.
   * Gắn thẻ (Assign) Nhóm trưởng hoặc gửi thông báo lên nhóm để tiến hành review code, kiểm tra cấu hình module Odoo (`__manifest__.py`, file XML, file Python models) trước khi merge.

4. **Lưu ý cấu hình Odoo:** * Nhớ cập nhật phiên bản số (version) trong file cấu hình module và thực hiện `-u` (upgrade) dữ liệu hệ thống khi chạy thử nghiệm trên local.
