# BÁO CÁO ĐỒ ÁN TỐT NGHIỆP

## HỆ THỐNG KIỂM THỬ VÀ ĐÁNH GIÁ CHẤT LƯỢNG PHẦN MỀM

---

**Tên hệ thống:** WebTesterPro

**Mô tả:** Hệ thống kiểm thử website toàn diện - tích hợp 8 module kiểm thử (SEO, Performance, Security, Accessibility, Crawler, Visual, Monitor, Scanner) trên nền tảng web với giao diện Dashboard.

**Công nghệ sử dụng:** Python/FastAPI, SQLAlchemy, SQLite, Playwright, Jinja2, Tailwind CSS

---

# MỤC LỤC

1. [Chương 1: Tổng quan dự án](#chương-1-tổng-quan-dự-án)
2. [Chương 2: Phân tích nghiệp vụ](#chương-2-phân-tích-nghiệp-vụ)
3. [Chương 3: Phân tích và thiết kế hệ thống](#chương-3-phân-tích-và-thiết-kế-hệ-thống)
4. [Chương 4: Kiến trúc hệ thống](#chương-4-kiến-trúc-hệ-thống)
5. [Chương 5: Thiết kế cơ sở dữ liệu](#chương-5-thiết-kế-cơ-sở-dữ-liệu)
6. [Chương 6: Thiết kế giao diện](#chương-6-thiết-kế-giao-diện)
7. [Chương 7: Xây dựng hệ thống](#chương-7-xây-dựng-hệ-thống)
8. [Chương 8: Kiểm thử hệ thống](#chương-8-kiểm-thử-hệ-thống)
9. [Chương 9: Đánh giá và hướng phát triển](#chương-9-đánh-giá-và-hướng-phát-triển)
10. [Chương 10: Phụ lục hình ảnh](#chương-10-phụ-lục-hình-ảnh)

---

# CHƯƠNG 1: TỔNG QUAN DỰ ÁN

## 1.1 Giới thiệu hệ thống

**WebTesterPro** là một hệ thống kiểm thử website toàn diện, được phát triển bằng Python với FastAPI framework. Hệ thống cung cấp 8 module kiểm thử chuyên biệt giúp đánh giá chất lượng website một cách đa chiều, bao gồm:

| Module | Chức năng |
|--------|-----------|
| **SEO Analysis** | Phân tích SEO: Meta tags, cấu trúc heading, Open Graph, Schema.org |
| **Performance** | Đo hiệu năng: Core Web Vitals (LCP, FID, CLS, TTFB, FCP) |
| **Security Scan** | Quét bảo mật: XSS, SQL Injection, Security Headers |
| **Accessibility** | Kiểm tra khả năng tiếp cận: WCAG 2.1 với axe-core |
| **Crawler** | Thu thập URL, phân tích cấu trúc site theo depth |
| **Visual Testing** | Chụp ảnh đa viewport, so sánh responsive layout |
| **Monitor** | Theo dõi uptime, response time và cảnh báo downtime |
| **Scanner** | Quét forms, links, resources trên website |

Hệ thống sử dụng **Playwright** làm engine để tự động hóa trình duyệt, kết hợp với giao diện Dashboard hiện đại sử dụng **Jinja2 templates** và **Tailwind CSS**.

## 1.2 Bối cảnh bài toán

Trong bối cảnh công nghệ thông tin phát triển mạnh mẽ, website là kênh giao tiếp chính giữa doanh nghiệp và khách hàng. Việc đảm bảo chất lượng website đòi hỏi kiểm thử đa chiều trên nhiều phương diện:

- **SEO**: Đảm bảo website được index tốt bởi các công cụ tìm kiếm
- **Performance**: Tốc độ tải trang ảnh hưởng trực tiếp đến trải nghiệm người dùng và xếp hạng tìm kiếm
- **Security**: Bảo vệ website khỏi các mối đe dọa từ hacker và malware
- **Accessibility**: Đảm bảo mọi người đều có thể tiếp cận nội dung website

## 1.3 Thực trạng hiện nay

Hiện tại, việc kiểm thử website thường gặp các vấn đề:

| Vấn đề | Mô tả |
|---------|--------|
| **Phân mảnh công cụ** | Cần sử dụng nhiều công cụ riêng biệt cho từng loại kiểm thử |
| **Thiếu tự động hóa** | Nhiều kiểm thử vẫn được thực hiện thủ công, tốn thời gian |
| **Không có dashboard** | Khó theo dõi và so sánh kết quả giữa các lần kiểm thử |
| **Thiếu báo cáo chuyên nghiệp** | Kết quả kiểm thử không được trình bày trực quan |

## 1.4 Các vấn đề tồn tại cần giải quyết

Hệ thống WebTesterPro được xây dựng để giải quyết các vấn đề trên:

1. **Tích hợp đa module**: Tất cả 8 module kiểm thử được tích hợp trong một hệ thống duy nhất
2. **Tự động hóa hoàn toàn**: Sử dụng Playwright để thực thi kiểm thử tự động
3. **Dashboard trực quan**: Giao diện web cho phép theo dõi tiến trình và kết quả real-time
4. **Báo cáo đa dạng**: Xuất báo cáo dưới dạng JSON, HTML, CSV
5. **Chia sẻ kết quả**: Tạo link chia sẻ báo cáo với thời hạn

## 1.5 Mục tiêu hệ thống

| Mục tiêu | Mô tả |
|-----------|--------|
| **TO.1** | Cung cấp nền tảng kiểm thử website toàn diện với 8 module |
| **TO.2** | Cho phép người dùng tạo, theo dõi và quản lý các bài kiểm thử |
| **TO.3** | Hiển thị kết quả kiểm thử trực quan qua Dashboard |
| **TO.4** | Hỗ trợ xuất báo cáo đa định dạng (JSON, HTML, CSV) |
| **TO.5** | Cho phép chia sẻ kết quả kiểm thử qua link |
| **TO.6** | Cung cấp analytics để theo dõi xu hướng chất lượng website |

## 1.6 Ý nghĩa thực tiễn

| Ý nghĩa | Chi tiết |
|----------|----------|
| **Tiết kiệm thời gian** | Tự động hóa quy trình kiểm thử, giảm 80% thời gian so với kiểm thử thủ công |
| **Nâng cao chất lượng** | Phát hiện sớm các vấn đề về SEO, performance, security, accessibility |
| **Chuẩn hóa quy trình** | Áp dụng các tiêu chuẩn quốc tế (WCAG 2.1, Core Web Vitals) |
| **Đào tạo nhân sự** | Công cụ hữu ích cho đội ngũ QA và developer |

## 1.7 Phạm vi dự án

### In Scope (Trong phạm vi)

| STT | Nội dung |
|-----|----------|
| 1 | 8 module kiểm thử (SEO, Performance, Security, Accessibility, Crawler, Visual, Monitor, Scanner) |
| 2 | Hệ thống Authentication với JWT |
| 3 | Dashboard quản lý và theo dõi |
| 4 | Xuất báo cáo (JSON, HTML, CSV) |
| 5 | Chia sẻ báo cáo qua link |
| 6 | Analytics và thống kê |
| 7 | So sánh 2 báo cáo |
| 8 | User management và Admin panel |

### Out Scope (Ngoài phạm vi)

| STT | Nội dung |
|-----|----------|
| 1 | Kiểm thử tải (Load Testing) với nhiều concurrent users |
| 2 | Tích hợp CI/CD pipeline |
| 3 | API documentation tự động |
| 4 | Multi-tenant architecture |
| 5 | Kiểm thử trên nhiều trình duyệt cùng lúc |

## 1.8 Stakeholder Analysis

| Stakeholder | Vai trò | Mức độ ảnh hưởng | Nhu cầu |
|-------------|---------|-------------------|----------|
| **Người dùng thông thường** | Sử dụng hệ thống để kiểm thử website của mình | Cao | Tạo test, xem kết quả, xuất báo cáo |
| **Quản trị viên (Admin)** | Quản lý người dùng và hệ thống | Cao | Quản lý users, xem tất cả reports |
| **QA Engineer** | Sử dụng để kiểm thử website trước khi release | Cao | Báo cáo chi tiết, so sánh kết quả |
| **Developer** | Sử dụng để debug và cải thiện website | Trung bình | Kết quả nhanh, actionable recommendations |
| **Project Manager** | Theo dõi chất lượng website dự án | Trung bình | Dashboard overview, analytics |
| **DevOps** | Tích hợp vào CI/CD pipeline | Thấp | API để automation |

## 1.9 Business Value

| Giá trị | Mô tả | Đo lường |
|---------|--------|----------|
| **Tự động hóa** | Giảm thời gian kiểm thử thủ công | Thời gian kiểm thử giảm 80% |
| **Chất lượng** | Phát hiện sớm các vấn đề | Giảm 50% lỗi sau release |
| **Hiệu quả chi phí** | Một công cụ thay thế nhiều công cụ riêng biệt | Tiết kiệm chi phí license |
| **Năng suất** | QA team tập trung vào các test case phức tạp | Tăng 30% test coverage |
| **Chuẩn hóa** | Áp dụng tiêu chuẩn quốc tế (WCAG, Core Web Vitals) | Tuân thủ 100% |

## 1.10 Risk Analysis

| ID | Rủi ro | Mức độ | Xác suất | Tác động | Biện pháp giảm thiểu |
|----|--------|---------|----------|----------|------------------------|
| R01 | Playwright không tương thích với một số website | Cao | Trung bình | Cao | Xây dựng fallback mechanism, timeout handling |
| R02 | Tài nguyên server không đủ cho concurrent tests | Cao | Thấp | Cao | Giới hạn số lượng concurrent tests, queue system |
| R03 | Bảo mật khi chia sẻ báo cáo | Trung bình | Thấp | Cao | Token-based access, expiration, view count limit |
| R04 | Database growth khi lưu nhiều reports | Trung bình | Trung bình | Trung bình | Data retention policy, archiving old reports |
| R05 | Rate limiting bypass | Thấp | Thấp | Cao | Implement IP-based and token-based rate limiting |

---

# CHƯƠNG 2: PHÂN TÍCH NGHIỆP VỤ

## 2.1 Actor Analysis

### 2.1.1 Các Actor trong hệ thống

| Actor | Mô tả | Quyền hạn |
|-------|-------|-----------|
| **Anonymous User** | Người dùng chưa đăng nhập | Xem shared report (qua token) |
| **Registered User** | Người dùng đã đăng ký | Tạo test, xem kết quả, xuất báo cáo, chia sẻ |
| **Admin User** | Quản trị viên hệ thống | Tất cả quyền của User + quản lý users, xem all reports |

### 2.1.2 Actor Details

#### Actor 1: Anonymous User

- **Mô tả**: Người dùng chưa có tài khoản hoặc chưa đăng nhập
- **Tương tác với hệ thống**:
  - Xem trang đăng nhập/đăng ký
  - Xem shared report qua link chia sẻ
- **Quyền hạn**: Giới hạn

#### Actor 2: Registered User

- **Mô tả**: Người dùng đã đăng ký và đăng nhập thành công
- **Tương tác với hệ thống**:
  - Đăng nhập/đăng xuất
  - Tạo bài kiểm thử mới
  - Xem danh sách và chi tiết báo cáo
  - Xuất báo cáo (JSON, HTML, CSV)
  - Chia sẻ báo cáo qua link
  - So sánh 2 báo cáo
  - Xem Analytics dashboard
  - Theo dõi tiến trình test real-time (SSE)
- **Quyền hạn**: Chỉ xem và quản lý báo cáo của mình

#### Actor 3: Admin User

- **Mô tả**: Quản trị viên hệ thống
- **Tương tác với hệ thống**:
  - Tất cả chức năng của Registered User
  - Quản lý người dùng (xem, tạo, sửa, xóa)
  - Xem tất cả báo cáo của mọi user
  - Admin dashboard
- **Quyền hạn**: Toàn quyền hệ thống

## 2.2 Business Rules

### 2.2.1 Authentication Rules

| Mã | Quy tắc | Mô tả |
|----|---------|--------|
| BR01 | Password Strength | Password phải có ít nhất 8 ký tự, bao gồm chữ hoa, chữ thường và số |
| BR02 | Username Format | Username chỉ chứa chữ cái, số và dấu gạch dưới (_), 3-100 ký tự |
| BR03 | Email Unique | Email phải là duy nhất trong hệ thống |
| BR04 | Username Unique | Username phải là duy nhất trong hệ thống |
| BR05 | Token Expiry | Access token hết hạn sau 30 phút, Refresh token sau 7 ngày |
| BR06 | Rate Limiting | Giới hạn 5 lần đăng nhập thất bại / 15 phút / IP |

### 2.2.2 Test Rules

| Mã | Quy tắc | Mô tả |
|----|---------|--------|
| BR07 | URL Validation | URL phải bắt đầu bằng http:// hoặc https:// |
| BR08 | Module Selection | Phải chọn ít nhất 1 module khi tạo test |
| BR09 | Max Depth | Crawler depth tối đa là 5 |
| BR10 | Max Pages | Số trang tối đa khi crawl là 500 |
| BR11 | Monitor Duration | Thời gian monitor từ 10 đến 120 phút |

### 2.2.3 Report Rules

| Mã | Quy tắc | Mô tả |
|----|---------|--------|
| BR12 | Report Ownership | User chỉ có thể xem báo cáo của mình (trừ Admin) |
| BR13 | Share Token | Token chia sẻ có thời hạn (mặc định 30 ngày) |
| BR14 | Report Format | Hỗ trợ xuất: JSON, HTML, CSV |

### 2.2.4 Scoring Rules

| Mã | Quy tắc | Mô tả |
|----|---------|--------|
| BR15 | Score Range | Điểm số từ 0-100 |
| BR16 | SEO Score | Dựa trên: Title (15%), Meta tags (15%), Headings (15%), Images (15%), Links (10%), Content (15%), Technical (15%) |
| BR17 | Performance Score | Dựa trên Core Web Vitals: LCP (25%), CLS (25%), FID (25%), TTFB (15%), TBT (10%) |
| BR18 | Security Score | 100 - (Critical×30 + High×20 + Medium×10 + Low×5) |
| BR19 | Accessibility Score | 100 - (Critical×15 + Serious×10 + Moderate×5 + Minor×1) |

## 2.3 Functional Requirements

### 2.3.1 FR-001: Quản lý Authentication

| ID | Yêu cầu | Mô tả |
|----|----------|--------|
| FR-001.1 | Đăng ký tài khoản | User đăng ký với email, username, password |
| FR-001.2 | Đăng nhập | User đăng nhập với email/username và password |
| FR-001.3 | Đăng xuất | Xóa tokens và cookies |
| FR-001.4 | Refresh token | Tự động cấp token mới khi access token hết hạn |
| FR-001.5 | Xem thông tin user | Hiển thị profile của user hiện tại |

### 2.3.2 FR-002: Quản lý Tests

| ID | Yêu cầu | Mô tả |
|----|----------|--------|
| FR-002.1 | Tạo test mới | Chọn URL, modules, và các tùy chọn (max_depth, max_pages, viewport) |
| FR-002.2 | Theo dõi tiến trình | Real-time progress qua SSE (Server-Sent Events) |
| FR-002.3 | Xem kết quả | Hiển thị chi tiết kết quả từng module |
| FR-002.4 | Tải kết quả | Xuất báo cáo dưới dạng JSON, HTML, CSV |
| FR-002.5 | Lịch sử test | Xem danh sách các bài test đã thực hiện |

### 2.3.3 FR-003: Module Testing

| ID | Yêu cầu | Mô tả |
|----|----------|--------|
| FR-003.1 | SEO Analysis | Kiểm tra meta tags, headings, Open Graph, Schema.org |
| FR-003.2 | Performance Testing | Đo Core Web Vitals, load time, resource size |
| FR-003.3 | Security Scanning | Quét XSS, SQL Injection, security headers, sensitive files |
| FR-003.4 | Accessibility Check | WCAG 2.1 compliance với axe-core |
| FR-003.5 | Website Crawling | Thu thập URLs, phân tích cấu trúc site |
| FR-003.6 | Visual Testing | Chụp ảnh đa viewport |
| FR-003.7 | Website Monitoring | Theo dõi uptime và response time |

### 2.3.4 FR-004: Báo cáo và Chia sẻ

| ID | Yêu cầu | Mô tả |
|----|----------|--------|
| FR-004.1 | Xuất JSON | Xuất toàn bộ dữ liệu dạng JSON |
| FR-004.2 | Xuất HTML | Xuất báo cáo độc lập dạng HTML |
| FR-004.3 | Xuất CSV | Xuất dữ liệu dạng bảng CSV |
| FR-004.4 | Tạo share link | Tạo link công khai để chia sẻ báo cáo |
| FR-004.5 | So sánh reports | So sánh 2 báo cáo bên cạnh nhau |

### 2.3.5 FR-005: Analytics

| ID | Yêu cầu | Mô tả |
|----|----------|--------|
| FR-005.1 | Thống kê tổng quan | Total tests, completed tests, avg score |
| FR-005.2 | Score Trend | Biểu đồ xu hướng điểm số theo thời gian |
| FR-005.3 | Module Usage | Thống kê sử dụng các module |
| FR-005.4 | Test Frequency | Số lần test theo ngày |
| FR-005.5 | Performance Stats | Thống kê hiệu năng |

### 2.3.6 FR-006: Admin Functions

| ID | Yêu cầu | Mô tả |
|----|----------|--------|
| FR-006.1 | User Management | CRUD users |
| FR-006.2 | View All Reports | Admin xem tất cả reports |
| FR-006.3 | Audit Logs | Xem lịch sử hoạt động của users |

## 2.4 Non-functional Requirements

### 2.4.1 Performance

| ID | Yêu cầu | Tiêu chuẩn |
|----|----------|-------------|
| NFR01 | Response Time | API response < 200ms (trừ test execution) |
| NFR02 | Concurrent Users | Hỗ trợ 50 concurrent users |
| NFR03 | Test Execution | Tối đa 5 tests đồng thời |
| NFR04 | Database Query | Single query < 100ms |

### 2.4.2 Security

| ID | Yêu cầu | Tiêu chuẩn |
|----|----------|-------------|
| NFR05 | Password Hashing | Sử dụng bcrypt |
| NFR06 | Token Algorithm | HS256 |
| NFR07 | Cookie Security | HttpOnly, SameSite=Lax |
| NFR08 | Rate Limiting | Giới hạn login attempts |

### 2.4.3 Usability

| ID | Yêu cầu | Tiêu chuẩn |
|----|----------|-------------|
| NFR09 | Responsive Design | Hỗ trợ desktop, tablet, mobile |
| NFR10 | Real-time Updates | Progress updates qua SSE |
| NFR11 | Error Messages | Thông báo lỗi rõ ràng, có hướng dẫn |

### 2.4.4 Reliability

| ID | Yêu cầu | Tiêu chuẩn |
|----|----------|-------------|
| NFR12 | Uptime | 99% uptime |
| NFR13 | Error Handling | Graceful error handling với try-catch |
| NFR14 | Logging | Ghi log cho tất cả operations |

## 2.5 User Stories

### 2.5.1 Authentication

| ID | User Story | Acceptance Criteria |
|----|------------|---------------------|
| US-001 | Là một người dùng mới, tôi muốn đăng ký tài khoản để sử dụng hệ thống | - Điền form đăng ký với email, username, password<br>- Hệ thống tạo tài khoản thành công<br>- Email và username phải unique |
| US-002 | Là một người dùng, tôi muốn đăng nhập để truy cập hệ thống | - Điền email/username và password<br>- Nhận JWT tokens<br>- Được chuyển hướng đến Dashboard |
| US-003 | Là một người dùng, tôi muốn đăng xuất để bảo mật tài khoản | - Tokens bị xóa<br>- Được chuyển hướng đến trang login |

### 2.5.2 Testing

| ID | User Story | Acceptance Criteria |
|----|------------|---------------------|
| US-010 | Là một người dùng, tôi muốn tạo bài test mới để kiểm tra website | - Nhập URL hợp lệ<br>- Chọn ít nhất 1 module<br>- Bài test được tạo và chạy background<br>- Được chuyển hướng đến trang kết quả |
| US-011 | Là một người dùng, tôi muốn xem tiến trình test để biết trạng thái | - Progress bar hiển thị % hoàn thành<br>- Module hiện tại được hiển thị<br>- Updates real-time qua SSE |
| US-012 | Là một người dùng, tôi muốn xem kết quả test chi tiết | - Hiển thị overall score<br>- Chi tiết từng module<br>- Danh sách issues và recommendations |

### 2.5.3 Reporting

| ID | User Story | Acceptance Criteria |
|----|------------|---------------------|
| US-020 | Là một người dùng, tôi muốn tải kết quả test để lưu trữ | - Tải được JSON, HTML, CSV<br>- File được định dạng đúng |
| US-021 | Là một người dùng, tôi muốn chia sẻ kết quả test | - Tạo được share link<br>- Link có thể set expiration<br>- Người khác xem được khi có link |

### 2.5.4 Analytics

| ID | User Story | Acceptance Criteria |
|----|------------|---------------------|
| US-030 | Là một người dùng, tôi muốn xem thống kê để đánh giá xu hướng | - Dashboard hiển thị total tests, avg score<br>- Biểu đồ score trend<br>- Module usage statistics |

## 2.6 Acceptance Criteria

### AC-001: Authentication

| Criteria | Mô tả | Test Case |
|----------|--------|-----------|
| AC-001.1 | User có thể đăng ký với thông tin hợp lệ | TC-001 |
| AC-001.2 | System từ chối email trùng lặp | TC-002 |
| AC-001.3 | System từ chối password yếu | TC-003 |
| AC-001.4 | User có thể đăng nhập thành công | TC-004 |
| AC-001.5 | System block IP sau 5 lần login thất bại | TC-005 |

### AC-002: Testing

| Criteria | Mô tả | Test Case |
|----------|--------|-----------|
| AC-002.1 | User có thể tạo test với URL và modules | TC-010 |
| AC-002.2 | System hiển thị progress real-time | TC-011 |
| AC-002.3 | Test hoàn thành và lưu kết quả | TC-012 |
| AC-002.4 | System hiển thị kết quả chi tiết | TC-013 |

### AC-003: Modules

| Criteria | Mô tả | Test Case |
|----------|--------|-----------|
| AC-003.1 | SEO module phát hiện missing meta tags | TC-020 |
| AC-003.2 | Performance module đo Core Web Vitals | TC-021 |
| AC-003.3 | Security module phát hiện XSS patterns | TC-022 |
| AC-003.4 | Accessibility module kiểm tra WCAG compliance | TC-023 |

## 2.7 As-Is Process

### Quy trình kiểm thử website hiện tại (Manual)

```
┌─────────────┐
│ 1. Xác định │
│    yêu cầu  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 2. Sử dụng  │────► Google PageSpeed Insights
│    công cụ  │────► GTmetrix
│    riêng lẻ │────► Lighthouse
│             │────► WAVE Accessibility
│             │────► SecurityHeaders.com
└──────┬──────┘────► Manual testing
       │
       ▼
┌─────────────┐
│ 3. Ghi nhận │
│    kết quả  │
│    thủ công │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 4. So sánh  │
│    kết quả  │
│    giữa các │
│    lần test │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 5. Xuất báo │
│    cáo thủ  │
│    công     │
└─────────────┘
```

**Nhược điểm:**
- Tốn thời gian (2-4 giờ/test)
- Không nhất quán giữa các công cụ
- Khó so sánh kết quả
- Thiếu dashboard tổng hợp

## 2.8 To-Be Process

### Quy trình kiểm thử website mới (WebTesterPro)

```
┌─────────────┐
│ 1. Đăng    │
│    nhập    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│ 2. Tạo Test                        │
│    - Nhập URL                      │
│    - Chọn modules                  │
│    - Thiết lập options             │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│ 3. Thực thi Test (Background)       │
│    - Playwright automation          │
│    - Real-time progress (SSE)       │
│    - Multiple modules parallel      │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│ 4. Xem Kết quả                      │
│    - Dashboard với scores           │
│    - Chi tiết từng module           │
│    - Issues và recommendations      │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│ 5. Báo cáo & Chia sẻ               │
│    - Export JSON/HTML/CSV           │
│    - Share link                     │
│    - Compare reports                │
│    - Analytics dashboard            │
└─────────────────────────────────────┘
```

**Ưu điểm:**
- Tự động hóa hoàn toàn
- Thời gian giảm 80%
- Dashboard trực quan
- So sánh dễ dàng

## 2.9 BPMN 2.0

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              BPMN: WebTesterPro Test Process                  │
└─────────────────────────────────────────────────────────────────────────────┘

[Start] ──► (Login Required)
                 │
                 ▼
         ┌───────────────┐
         │ Enter URL     │ ◄─────────────────────────┐
         └───────┬───────┘                           │
                 │                                   │
                 ▼                                   │
         ┌───────────────┐                           │
         │ Select Modules│                           │
         │ (At least 1)  │                           │
         └───────┬───────┘                           │
                 │                                   │
                 ▼                                   │
         ┌───────────────────┐     No      ┌─────────────────┐
         │ Validate URL     │───────────► │ Show Error       │
         └─────────┬────────┘             └─────────────────┘
                   │ Yes
                   ▼
         ┌───────────────────┐
         │ Create Test Record│
         └─────────┬─────────┘
                   │
                   ▼
         ┌───────────────────┐
         │ Run Modules       │
         │ (Background)     │
         └─────────┬─────────┘
                   │
                   ▼
         ┌───────────────────┐
         │ SSE: Progress    │◄──── Real-time Updates
         │ Updates (0-100%) │
         └─────────┬─────────┘
                   │
                   ▼
         ┌───────────────────┐
         │ Test Complete?    │
         └─────────┬─────────┘
                   │
          ┌────────┴────────┐
          │                  │
          ▼                  ▼
      ┌────────┐       ┌────────┐
      │ Success│       │ Failed │
      └───┬────┘       └───┬────┘
          │                │
          ▼                ▼
    ┌─────────────┐  ┌─────────────┐
    │ Save Report │  │ Log Error   │
    │ + Scores   │  │ + Status    │
    └──────┬─────┘  └─────────────┘
           │
           ▼
    ┌─────────────────┐
    │ View Results     │◄──── Dashboard
    │ + Download      │
    │ + Share         │
    └─────────────────┘
           │
           ▼
        [End]
```

---

# CHƯƠNG 3: PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG

## 3.1 Danh sách Use Case

| Mã UC | Tên Use Case | Actor | Độ ưu tiên |
|-------|-------------|-------|------------|
| UC-001 | Đăng ký tài khoản | Anonymous User | Cao |
| UC-002 | Đăng nhập | User | Cao |
| UC-003 | Đăng xuất | User | Cao |
| UC-004 | Xem Dashboard | User, Admin | Cao |
| UC-005 | Tạo test mới | User | Cao |
| UC-006 | Xem kết quả test | User | Cao |
| UC-007 | Theo dõi tiến trình test | User | Cao |
| UC-008 | Tải báo cáo | User | Trung bình |
| UC-009 | Chia sẻ báo cáo | User | Trung bình |
| UC-010 | So sánh báo cáo | User | Trung bình |
| UC-011 | Xem Analytics | User, Admin | Trung bình |
| UC-012 | Quản lý users | Admin | Thấp |
| UC-013 | Xem audit logs | Admin | Thấp |
| UC-014 | Xem shared report | Anonymous User | Cao |
| UC-015 | Refresh token | User | Cao |
| UC-016 | Chạy SEO Analysis | System | Cao |
| UC-017 | Chạy Performance Test | System | Cao |
| UC-018 | Chạy Security Scan | System | Cao |
| UC-019 | Chạy Accessibility Check | System | Cao |
| UC-020 | Chạy Crawler | System | Trung bình |
| UC-021 | Chạy Visual Test | System | Trung bình |
| UC-022 | Chạy Monitor | System | Trung bình |

## 3.2 Use Case Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Use Case Diagram: WebTesterPro                       │
└─────────────────────────────────────────────────────────────────────────────┘

                          ┌─────────────────────┐
                          │    <<system>>       │
                          │   WebTesterPro      │
                          └─────────────────────┘
                                        │
    ┌──────────────┐    ┌──────────────┐ │ ┌──────────────┐    ┌──────────────┐
    │   Anonymous  │    │    User      │ │ │    Admin     │   │    System     │
    │    User     │    │              │ │ │              │   │              │
    └──────┬───────┘    └──────┬───────┘ │ └──────┬───────┘   └──────┬───────┘
           │                   │          │        │                  │
           │ UC-001            │          │        │                  │
           ├───────────────────┤          │        │                  │
           │ UC-002            │          │        │                  │
           ├───────────────────┤          │        │                  │
           │ UC-003            │          │        │                  │
           ├───────────────────┤          │        │                  │
           │ UC-014            │          │        │                  │
           ├───────────────────┤          │        │                  │
           └─────────┬─────────┘          │        │                  │
                     │                    │        │                  │
                     ▼                    ▼        ▼                  ▼
           ┌─────────────────────────────────────────────────────────────────┐
           │                      Use Cases                                   │
           ├─────────────────────────────────────────────────────────────────┤
           │                                                                  │
           │  UC-001: Register ────► UC-002: Login ────► UC-003: Logout    │
           │                                                                  │
           │  UC-004: View Dashboard ────► UC-006: View Results               │
           │         │                         │                              │
           │         │                         ├────► UC-007: Track Progress │
           │         │                         │                              │
           │         │                         └────► UC-008: Download Report│
           │         │                                                       │
           │         ├────► UC-005: Create Test ────────────────────────    │
           │         │             │                                        │
           │         │             └────► UC-009: Share Report ────────┐     │
           │         │                                           │          │
           │         │                                           ▼          │
           │         │                               UC-010: Compare Reports │
           │         │                                                       │
           │         └────► UC-011: View Analytics                          │
           │                                                                     │
           │  UC-012: Manage Users ────► UC-013: View Audit Logs              │
           │                  │                                                 │
           │                  └────► UC-015: Refresh Token                    │
           │                                                                     │
           │  UC-016: Run SEO Analysis                                         │
           │  UC-017: Run Performance Test                                     │
           │  UC-018: Run Security Scan                                       │
           │  UC-019: Run Accessibility Check                                 │
           │  UC-020: Run Crawler                                             │
           │  UC-021: Run Visual Test                                         │
           │  UC-022: Run Monitor                                            │
           │                                                                     │
           └─────────────────────────────────────────────────────────────────┘
```

## 3.3 Đặc tả Use Case

### UC-001: Đăng ký tài khoản

| Thuộc tính | Nội dung |
|------------|----------|
| **Mã Use Case** | UC-001 |
| **Tên Use Case** | Đăng ký tài khoản (Register) |
| **Mục tiêu** | Cho phép người dùng tạo tài khoản mới để truy cập hệ thống |
| **Actor** | Anonymous User |
| **Trigger** | Người dùng nhấn "Register" trên trang đăng nhập |
| **Điều kiện tiên quyết** | Người dùng chưa có tài khoản |
| **Điều kiện kết thúc** | Tài khoản được tạo thành công hoặc hiển thị lỗi validation |
| **Luồng chính** | 1. User nhấn "Register"<br>2. Hệ thống hiển thị form đăng ký<br>3. User nhập email, username, password, confirm_password<br>4. Hệ thống validate dữ liệu<br>5. Hệ thống kiểm tra email/username unique<br>6. Hệ thống hash password và lưu user<br>7. Hệ thống chuyển hướng đến trang login với thông báo thành công |
| **Luồng thay thế** | A1: Email đã tồn tại → Hiển thị lỗi "Email đã được sử dụng"<br>A2: Username đã tồn tại → Hiển thị lỗi "Username đã được sử dụng"<br>A3: Password không khớp → Hiển thị lỗi "Mật khẩu xác nhận không khớp"<br>A4: Password yếu → Hiển thị lỗi validation |
| **Luồng ngoại lệ** | E1: Database error → Hiển thị "Đã xảy ra lỗi. Vui lòng thử lại sau." |
| **Input** | email, username, password, confirm_password |
| **Output** | User object, success/error message |
| **API liên quan** | POST /auth/register |
| **Bảng dữ liệu liên quan** | users |
| **Business Rule liên quan** | BR01, BR02, BR03, BR04 |

### UC-002: Đăng nhập

| Thuộc tính | Nội dung |
|------------|----------|
| **Mã Use Case** | UC-002 |
| **Tên Use Case** | Đăng nhập (Login) |
| **Mục tiêu** | Xác thực người dùng và cấp JWT tokens |
| **Actor** | User |
| **Trigger** | Người dùng nhấn "Login" |
| **Điều kiện tiên quyết** | Người dùng đã đăng ký tài khoản |
| **Điều kiện kết thúc** | User được xác thực và nhận tokens hoặc hiển thị lỗi |
| **Luồng chính** | 1. User nhấn "Login"<br>2. Hệ thống hiển thị form đăng nhập<br>3. User nhập email/username và password<br>4. Hệ thống kiểm tra rate limit<br>5. Hệ thống xác thực credentials<br>6. Hệ thống tạo access token (30 phút) và refresh token (7 ngày)<br>7. Hệ thống set cookies và chuyển hướng đến Dashboard |
| **Luồng thay thế** | A1: Invalid credentials → Ghi log thất bại, hiển thị lỗi<br>A2: Account disabled → Hiển thị "Tài khoản đã bị vô hiệu hóa"<br>A3: Rate limit exceeded → Hiển thị "Quá nhiều lần thử. Thử lại sau 15 phút." |
| **Luồng ngoại lệ** | E1: Token creation error → Hiển thị lỗi đăng nhập |
| **Input** | email/username, password |
| **Output** | JWT tokens, redirect to Dashboard |
| **API liên quan** | POST /auth/login, POST /login |
| **Bảng dữ liệu liên quan** | users, audit_logs |
| **Business Rule liên quan** | BR05, BR06 |

### UC-005: Tạo test mới

| Thuộc tính | Nội dung |
|------------|----------|
| **Mã Use Case** | UC-005 |
| **Tên Use Case** | Tạo test mới (Create Test) |
| **Mục tiêu** | Cho phép người dùng tạo bài kiểm thử website mới |
| **Actor** | User |
| **Trigger** | User nhấn "New Test" hoặc chọn module từ Dashboard |
| **Điều kiện tiên quyết** | User đã đăng nhập |
| **Điều kiện kết thúc** | Test được tạo, chạy background, user được chuyển đến trang kết quả |
| **Luồng chính** | 1. User nhấn "New Test"<br>2. Hệ thống hiển thị form tạo test<br>3. User nhập URL, chọn modules, thiết lập options<br>4. Hệ thống validate URL<br>5. Hệ thống kiểm tra ít nhất 1 module được chọn<br>6. Hệ thống tạo Report record với status="running"<br>7. Hệ thống chạy test trong background<br>8. Hệ thống chuyển hướng đến trang kết quả |
| **Luồng thay thế** | A1: Invalid URL → Hiển thị lỗi "URL không hợp lệ"<br>A2: No module selected → Hiển thị lỗi "Vui lòng chọn ít nhất một module" |
| **Luồng ngoại lệ** | E1: Background task error → Log lỗi, status="failed" |
| **Input** | url, modules[], max_depth, max_pages, viewport, monitor_duration |
| **Output** | Report object, redirect to results page |
| **API liên quan** | POST /test/new, GET /results/{report_id}/stream |
| **Bảng dữ liệu liên quan** | reports |
| **Business Rule liên quan** | BR07, BR08, BR09, BR10, BR11 |

### UC-006: Xem kết quả test

| Thuộc tính | Nội dung |
|------------|----------|
| **Mã Use Case** | UC-006 |
| **Tên Use Case** | Xem kết quả test (View Results) |
| **Mục tiêu** | Hiển thị chi tiết kết quả kiểm thử |
| **Actor** | User |
| **Trigger** | User nhấn vào test từ Dashboard hoặc History |
| **Điều kiện tiên quyết** | Test đã hoàn thành (status="completed") |
| **Điều kiện kết thúc** | Kết quả được hiển thị đầy đủ |
| **Luồng chính** | 1. User nhấn vào test<br>2. Hệ thống kiểm tra quyền truy cập (owner hoặc admin)<br>3. Hệ thống load kết quả từ DB hoặc JSON file<br>4. Hệ thống parse và tính toán scores<br>5. Hệ thống hiển thị Dashboard với scores và issues<br>6. User có thể xem chi tiết từng module |
| **Luồng thay thế** | A1: Test đang chạy → Hiển thị progress và auto-refresh<br>A2: Test thất bại → Hiển thị thông báo lỗi<br>A3: No permission → HTTP 403 |
| **Luồng ngoại lệ** | E1: Report not found → HTTP 404<br>E2: JSON parse error → Hiển thị raw data |
| **Input** | report_id |
| **Output** | HTML page với results, scores, issues |
| **API liên quan** | GET /results/{report_id}, GET /results/{report_id}/status |
| **Bảng dữ liệu liên quan** | reports |
| **Business Rule liên quan** | BR12, BR15, BR16, BR17, BR18, BR19 |

### UC-009: Chia sẻ báo cáo

| Thuộc tính | Nội dung |
|------------|----------|
| **Mã Use Case** | UC-009 |
| **Tên Use Case** | Chia sẻ báo cáo (Share Report) |
| **Mục tiêu** | Tạo link công khai để chia sẻ báo cáo |
| **Actor** | User |
| **Trigger** | User nhấn "Share" trên trang kết quả |
| **Điều kiện tiên quyết** | User sở hữu báo cáo |
| **Điều kiện kết thúc** | Share token được tạo, link được hiển thị |
| **Luồng chính** | 1. User nhấn "Share"<br>2. Hệ thống tạo secure token (32 bytes)<br>3. Hệ thống lưu ShareToken với expiration<br>4. Hệ thống trả về share URL<br>5. User có thể copy link |
| **Luồng thay thế** | A1: User hủy share → Không tạo token |
| **Luồng ngoại lệ** | E1: Token creation error → Hiển thị lỗi |
| **Input** | report_id, expires_days (optional, default 30) |
| **Output** | share_url, token, expires_days |
| **API liên quan** | POST /results/{report_id}/share, GET /share/{token} |
| **Bảng dữ liệu liên quan** | share_tokens, reports |
| **Business Rule liên quan** | BR13 |

### UC-010: So sánh báo cáo

| Thuộc tính | Nội dung |
|------------|----------|
| **Mã Use Case** | UC-010 |
| **Tên Use Case** | So sánh báo cáo (Compare Reports) |
| **Mục tiêu** | So sánh kết quả của 2 bài test |
| **Actor** | User |
| **Trigger** | User nhấn "Compare" từ Dashboard |
| **Điều kiện tiên quyết** | User có ít nhất 2 báo cáo |
| **Điều kiện kết thúc** | So sánh được hiển thị |
| **Luồng chính** | 1. User nhấn "Compare"<br>2. Hệ thống hiển thị form chọn 2 reports<br>3. User chọn 2 reports để so sánh<br>4. Hệ thống load dữ liệu cả 2 reports<br>5. Hệ thống tính toán differences<br>6. Hệ thống hiển thị side-by-side comparison |
| **Luồng thay thế** | A1: Chỉ 1 report → Disable compare button<br>A2: Reports khác domain → Warning message |
| **Luồng ngoại lệ** | E1: Report not found → HTTP 404 |
| **Input** | report1_id, report2_id |
| **Output** | Comparison data với scores, issues differences |
| **API liên quan** | GET /api/compare/{report1_id}/{report2_id} |
| **Bảng dữ liệu liên quan** | reports |
| **Business Rule liên quan** | BR12 |

## 3.4 Activity Diagram

### UC-005: Tạo test mới

```
┌──────────────┐
│   Bắt đầu   │
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│  Hiển thị form       │
│  tạo test           │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Nhập URL            │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐    No      ┌─────────────────┐
│  URL hợp lệ?         ├───────────►│ Hiển thị lỗi   │
└──────────┬───────────┘             └─────────────────┘
           │ Yes
           ▼
┌──────────────────────┐
│  Chọn modules        │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐    No      ┌─────────────────┐
│  Có ít nhất 1       ├───────────►│ Hiển thị lỗi   │
│  module?            │             └─────────────────┘
└──────────┬───────────┘
           │ Yes
           ▼
┌──────────────────────┐
│  Thiết lập options  │
│  (depth, pages...)  │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Tạo Report record   │
│  status="running"   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Chạy test           │
│  (Background Task)  │
└──────────┬───────────┘
           │
           ▼
    ┌──────┴──────┐
    │             │
    ▼             ▼
┌────────┐  ┌────────┐
│ Success│  │ Failed │
└───┬────┘  └───┬────┘
    │            │
    ▼            ▼
┌──────────────────────┐
│  Lưu kết quả        │
│  + Scores           │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Chuyển hướng đến   │
│  trang kết quả       │
└──────────┬───────────┘
           │
           ▼
┌──────────────┐
│    Kết thúc  │
└──────────────┘
```

### UC-002: Đăng nhập

```
┌──────────────┐
│   Bắt đầu   │
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│  Hiển thị form       │
│  đăng nhập          │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Nhập credentials    │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐    Yes     ┌─────────────────┐
│  Rate limit          ├───────────►│ Hiển thị lỗi   │
│  exceeded?           │             │ "Thử lại sau    │
└──────────┬───────────┘             │  15 phút"       │
           │ No                       └─────────────────┘
           ▼
┌──────────────────────┐    No      ┌─────────────────┐
│  Valid              ├───────────►│ Ghi log thất   │
│  credentials?        │             │ bại + Hiển thị │
└──────────┬───────────┘             │ lỗi            │
           │ Yes                      └─────────────────┘
           ▼
┌──────────────────────┐
│  Reset rate limit   │
│  counter            │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Cập nhật          │
│  last_login        │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Tạo JWT tokens    │
│  - Access (30m)    │
│  - Refresh (7d)     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Set HttpOnly       │
│  Cookies            │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Chuyển hướng       │
│  đến Dashboard      │
└──────────┬───────────┘
           │
           ▼
┌──────────────┐
│    Kết thúc  │
└──────────────┘
```

## 3.5 Sequence Diagram

### UC-005: Tạo test và theo dõi tiến trình

```
┌─────────┐     ┌────────────┐     ┌──────────────┐     ┌─────────────┐
│  User   │     │  Frontend  │     │   Backend    │     │   Database  │
└────┬────┘     └──────┬─────┘     └───────┬───────┘     └──────┬──────┘
     │                 │                    │                   │
     │  1. POST /test/new                   │                   │
     │────────────────►│                    │                   │
     │                 │                    │                   │
     │                 │  2. Validate URL   │                   │
     │                 │───────────────────►│                   │
     │                 │                    │                   │
     │                 │                    │  3. INSERT report │
     │                 │                    │──────────────────►│
     │                 │                    │                   │
     │                 │                    │  4. Return report │
     │                 │                    │◄──────────────────│
     │                 │                    │                   │
     │  5. Redirect    │                    │                   │
     │◄────────────────│                    │                   │
     │                 │                    │                   │
     │  6. GET /results/{id}/stream        │                   │
     │────────────────────────────────────►│                   │
     │                 │                    │                   │
     │                 │                    │  7. Subscribe SSE │
     │                 │                    │──────────────────►│
     │                 │                    │                   │
     │  8. SSE: progress updates           │                   │
     │◄────────────────────────────────────│                   │
     │                 │                    │                   │
     │                 │                    │  9. Background Task│
     │                 │                    │──────────────────►│
     │                 │                    │                   │
     │                 │                    │  10. Update report│
     │                 │                    │   (progress)      │
     │                 │                    │──────────────────►│
     │                 │                    │                   │
     │                 │                    │  11. Queue SSE    │
     │                 │                    │   event           │
     │                 │                    │                   │
     │  12. SSE: complete                   │                   │
     │◄────────────────────────────────────│                   │
     │                 │                    │                   │
     │  13. GET /results/{id}              │                   │
     │────────────────────────────────────►│                   │
     │                 │                    │                   │
     │                 │                    │  14. SELECT report│
     │                 │                    │──────────────────►│
     │                 │                    │                   │
     │                 │                    │  15. Return data  │
     │                 │                    │◄──────────────────│
     │                 │                    │                   │
     │  16. Display results HTML            │                   │
     │◄─────────────────────────────────────│                   │
     │                 │                    │                   │
```

## 3.6 Class Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Class Diagram: WebTesterPro                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────┐         ┌─────────────────────────┐
│         User             │         │        Report            │
├─────────────────────────┤         ├─────────────────────────┤
│ - id: int               │         │ - id: int               │
│ - email: str           │         │ - user_id: int          │
│ - username: str        │         │ - title: str           │
│ - hashed_password: str │1    *   │ - url: str              │
│ - is_active: bool     ├─────────┤ - file_path: str       │
│ - is_admin: bool       │         │ - json_path: str        │
│ - created_at: datetime  │         │ - overall_score: int   │
│ - last_login: datetime  │         │ - summary: str         │
├─────────────────────────┤         │ - status: str           │
│ + create_user()         │         │ - modules_run: str     │
│ + get_user_by_id()      │         │ - results_json: str   │
│ + get_user_by_email()   │         │ - progress: int        │
│ + get_user_by_username()│         │ - current_module: str  │
│ + update_last_login()   │         │ - created_at: datetime │
└─────────────────────────┘         ├─────────────────────────┤
                                    │ + create_report()        │
                                    │ + get_reports_by_user()  │
                                    │ + get_report_by_id()     │
                                    │ + update_report()        │
                                    └───────────┬─────────────┘
                                                │
                                                │
                                    ┌───────────┴─────────────┐
                                    │                         │
                                    ▼                         ▼
┌─────────────────────────┐   ┌─────────────────────────┐   ┌─────────────────────────┐
│     AuditLog            │   │    ScheduledTest         │   │     ShareToken          │
├─────────────────────────┤   ├─────────────────────────┤   ├─────────────────────────┤
│ - id: int               │   │ - id: int               │   │ - id: int               │
│ - user_id: int         │   │ - user_id: int         │   │ - report_id: int        │
│ - action: str           │   │ - name: str            │   │ - token: str            │
│ - resource_type: str    │   │ - url: str             │   │ - expires_at: datetime  │
│ - resource_id: int       │   │ - modules: str         │   │ - view_count: int       │
│ - details: str           │   │ - cron_expression: str │   │ - created_by: int        │
│ - ip_address: str        │   │ - is_active: bool     │   │ - created_at: datetime   │
│ - user_agent: str        │   │ - last_run: datetime   │   └─────────────────────────┘
│ - created_at: datetime    │   │ - next_run: datetime   │
└─────────────────────────┘   │ - created_at: datetime  │
                                └─────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                         Testing Modules (Engine)                             │
└─────────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────────────────┐
                              │   WebTesterEngine        │
                              ├─────────────────────────┤
                              │ - config: Config         │
                              │ - crawler: WebsiteCrawler │
                              │ - scanner: WebsiteScanner │
                              │ - analyzer: WebsiteAnalyzer│
                              │ - monitor: WebsiteMonitor │
                              │ - performance: PerformanceTester│
                              │ - security: SecurityScanner│
                              │ - accessibility: AccessibilityChecker│
                              │ - seo: SEOAnalyzer        │
                              │ - visual: VisualTester    │
                              │ - reporter: ReportGenerator│
                              ├─────────────────────────┤
                              │ + start()               │
                              │ + stop()                │
                              │ + crawl_site()          │
                              │ + scan_site()           │
                              │ + analyze_site()        │
                              │ + monitor_site()        │
                              │ + test_performance()    │
                              │ + scan_security()        │
                              │ + check_accessibility()  │
                              │ + analyze_seo()          │
                              │ + capture_screenshot()   │
                              └─────────────────────────┘
                                              │
        ┌─────────────┬─────────────┬─────────┴────────┬─────────────┐
        │             │             │                  │             │
        ▼             ▼             ▼                  ▼             ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│SEOAnalyzer   │ │Performance   │ │Security      │ │Accessibility │ │VisualTester  │
│              │ │Tester        │ │Scanner       │ │Checker       │ │              │
├──────────────┤ ├──────────────┤ ├──────────────┤ ├──────────────┤ ├──────────────┤
│+analyze()   │ │+test_perf()  │ │+scan()       │ │+check()      │ │+screenshot() │
│+quick_analyze│ │+compare_urls│ │+quick_scan() │ │+quick_check()│ │              │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

## 3.7 State Diagram

### Report State Machine

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        State Diagram: Report Status                        │
└─────────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────────────────────────────┐
                    │                                             │
                    │                                             │
                    ▼                                             │
            ┌───────────────┐                                    │
            │   pending     │                                    │
            └───────┬───────┘                                    │
                    │                                            │
                    │ create_report()                            │
                    │                                            │
                    ▼                                            │
            ┌───────────────┐                                    │
     ┌──────│    running    │◄─────────────────────────────┐    │
     │      └───────┬───────┘                              │    │
     │              │                                       │    │
     │              │ Background task running               │    │
     │              │ Progress updates (0-95%)              │    │
     │              │                                       │    │
     │              │ Module execution:                     │    │
     │              │ - crawler                            │    │
     │              │ - scanner                            │    │
     │              │ - seo                                │    │
     │              │ - performance                         │    │
     │              │ - security                           │    │
     │              │ - accessibility                       │    │
     │              │ - visual                             │    │
     │              │ - monitor                            │    │
     │              │                                       │    │
     │              └─────────────────┬─────────────────────┘    │
     │                                │                         │
     │              ┌─────────────────┴─────────────────┐        │
     │              │                                   │        │
     │              │                                   │        │
     │              ▼                                   ▼        │
     │      ┌───────────────┐                   ┌───────────────┐
     │      │  completed    │                   │    failed     │
     │      └───────────────┘                   └───────────────┘
     │              │
     │              │ User actions:
     │              │ - View results
     │              │ - Download
     │              │ - Share
     │              │ - Compare
     │              │
     │              └─────────────────┐
     │                                  │
     │                                  │ Admin action:
     │                                  │ - Delete
     │                                  │
     │                                  ▼
     │                          ┌───────────────┐
     │                          │   deleted     │
     │                          └───────────────┘
     │
     │ Timeout (>10 minutes)
     │
     └─────────────────────────────►
```

## 3.8 Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Component Diagram: WebTesterPro                           │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              Client (Browser)                              │
│  ┌─────────────────────────────────────────────────────────────────────┐     │
│  │  Web Browser                                                        │     │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐               │     │
│  │  │  HTML/CSS   │  │ JavaScript  │  │  SSE Client │               │     │
│  │  │  Templates   │  │  (Vanilla)  │  │             │               │     │
│  │  └─────────────┘  └─────────────┘  └─────────────┘               │     │
│  └─────────────────────────────────────────────────────────────────────┘     │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │ HTTP/HTTPS
                                 │ Templates
                                 │ SSE
┌────────────────────────────────▼────────────────────────────────────────────┐
│                              Backend (FastAPI)                              │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                        Dashboard Module                               │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐ │ │
│  │  │  Pages      │  │  Services   │  │   Utils     │  │ Deps      │ │ │
│  │  │  Router    │  │  - TestRunner│  │ - ResultsParser│ │ - Auth    │ │ │
│  │  │  (main.py) │  │  - AuditSvc │  │             │  │ - UserDep │ │ │
│  │  │            │  │  - ExportSvc│  │             │  │ - AdminDep│ │ │
│  │  │            │  │  - CompareSvc│  │             │  │           │ │ │
│  │  │            │  │  - AnalyticsSvc│ │             │  │           │ │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └───────────┘ │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                     Authentication Module                             │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  │ │
│  │  │   Router    │  │    Auth     │  │    CRUD     │                  │ │
│  │  │ /auth/*    │  │ - JWT       │  │ - get_user  │                  │ │
│  │  │            │  │ - bcrypt    │  │ - create_usr│                  │ │
│  │  │            │  │ - RateLimit │  │ - get_report│                  │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                  │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                    WebTesterEngine (Core)                             │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐               │ │
│  │  │  SEO     │ │Performance│ │ Security │ │Accessibil│               │ │
│  │  │ Analyzer │ │ Tester   │ │ Scanner  │ │   ity    │               │ │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘               │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐               │ │
│  │  │ Crawler  │ │ Scanner  │ │ Visual   │ │ Monitor  │               │ │
│  │  │          │ │          │ │ Tester   │ │          │               │ │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘               │ │
│  │                          ┌──────────┐                                  │ │
│  │                          │ Report   │                                  │ │
│  │                          │Generator │                                  │ │
│  │                          └──────────┘                                  │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 │ SQLAlchemy ORM
                                 │
┌────────────────────────────────▼────────────────────────────────────────────┐
│                            Database Layer                                    │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                           SQLite                                        │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │ │
│  │  │   users    │  │  reports   │  │ audit_logs │  │share_tokens│ │ │
│  │  │            │  │            │  │             │  │            │ │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │ │
│  │  ┌─────────────┐                                                        │ │
│  │  │scheduled_  │                                                        │ │
│  │  │  tests     │                                                        │ │
│  │  └─────────────┘                                                        │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                        File System                                      │ │
│  │  ┌─────────────────────────────┐  ┌─────────────────────────────┐     │ │
│  │  │  reports/                  │  │  data/                        │     │ │
│  │  │  ├── dashboard/*.json      │  │  └── webtesterpro.db         │     │ │
│  │  │  ├── dashboard/*.html      │  │                              │     │ │
│  │  │  └── history.json          │  └─────────────────────────────┘     │ │
│  │  └─────────────────────────────┘                                     │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 3.9 Package Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Package Diagram: WebTesterPro                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                            webtesterpro                                   │
│                          (Root Package)                                    │
│                                                                             │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐               │
│  │    database     │ │    core         │ │    models       │               │
│  ├─────────────────┤ ├─────────────────┤ ├─────────────────┤               │
│  │ + Base          │ │ + Config        │ │ + User          │               │
│  │ + engine        │ │ + WebTesterEngine│ │                 │               │
│  │ + SessionLocal │ │                 │ │                 │               │
│  │ + get_db()    │ │                 │ │                 │               │
│  │ + init_db()   │ │                 │ │                 │               │
│  └────────┬────────┘ └────────┬────────┘ └─────────────────┘               │
│           │                   │                                             │
│           │                   │                                             │
│           ▼                   ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                            auth                                       │ │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────┐ │ │
│  │  │    models    │ │     auth      │ │    router     │ │   schemas   │ │ │
│  │  │  - User      │ │  - JWT       │ │  /auth/*     │ │  - UserCreate│ │ │
│  │  │  - Report    │ │  - bcrypt    │ │  /auth/login  │ │  - UserLogin │ │ │
│  │  │  - AuditLog  │ │  - RateLimit │ │  /auth/register│ │  - Token     │ │ │
│  │  │  - ShareToken│ │              │ │  /auth/me     │ │  - ReportCreate│ │ │
│  │  │  - ScheduledTest│ │           │ │              │ │             │ │ │
│  │  └──────────────┘ └──────────────┘ └──────────────┘ └────────────┘ │ │
│  │  ┌──────────────┐ ┌──────────────┐                                  │ │
│  │  │    crud     │ │ dependencies  │                                  │ │
│  │  │  - get_user │ │  - get_current_user │                             │ │
│  │  │  - create_user│ │  - get_current_admin │                           │ │
│  │  │  - get_report │ │  - get_optional_user │                           │ │
│  │  │  - create_report│ │              │                                  │ │
│  │  └──────────────┘ └──────────────┘                                  │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                          dashboard                                    │ │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────┐ │ │
│  │  │    main      │ │  constants   │ │dependencies  │ │  services   │ │ │
│  │  │  /dashboard  │ │  - MODULES  │ │              │ │  - TestRunner│ │ │
│  │  │  /test/*    │ │  - VIEWPORTS │ │              │ │  - AuditSvc │ │ │
│  │  │  /results/* │ │              │ │              │ │  - ExportSvc │ │ │
│  │  │  /history   │ │              │ │              │ │  - CompareSvc │ │ │
│  │  │  /analytics │ │              │ │              │ │  - AnalyticsSvc│ │ │
│  │  │  /compare   │ │              │ │              │ │  - SSEManager│ │ │
│  │  └──────────────┘ └──────────────┘ └──────────────┘ └────────────┘ │ │
│  │  ┌──────────────┐ ┌──────────────┐                                  │ │
│  │  │   templates  │ │    static     │                                  │ │
│  │  │  - base.html│ │  - manifest.json│                                 │ │
│  │  │  - index.html│ │  - sw.js      │                                 │ │
│  │  │  - login.html│ │  - js/        │                                 │ │
│  │  │  - results.html│ │    - toast.js│                                 │ │
│  │  │  - history.html│ │    - shortcuts│ │                                │ │
│  │  │  - analytics.html│ │    - tour.js│ │                                │ │
│  │  └──────────────┘ └──────────────┘                                  │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                           modules                                    │ │
│  │  ┌─────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────┐ │ │
│  │  │  seo    │ │performance│ │ security │ │accessibility│ │ crawler │ │ │
│  │  │-Analyzer│ │ - Tester │ │ -Scanner │ │ - Checker │ │ -Crawler│ │ │
│  │  └─────────┘ └──────────┘ └──────────┘ └──────────┘ └─────────┘ │ │
│  │  ┌─────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐               │ │
│  │  │ scanner │ │ visual   │ │ monitor  │ │ reporting│               │ │
│  │  │ -Scanner│ │ -Tester  │ │ -Monitor │ │ -Generator│               │ │
│  │  └─────────┘ └──────────┘ └──────────┘ └──────────┘               │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                            tests                                     │ │
│  │  ┌──────────────┐ ┌──────────────┐                                 │ │
│  │  │    unit      │ │  integration │                                 │ │
│  │  │ - test_seo   │ │              │                                 │ │
│  │  │ - test_performance │ │        │                                 │ │
│  │  │ - test_security │ │            │                                 │ │
│  │  │ - test_accessibility │ │        │                                 │ │
│  │  │ - test_crawler │ │            │                                 │ │
│  │  │ - test_visual  │ │            │                                 │ │
│  │  │ - test_reporting│ │           │                                 │ │
│  │  │ - test_config  │ │           │                                 │ │
│  │  └──────────────┘ └──────────────┘                                 │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 3.10 Deployment Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      Deployment Diagram: WebTesterPro                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              Development Environment                        │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                        Developer's Machine                             │ │
│  │                                                                        │ │
│  │   ┌────────────────────────────────────────────────────────────────┐  │ │
│  │   │                    Container: Python Application                 │  │ │
│  │   │                                                                    │  │ │
│  │   │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │  │ │
│  │   │   │   FastAPI     │  │   Playwright  │  │   SQLite     │        │  │ │
│  │   │   │   (Uvicorn)   │  │   (Browser)   │  │   Database   │        │  │ │
│  │   │   │               │  │              │  │              │        │  │ │
│  │   │   │  ┌──────────┐  │  │  ┌────────┐  │  │              │        │  │ │
│  │   │   │  │  Routes  │  │  │  │Chromium│  │  │              │        │  │ │
│  │   │   │  └──────────┘  │  │  └────────┘  │  │              │        │  │ │
│  │   │   │  ┌──────────┐  │  │              │  │              │        │  │ │
│  │   │   │  │  Services │  │  │              │  │              │        │  │ │
│  │   │   │  └──────────┘  │  │              │  │              │        │  │ │
│  │   │   │  ┌──────────┐  │  │              │  │              │        │  │ │
│  │   │   │  │   ORM    │  │  │              │  │              │        │  │ │
│  │   │   │  └──────────┘  │  │              │  │              │        │  │ │
│  │   │   └──────────────┘  └──────────────┘  └──────────────┘        │  │ │
│  │   │                                                                    │  │ │
│  │   │   ┌────────────────────────────────────────────────────────────┐  │  │ │
│  │   │   │              Client Browser                               │  │  │ │
│  │   │   │   ┌────────────┐  ┌────────────┐  ┌────────────┐         │  │  │ │
│  │   │   │   │   Chrome   │  │   Firefox │  │   Safari   │         │  │  │ │
│  │   │   │   └────────────┘  └────────────┘  └────────────┘         │  │  │ │
│  │   │   └────────────────────────────────────────────────────────────┘  │  │ │
│  │   └────────────────────────────────────────────────────────────────┘  │  │
│  │                                                                        │  │
│  │   ┌────────────────────────────────────────────────────────────────────┐ │  │
│  │   │                        File System                                 │ │  │
│  │   │   ┌────────────────┐  ┌────────────────┐  ┌────────────────┐       │ │  │
│  │   │   │  reports/      │  │  data/         │  │  logs/         │       │ │  │
│  │   │   │  ├── *.json    │  │  ├── *.db       │  │  ├── *.log     │       │ │  │
│  │   │   │  └── *.html    │  │  └── *.db-journal│ │  └── *.log.1   │       │ │  │
│  │   │   └────────────────┘  └────────────────┘  └────────────────┘       │ │  │
│  │   └────────────────────────────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                           │
                                           │ HTTP/WS
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Production Environment                         │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                         Load Balancer                                  │ │
│  │                         (Nginx)                                        │ │
│  │                                                                          │ │
│  │   ┌────────────────┐  ┌────────────────┐  ┌────────────────┐            │ │
│  │   │   Instance 1   │  │   Instance 2   │  │   Instance N   │            │ │
│  │   │   (App Server) │  │   (App Server) │  │   (App Server) │            │ │
│  │   └───────┬────────┘  └───────┬────────┘  └───────┬────────┘            │ │
│  └───────────┼───────────────────┼───────────────────┼───────────────────────┘ │
│              │                   │                   │                        │
│              │                   │                   │                        │
│              ▼                   ▼                   ▼                        │
│  ┌───────────────────────────────────────────────────────────────────────┐    │
│  │                      Application Servers                             │    │
│  │                                                                        │    │
│  │   ┌───────────────────────────────────────────────────────────────┐    │    │
│  │   │                    Container: Python/FastAPI                   │    │    │
│  │   │                                                                     │    │    │
│  │   │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │    │    │
│  │   │   │   FastAPI     │  │   Playwright  │  │   Gunicorn   │         │    │    │
│  │   │   │   (ASGI)     │  │   (Headless)  │  │   (Workers)  │         │    │    │
│  │   │   │              │  │              │  │              │         │    │    │
│  │   │   │  ┌────────┐  │  │  ┌────────┐  │  │              │         │    │    │
│  │   │   │  │ Routes │  │  │  │Chromium│  │  │              │         │    │    │
│  │   │   │  └────────┘  │  │  └────────┘  │  │              │         │    │    │
│  │   │   │  ┌────────┐  │  │              │  │              │         │    │    │
│  │   │   │  │ Services│  │  │              │  │              │         │    │    │
│  │   │   │  └────────┘  │  │              │  │              │         │    │    │
│  │   │   └──────────────┘  └──────────────┘  └──────────────┘         │    │    │
│  │   └───────────────────────────────────────────────────────────────┘    │    │
│  └───────────────────────────────────────────────────────────────────────┘    │
│                                           │                                │
│                                           │                                │
│                                           ▼                                │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                        PostgreSQL Server                               │ │
│  │                         (Remote Database)                              │ │
│  │                                                                          │ │
│  │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │ │
│  │   │   Primary     │  │    Replica    │  │   Replica     │               │ │
│  │   │   (Write)     │  │    (Read)      │  │    (Read)      │               │ │
│  │   └──────────────┘  └──────────────┘  └──────────────┘               │ │
│  │                                                                          │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                          File Storage (S3)                             │ │
│  │   ┌────────────────┐  ┌────────────────┐  ┌────────────────┐            │ │
│  │   │  reports/      │  │  screenshots/  │  │  logs/         │            │ │
│  │   └────────────────┘  └────────────────┘  └────────────────┘            │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

# CHƯƠNG 4: KIẾN TRÚC HỆ THỐNG

## 4.1 Context Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Context Diagram: WebTesterPro                         │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                              WebTesterPro System                            │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                                                                        │ │
│  │   ┌─────────────────────────────────────────────────────────────┐    │ │
│  │   │                                                              │    │ │
│  │   │                      WebTesterPro                            │    │ │
│  │   │                      Dashboard                                │    │ │
│  │   │                                                              │    │ │
│  │   │   ┌─────────────────────────────────────────────────────┐  │    │ │
│  │   │   │                                                     │  │    │ │
│  │   │   │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ │  │    │ │
│  │   │   │  │   SEO   │ │ Perf-   │ │ Security│ │ Access- │ │  │    │ │
│  │   │   │  │Analysis │ │formance │ │ Scan   │ │ibility  │ │  │    │ │
│  │   │   │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ │  │    │ │
│  │   │   │                                                     │  │    │ │
│  │   │   │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ │  │    │ │
│  │   │   │  │ Crawler │ │ Visual  │ │ Monitor │ │ Scanner │ │  │    │ │
│  │   │   │  │         │ │ Testing │ │         │ │         │ │  │    │ │
│  │   │   │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ │  │    │ │
│  │   │   │                                                     │  │    │ │
│  │   │   └─────────────────────────────────────────────────────┘  │    │ │
│  │   │                                                              │    │ │
│  │   └─────────────────────────────────────────────────────────────┘    │ │
│  │                                                                        │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
        │                          │                          │
        │                          │                          │
        │                          │                          │
        ▼                          ▼                          ▼
┌──────────────┐        ┌──────────────┐        ┌──────────────┐
│    User      │        │  Target      │        │   External   │
│  (Actor)    │        │  Website     │        │   Services    │
│              │        │  (Being      │        │              │
│ - Register  │        │   Tested)   │        │ - Playwright │
│ - Login     │        │              │        │ - Google Fonts│
│ - Create    │        │              │        │ - CDN        │
│   Test      │        │              │        │              │
│ - View      │        │              │        │              │
│   Results   │        │              │        │              │
│ - Download  │        │              │        │              │
│ - Share     │        │              │        │              │
│ - Compare   │        │              │        │              │
└──────────────┘        └──────────────┘        └──────────────┘
```

## 4.2 C4 Model

### Level 1: Context (System Context)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        C4 Model Level 1: Context                           │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│    ┌──────────────────────────────────────────────────────────────────────┐  │
│    │                                                                      │  │
│    │                    WebTesterPro System                              │  │
│    │                    (Web Application)                                 │  │
│    │                                                                      │  │
│    │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │  │
│    │   │   Website    │  │    Test      │  │   Report     │            │  │
│    │   │   Testing    │  │   Results    │  │   Export     │            │  │
│    │   │   Engine     │  │   Dashboard  │  │              │            │  │
│    │   └──────────────┘  └──────────────┘  └──────────────┘            │  │
│    │                                                                      │  │
│    └──────────────────────────────────────────────────────────────────────┘  │
│                                    │                                        │
│              ┌─────────────────────┼─────────────────────┐                │
│              │                     │                     │                │
│              ▼                     ▼                     ▼                │
│    ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐     │
│    │    Website       │  │    User          │  │   Admin         │     │
│    │    Owners        │  │    (Tester)      │  │   Users         │     │
│    │                  │  │                  │  │                  │     │
│    │ - QA Engineers  │  │ - Developers    │  │ - System Admin  │     │
│    │ - DevOps        │  │ - PM            │  │ - IT Admin      │     │
│    │ - Marketing     │  │ - Stakeholders  │  │                  │     │
│    └──────────────────┘  └──────────────────┘  └──────────────────┘     │
│                                                                             │
│                              External Systems                               │
│    ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐     │
│    │   Target         │  │   Google        │  │   DNS           │     │
│    │   Websites       │  │   Search        │  │   Servers       │     │
│    │                  │  │                  │  │                  │     │
│    │ - Any website   │  │ - SEO indexing  │  │ - Domain lookup│     │
│    │   to be tested  │  │                  │  │                  │     │
│    └──────────────────┘  └──────────────────┘  └──────────────────┘     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Level 2: Container

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       C4 Model Level 2: Container                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                           WebTesterPro                                      │
│                           (Web Application)                                 │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                         Web Browser                                   │ │
│  │  ┌────────────────────────────────────────────────────────────────┐  │ │
│  │  │                      Single Page Application                    │  │ │
│  │  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐   │  │ │
│  │  │  │  Dashboard │ │   Results   │ │  Analytics │ │   Admin    │   │  │ │
│  │  │  │   Page     │ │    Page     │ │    Page    │ │   Page     │   │  │ │
│  │  │  └────────────┘ └────────────┘ └────────────┘ └────────────┘   │  │ │
│  │  │                                                               │  │ │
│  │  │  ┌──────────────────────────────────────────────────────┐   │  │ │
│  │  │  │              JavaScript (Vanilla JS)                   │   │  │ │
│  │  │  │  - SSE Client    - Form Handler    - Toast Notifications │   │  │ │
│  │  │  │  - API Client   - URL Validator   - Keyboard Shortcuts    │   │  │ │
│  │  │  └──────────────────────────────────────────────────────┘   │  │ │
│  │  └────────────────────────────────────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                     │                                       │
│                                     │ HTTP/REST + SSE                       │
│                                     ▼                                       │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                    FastAPI Application (Python)                        │ │
│  │                                                                        │ │
│  │   ┌─────────────────────────────────────────────────────────────────┐ │ │
│  │   │                      API Layer (Routes)                           │ │ │
│  │   │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │ │ │
│  │   │  │   Auth   │ │  Tests   │ │ Reports  │ │  Admin   │          │ │ │
│  │   │  │  Routes  │ │  Routes  │ │  Routes  │ │  Routes  │          │ │ │
│  │   │  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │ │ │
│  │   └─────────────────────────────────────────────────────────────────┘ │ │
│  │                                                                        │ │
│  │   ┌─────────────────────────────────────────────────────────────────┐ │ │
│  │   │                    Service Layer                                 │ │ │
│  │   │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐   │ │ │
│  │   │  │TestRunner │ │   Audit   │ │  Export   │ │  Analytics │   │ │ │
│  │   │  │  Service   │ │  Service  │ │  Service  │ │  Service   │   │ │ │
│  │   │  └────────────┘ └────────────┘ └────────────┘ └────────────┘   │ │ │
│  │   │  ┌────────────┐ ┌────────────┐ ┌────────────┐                   │ │ │
│  │   │  │  Compare  │ │    SSE    │ │   User    │                   │ │ │
│  │   │  │  Service  │ │  Manager  │ │  Service  │                   │ │ │
│  │   │  └────────────┘ └────────────┘ └────────────┘                   │ │ │
│  │   └─────────────────────────────────────────────────────────────────┘ │ │
│  │                                                                        │ │
│  │   ┌─────────────────────────────────────────────────────────────────┐ │ │
│  │   │                   WebTesterEngine (Core)                        │ │ │
│  │   │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │ │ │
│  │   │  │   SEO    │ │Perf-     │ │ Security │ │Access-   │          │ │ │
│  │   │  │ Analyzer │ │formance  │ │ Scanner  │ │ibility   │          │ │ │
│  │   │  │          │ │ Tester   │ │          │ │ Checker  │          │ │ │
│  │   │  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │ │ │
│  │   │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │ │ │
│  │   │  │ Crawler  │ │  Visual  │ │ Monitor  │ │ Reporter │          │ │ │
│  │   │  │          │ │  Tester  │ │          │ │          │          │ │ │
│  │   │  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │ │ │
│  │   └─────────────────────────────────────────────────────────────────┘ │ │
│  │                                                                        │ │
│  │   ┌─────────────────────────────────────────────────────────────────┐ │ │
│  │   │                  Authentication (JWT + bcrypt)                    │ │ │
│  │   └─────────────────────────────────────────────────────────────────┘ │ │
│  │                                                                        │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                     │                                       │
│                                     │ SQLAlchemy ORM                       │
│                                     ▼                                       │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                           SQLite Database                             │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │ │
│  │  │  users  │ │ reports │ │ audit_  │ │  share_ │ │scheduled│   │ │
│  │  │          │ │          │ │  logs   │ │  tokens │ │ _tests  │   │ │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘   │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                          File System                                   │ │
│  │  ┌────────────────────┐  ┌────────────────────┐  ┌────────────────┐   │ │
│  │  │  reports/         │  │  data/              │  │  logs/         │   │ │
│  │  │  ├── *.json       │  │  ├── webtesterpro.db │  │  └── *.log     │   │ │
│  │  │  └── *.html       │  │                     │  │                 │   │ │
│  │  └────────────────────┘  └────────────────────┘  └────────────────┘   │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Level 3: Component

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    C4 Model Level 3: Component (Testing Engine)              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                           WebTesterEngine                                   │
│                          (Testing Engine)                                  │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                    Playwright Browser Instance                          │ │
│  │                                                                        │ │
│  │   ┌─────────────────────────────────────────────────────────────────┐ │ │
│  │   │                      Browser Context                             │ │ │
│  │   │                                                                     │ │ │
│  │   │   ┌─────────────────────────────────────────────────────────┐   │ │ │
│  │   │   │                    Page Instance                         │   │ │ │
│  │   │   │                                                               │   │ │ │
│  │   │   │   ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  │   │ │ │
│  │   │   │   │   HTML        │  │   Network     │  │   JavaScript  │  │   │ │ │
│  │   │   │   │   DOM         │  │   Requests    │  │   Runtime     │  │   │ │ │
│  │   │   │   └───────────────┘  └───────────────┘  └───────────────┘  │   │ │ │
│  │   │   │                                                               │   │ │ │
│  │   │   └─────────────────────────────────────────────────────────┘   │ │ │
│  │   │                                                                     │ │ │
│  │   └─────────────────────────────────────────────────────────────────┘ │ │
│  │                                                                        │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                       Testing Modules                                  │ │
│  │                                                                        │ │
│  │   ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐       │ │
│  │   │    SEO         │  │   Performance    │  │    Security     │       │ │
│  │   │   Analyzer     │  │    Tester       │  │     Scanner     │       │ │
│  │   ├─────────────────┤  ├─────────────────┤  ├─────────────────┤       │ │
│  │   │ +analyze()     │  │ +test_perf()    │  │ +scan()         │       │ │
│  │   │ -Title Check   │  │ -CoreWebVitals  │  │ -Headers Check  │       │ │
│  │   │ -Meta Check    │  │ -Load Time      │  │ -XSS Detect    │       │ │
│  │   │ -Heading Check │  │ -Resource Size  │  │ -SQLi Detect   │       │ │
│  │   │ -OG Tags       │  │ -TTFB          │  │ -File Expose  │       │ │
│  │   │ -Schema.org    │  │                 │  │                 │       │ │
│  │   │ -Image Alt     │  │                 │  │                 │       │ │
│  │   │ -Link Analyze  │  │                 │  │                 │       │ │
│  │   └─────────────────┘  └─────────────────┘  └─────────────────┘       │ │
│  │                                                                        │ │
│  │   ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐       │ │
│  │   │  Accessibility  │  │    Crawler      │  │    Visual       │       │ │
│  │   │    Checker      │  │                 │  │    Tester       │       │ │
│  │   ├─────────────────┤  ├─────────────────┤  ├─────────────────┤       │ │
│  │   │ +check()        │  │ +crawl()        │  │ +screenshot()   │       │ │
│  │   │ -axe-core       │  │ -Depth Crawl    │  │ -Multi-viewport│       │ │
│  │   │ -WCAG 2.1       │  │ -robots.txt     │  │ -Full Page     │       │ │
│  │   │ -Color Contrast │  │ -URL Filtering  │  │ -Comparison    │       │ │
│  │   │ -Alt Text       │  │ -Rate Limiting │  │                 │       │ │
│  │   │ -ARIA Labels    │  │ -Login Support │  │                 │       │ │
│  │   └─────────────────┘  └─────────────────┘  └─────────────────┘       │ │
│  │                                                                        │ │
│  │   ┌─────────────────┐  ┌─────────────────┐                            │ │
│  │   │    Monitor      │  │   Reporter      │                            │ │
│  │   ├─────────────────┤  ├─────────────────┤                            │ │
│  │   │ +monitor()      │  │ +generate()     │                            │ │
│  │   │ -Uptime Check  │  │ -HTML Report    │                            │ │
│  │   │ -Response Time │  │ -JSON Export    │                            │ │
│  │   │ -Alerting      │  │ -Dashboard      │                            │ │
│  │   └─────────────────┘  └─────────────────┘                            │ │
│  │                                                                        │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 4.3 Client-Server Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   Client-Server Architecture: WebTesterPro                    │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                                 CLIENT LAYER                                │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                          Web Browser                                 │  │
│  │                                                                        │  │
│  │   ┌───────────────────────────────────────────────────────────────┐  │  │
│  │   │                      Presentation Layer                          │  │  │
│  │   │                                                                       │  │  │
│  │   │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │  │  │
│  │   │   │   HTML      │  │   CSS       │  │  JavaScript │              │  │  │
│  │   │   │  Templates  │  │ (Tailwind)  │  │  (Vanilla)  │              │  │  │
│  │   │   └─────────────┘  └─────────────┘  └─────────────┘              │  │  │
│  │   │                                                                       │  │  │
│  │   │   ┌──────────────────────────────────────────────────────┐      │  │  │
│  │   │   │                    UI Components                        │      │  │  │
│  │   │   │   - Dashboard      - Forms      - Charts              │      │  │  │
│  │   │   │   - Results View   - Tables     - Modals              │      │  │  │
│  │   │   │   - Navigation     - Cards      - Toast Notifications  │      │  │  │
│  │   │   └──────────────────────────────────────────────────────┘      │  │  │
│  │   │                                                                       │  │  │
│  │   └───────────────────────────────────────────────────────────────┘  │  │
│  │                                                                        │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                    HTTP/HTTPS + SSE + WebSocket
                                 │
                                 ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                                SERVER LAYER                                  │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                    API Gateway / Load Balancer                         │ │
│  │                         (Nginx)                                        │ │
│  │                         Port: 80/443                                   │ │
│  │                         - SSL Termination                              │ │
│  │                         - Load Balancing                               │ │
│  │                         - Static Files                                 │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                        │                                     │
│                                        ▼                                     │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                    Application Server                                  │ │
│  │                    (FastAPI + Uvicorn)                                │ │
│  │                    Port: 8000                                         │ │
│  │                                                                        │ │
│  │   ┌───────────────────────────────────────────────────────────────┐   │ │
│  │   │                      API Layer                                  │   │ │
│  │   │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │   │ │
│  │   │   │  /auth/*    │  │  /test/*    │  │  /results/* │           │   │ │
│  │   │   │  Register    │  │  New Test   │  │  View       │           │   │ │
│  │   │   │  Login      │  │  Status     │  │  Download   │           │   │ │
│  │   │   │  Logout     │  │             │  │  Share     │           │   │ │
│  │   │   │  Refresh    │  │             │  │             │           │   │ │
│  │   │   └─────────────┘  └─────────────┘  └─────────────┘           │   │ │
│  │   │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │   │ │
│  │   │   │  /history   │  │ /analytics  │  │  /compare   │           │   │ │
│  │   │   │  List       │  │ Dashboard  │  │  Compare    │           │   │ │
│  │   │   │             │  │             │  │             │           │   │ │
│  │   │   └─────────────┘  └─────────────┘  └─────────────┘           │   │ │
│  │   └───────────────────────────────────────────────────────────────┘   │ │
│  │                                                                        │ │
│  │   ┌───────────────────────────────────────────────────────────────┐   │ │
│  │   │                    Business Logic Layer                          │   │ │
│  │   │                                                                       │   │ │
│  │   │   ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │   │ │
│  │   │   │   Auth Service  │  │  Test Runner    │  │  Report Service │  │   │ │
│  │   │   │  - JWT Token    │  │  - Orchestrate │  │  - Generate    │  │   │ │
│  │   │   │  - Password Hash│  │  - Background  │  │  - Export      │  │   │ │
│  │   │   │  - Rate Limit  │  │  - Progress    │  │  - Share       │  │   │ │
│  │   │   └─────────────────┘  └─────────────────┘  └─────────────────┘  │   │ │
│  │   │   ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │   │ │
│  │   │   │  Audit Service │  │  Compare Service│  │Analytics Service│  │   │ │
│  │   │   │  - Log Action │  │  - Diff Report │  │  - Statistics   │  │   │ │
│  │   │   │  - Query Logs │  │  - Score Comp  │  │  - Trends      │  │   │ │
│  │   │   └─────────────────┘  └─────────────────┘  └─────────────────┘  │   │ │
│  │   │                                                                       │   │ │
│  │   └───────────────────────────────────────────────────────────────┘   │ │
│  │                                                                        │ │
│  │   ┌───────────────────────────────────────────────────────────────┐   │ │
│  │   │                    Testing Engine Layer                        │   │ │
│  │   │                                                                       │   │ │
│  │   │   ┌─────────────────────────────────────────────────────────┐  │   │ │
│  │   │   │                    Playwright Engine                      │  │   │ │
│  │   │   │                                                             │  │   │ │
│  │   │   │   ┌───────────┐  ┌───────────┐  ┌───────────┐          │  │   │ │
│  │   │   │   │  Browser   │  │  Context   │  │   Pages   │          │  │   │ │
│  │   │   │   │  Chromium │  │            │  │            │          │  │   │ │
│  │   │   │   └───────────┘  └───────────┘  └───────────┘          │  │   │ │
│  │   │   │                                                             │  │   │ │
│  │   │   │   ┌─────────────────────────────────────────────────┐     │  │   │ │
│  │   │   │   │                  Modules                         │     │  │   │ │
│  │   │   │   │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐     │     │  │   │ │
│  │   │   │   │  │   SEO  │ │ Perf   │ │ Secur  │ │ A11y   │     │     │  │   │ │
│  │   │   │   │  └────────┘ └────────┘ └────────┘ └────────┘     │     │  │   │ │
│  │   │   │   │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐     │     │  │   │ │
│  │   │   │   │  │ Crawl  │ │ Visual │ │ Monitor│ │Report  │     │     │  │   │ │
│  │   │   │   │  └────────┘ └────────┘ └────────┘ └────────┘     │     │  │   │ │
│  │   │   │   └─────────────────────────────────────────────────┘     │  │   │ │
│  │   │   └─────────────────────────────────────────────────────────┘  │   │ │
│  │   │                                                                       │   │ │
│  │   └───────────────────────────────────────────────────────────────┘   │ │
│  │                                                                        │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────────────┘
                                 │
                                 │
                                 ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                              DATA LAYER                                     │
│                                                                              │
│  ┌─────────────────────────────┐    ┌─────────────────────────────────────┐│
│  │        SQLite Database      │    │           File System                 ││
│  │                             │    │                                       ││
│  │   ┌───────────────────┐    │    │   ┌─────────────────────────────────┐││
│  │   │      Tables       │    │    │   │          /data                   │││
│  │   │                   │    │    │   │   ┌───────────────────────────┐ │││
│  │   │  ┌─────────────┐ │    │    │   │   │   webtesterpro.db         │ │││
│  │   │  │   users     │ │    │    │   │   └───────────────────────────┘ │││
│  │   │  └─────────────┘ │    │    │   └─────────────────────────────────┘││
│  │   │  ┌─────────────┐ │    │    │                                       ││
│  │   │  │   reports   │ │    │    │   ┌─────────────────────────────────┐││
│  │   │  └─────────────┘ │    │    │   │        /reports                   │││
│  │   │  ┌─────────────┐ │    │    │   │   ┌───────────────────────────┐ │││
│  │   │  │  audit_logs│ │    │    │   │   │  report_*.json           │ │││
│  │   │  └─────────────┘ │    │    │   │   │  report_*.html           │ │││
│  │   │  ┌─────────────┐ │    │    │   │   │  history.json           │ │││
│  │   │  │share_tokens│ │    │    │   │   └───────────────────────────┘ │││
│  │   │  └─────────────┘ │    │    │   └─────────────────────────────────┘││
│  │   │  ┌─────────────┐ │    │    │                                       ││
│  │   │  │scheduled_   │ │    │    │   ┌─────────────────────────────────┐││
│  │   │  │   tests     │ │    │    │   │         /logs                   │││
│  │   │  └─────────────┘ │    │    │   │   ┌───────────────────────────┐ │││
│  │   │                   │    │    │   │   │  webtesterpro.log       │ │││
│  │   └───────────────────┘    │    │   │   └───────────────────────────┘ │││
│  │                             │    │   └─────────────────────────────────┘││
│  └─────────────────────────────┘    └─────────────────────────────────────┘│
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 4.4 Three-Layer Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   Three-Layer Architecture: WebTesterPro                   │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           PRESENTATION LAYER                                │
│                              (Web Browser)                                   │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                                                                       │ │
│  │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  │ │
│  │   │   Views      │  │  Components  │  │   Forms     │                  │ │
│  │   │             │  │              │  │              │                  │ │
│  │   │ - Dashboard  │  │ - Score Card │  │ - Login Form │                  │ │
│  │   │ - Results    │  │ - Module List│  │ - Register    │                  │ │
│  │   │ - History    │  │ - Issue List │  │ - Test Form   │                  │ │
│  │   │ - Analytics  │  │ - Chart      │  │              │                  │ │
│  │   │ - Compare    │  │ - Progress    │  │              │                  │ │
│  │   │ - Admin      │  │ - Toast       │  │              │                  │ │
│  │   └─────────────┘  └─────────────┘  └─────────────┘                  │ │
│  │                                                                       │ │
│  │   ┌───────────────────────────────────────────────────────────────┐ │ │
│  │   │                  JavaScript Controllers                         │ │ │
│  │   │   - SSE Client (Real-time Updates)                              │ │ │
│  │   │   - API Client (Fetch/Async)                                    │ │ │
│  │   │   - Form Validation                                             │ │ │
│  │   │   - URL Validator                                               │ │ │
│  │   │   - Toast Notifications                                         │ │ │
│  │   │   - Keyboard Shortcuts                                          │ │ │
│  │   └───────────────────────────────────────────────────────────────┘ │ │
│  │                                                                       │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                    HTTP/REST + SSE + Jinja2 Templates
                                 │
                                 ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                            BUSINESS LOGIC LAYER                              │
│                              (FastAPI Application)                           │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                     Authentication Module                               │ │
│  │   ┌────────────────┐  ┌────────────────┐  ┌────────────────┐           │ │
│  │   │  Auth Service  │  │ JWT Manager    │  │ Rate Limiter  │           │ │
│  │   │  - Login       │  │ - Token Create │  │ - IP Tracking │           │ │
│  │   │  - Register    │  │ - Token Verify │  │ - Max Attempts│           │ │
│  │   │  - Logout      │  │ - Token Refresh│  │               │           │ │
│  │   └────────────────┘  └────────────────┘  └────────────────┘           │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                      Test Management Module                              │ │
│  │   ┌────────────────┐  ┌────────────────┐  ┌────────────────┐           │ │
│  │   │  Test Runner   │  │  Report Service │  │  SSE Manager   │           │ │
│  │   │  - Orchestrate │  │  - Generate     │  │  - Subscribe   │           │ │
│  │   │  - Background  │  │  - Load        │  │  - Emit        │           │ │
│  │   │  - Progress     │  │  - Download    │  │  - Unsubscribe │           │ │
│  │   │  - Error Handle│  │  - Share      │  │               │           │ │
│  │   └────────────────┘  └────────────────┘  └────────────────┘           │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                       Analytics Module                                   │ │
│  │   ┌────────────────┐  ┌────────────────┐  ┌────────────────┐           │ │
│  │   │  Stats Service │  │ Trend Service  │  │  Compare Svc   │           │ │
│  │   │  - User Stats  │  │  - Score Trend│  │  - Diff Report │           │ │
│  │   │  - Score Dist  │  │  - Frequency  │  │  - Score Comp  │           │ │
│  │   │  - Module Usage│  │               │  │               │           │ │
│  │   └────────────────┘  └────────────────┘  └────────────────┘           │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                    WebTesterEngine (Testing Core)                       │ │
│  │   ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐                   │ │
│  │   │   SEO    │ │Performance│ │ Security │ │Access-   │                   │ │
│  │   │ Analyzer │ │ Tester   │ │ Scanner │ │ibility   │                   │ │
│  │   └──────────┘ └──────────┘ └──────────┘ └──────────┘                   │ │
│  │   ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐                   │ │
│  │   │ Crawler  │ │  Visual  │ │ Monitor  │ │ Reporter │                   │ │
│  │   │          │ │  Tester  │ │          │ │          │                   │ │
│  │   └──────────┘ └──────────┘ └──────────┘ └──────────┘                   │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                    SQLAlchemy ORM / File I/O
                                 │
                                 ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                              DATA ACCESS LAYER                               │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                      Database Module                                    │ │
│  │   ┌────────────────┐  ┌────────────────┐  ┌────────────────┐           │ │
│  │   │  SQLAlchemy    │  │    Models      │  │    Migrations  │           │ │
│  │   │  - Connection  │  │  - User        │  │  - Alembic     │           │ │
│  │   │  - Session    │  │  - Report      │  │  - Versions    │           │ │
│  │   │  - Query      │  │  - AuditLog   │  │                │           │ │
│  │   │               │  │  - ShareToken  │  │                │           │ │
│  │   │               │  │  - ScheduledTest│  │                │           │ │
│  │   └────────────────┘  └────────────────┘  └────────────────┘           │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                     File Storage Module                                  │ │
│  │   ┌────────────────┐  ┌────────────────┐  ┌────────────────┐           │ │
│  │   │   Reports      │  │    Database     │  │    Logs        │           │ │
│  │   │   - JSON       │  │    - SQLite     │  │    - .log      │           │ │
│  │   │   - HTML       │  │    - File       │  │    - Rotation  │           │ │
│  │   │   - CSV         │  │                 │  │                │           │ │
│  │   └────────────────┘  └────────────────┘  └────────────────┘           │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 4.5 Security Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     Security Architecture: WebTesterPro                     │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              External Zone                                  │
│                                                                             │
│   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐      │
│   │   Browser       │    │   Attacker       │    │   DNS           │      │
│   │   (Legitimate)  │    │   (Malicious)    │    │   Servers       │      │
│   │                 │    │                  │    │                 │      │
│   │ - HTTPS Request │    │ - DDoS Attack    │    │ - Domain        │      │
│   │ - Valid User    │    │ - SQL Injection  │    │   Resolution    │      │
│   │ - Session Cookie │    │ - XSS Attack    │    │                 │      │
│   └────────┬────────┘    └────────┬────────┘    └────────┬────────┘      │
│            │                      │                      │                 │
└────────────┼──────────────────────┼──────────────────────┼────────────────┘
             │                      │                      │
             │                      │                      │
             ▼                      ▼                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Web Application Firewall (WAF)                       │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐ │
│   │                    Security Checks                                    │ │
│   │   - SQL Injection Detection                                           │ │
│   │   - XSS Prevention                                                   │ │
│   │   - Rate Limiting                                                    │ │
│   │   - Bot Detection                                                     │ │
│   │   - Geo-blocking (optional)                                          │ │
│   └─────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                              Application Layer                                │
│                                                                              │
│   ┌───────────────────────────────────────────────────────────────────────┐ │
│   │                        Authentication Security                           │ │
│   │                                                                        │ │
│   │   ┌───────────────────────────────────────────────────────────────┐   │ │
│   │   │                      JWT Tokens                                │   │ │
│   │   │   ┌────────────────┐  ┌────────────────┐  ┌────────────────┐   │   │ │
│   │   │   │  Access Token │  │ Refresh Token  │  │  Token Storage │   │   │ │
│   │   │   │  - 30 min      │  │  - 7 days      │  │  - HttpOnly   │   │   │ │
│   │   │   │  - HS256       │  │  - Stored in   │  │  - SameSite   │   │   │ │
│   │   │   │  - User ID     │  │    Cookie      │  │  - Secure     │   │   │ │
│   │   │   └────────────────┘  └────────────────┘  └────────────────┘   │ │
│   │   └───────────────────────────────────────────────────────────────┘   │ │
│   │                                                                        │ │
│   │   ┌───────────────────────────────────────────────────────────────┐   │ │
│   │   │                      Password Security                         │   │ │
│   │   │   ┌────────────────┐  ┌────────────────┐                      │   │ │
│   │   │   │  bcrypt        │  │  Validation    │                      │   │ │
│   │   │   │  - Hashing     │  │  - Min 8 chars │                      │   │ │
│   │   │   │  - Salt        │  │  - Uppercase   │                      │   │ │
│   │   │   │  - Cost Factor │  │  - Lowercase   │                      │   │ │
│   │   │   │    (12)        │  │  - Number       │                      │   │ │
│   │   │   └────────────────┘  └────────────────┘                      │   │ │
│   │   └───────────────────────────────────────────────────────────────┘   │ │
│   │                                                                        │ │
│   │   ┌───────────────────────────────────────────────────────────────┐   │ │
│   │   │                      Rate Limiting                              │   │ │
│   │   │   ┌───────────────────────────────────────────────────────┐   │   │ │
│   │   │   │                     In-Memory Store                       │   │   │ │
│   │   │   │   - Login: 5 attempts / 15 minutes / IP                 │   │   │ │
│   │   │   │   - API: 100 requests / minute / user                   │   │   │ │
│   │   │   │   - Test Creation: 10 / hour / user                    │   │   │ │
│   │   │   └───────────────────────────────────────────────────────┘   │   │ │
│   │   └───────────────────────────────────────────────────────────────┘   │ │
│   └───────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│   ┌───────────────────────────────────────────────────────────────────────┐ │
│   │                       Authorization Security                            │ │
│   │                                                                        │ │
│   │   ┌───────────────────────────────────────────────────────────────┐   │ │
│   │   │                    Role-Based Access Control (RBAC)              │   │ │
│   │   │   ┌────────────────┐  ┌────────────────┐  ┌────────────────┐   │   │ │
│   │   │   │    Admin       │  │    User        │  │   Anonymous    │   │   │ │
│   │   │   │                │  │                │  │                │   │   │ │
│   │   │   │  - Full Access│  │  - Own Reports │  │  - Shared Only │   │   │ │
│   │   │   │  - User Mgmt  │  │  - Create Test │  │                │   │ │
│  │   │   │  - View All   │  │  - Download   │  │                │   │ │
│   │   │   │  - Audit Logs │  │  - Share      │  │                │   │ │
│   │   │   └────────────────┘  └────────────────┘  └────────────────┘   │   │ │
│   │   └───────────────────────────────────────────────────────────────┘   │ │
│   │                                                                        │ │
│   │   ┌───────────────────────────────────────────────────────────────┐   │ │
│   │   │                      Resource-Level Security                   │   │ │
│   │   │   - Report Owner Check: user_can_view_report()              │   │ │
│   │   │   - Share Token Validation                                   │   │ │
│   │   │   - Admin Override                                          │   │ │
│   │   └───────────────────────────────────────────────────────────────┘   │ │
│   └───────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│   ┌───────────────────────────────────────────────────────────────────────┐ │
│   │                        Audit Logging                                   │ │
│   │   ┌───────────────────────────────────────────────────────────────┐   │ │
│   │   │                      AuditLog Table                            │   │ │
│   │   │   - user_id (nullable for anonymous)                           │   │ │
│   │   │   - action (login, test_start, test_view, etc.)              │   │ │
│   │   │   - resource_type & resource_id                               │   │ │
│   │   │   - ip_address                                               │   │ │
│   │   │   - user_agent                                               │   │ │
│   │   │   - created_at                                               │   │ │
│   │   └───────────────────────────────────────────────────────────────┘   │ │
│   └───────────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                               Data Layer                                       │
│                                                                              │
│   ┌───────────────────────────────────────────────────────────────────────┐ │
│   │                         Database Security                              │ │
│   │   ┌────────────────┐  ┌────────────────┐  ┌────────────────┐          │ │
│   │   │  SQLite File   │  │   File System   │  │   Backups       │          │ │
│   │   │  Permissions   │  │   Permissions   │  │   Encrypted     │          │ │
│   │   │  - Owner Only │  │  - Restricted  │  │  - Daily        │          │ │
│   │   └────────────────┘  └────────────────┘  └────────────────┘          │ │
│   └───────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 4.6 Authentication Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      Authentication Flow: WebTesterPro                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────┐                    ┌──────────────┐                    ┌──────────────┐
│  User   │                    │  Frontend    │                    │   Backend    │
└────┬────┘                    └──────┬───────┘                    └──────┬───────┘
     │                               │                                  │
     │ 1. GET /login                │                                  │
     │──────────────────────────────►│                                  │
     │                               │                                  │
     │ 2. Render Login Page         │                                  │
     │◄─────────────────────────────│                                  │
     │                               │                                  │
     │ 3. POST /login (credentials) │                                  │
     │──────────────────────────────►│ 4. Forward to Backend            │
     │                               │────────────────────────────────►│
     │                               │                                  │
     │                               │                   5. Check Rate Limit
     │                               │                                  │
     │                               │                   6. Verify Credentials
     │                               │                                  │
     │                               │                   7. Create Tokens
     │                               │                   - Access (30m)
     │                               │                   - Refresh (7d)
     │                               │                                  │
     │                               │                   8. Update last_login
     │                               │                                  │
     │                               │                   9. Log to audit_logs
     │                               │                                  │
     │ 10. Set HttpOnly Cookies     │◄────────────────────────────────│
     │◄─────────────────────────────│                                  │
     │                               │                                  │
     │ 11. Redirect to /            │                                  │
     │◄─────────────────────────────│                                  │
     │                               │                                  │
     │ 12. GET / (with cookies)     │                                  │
     │──────────────────────────────►│ 13. Validate Access Token      │
     │                               │────────────────────────────────►│
     │                               │                                  │
     │                               │                   14. Extract user_id
     │                               │                                  │
     │                               │                   15. Get User from DB
     │                               │                                  │
     │                               │                   16. Check is_active
     │                               │                                  │
     │ 17. Dashboard Page (HTML)    │◄────────────────────────────────│
     │◄─────────────────────────────│                                  │


                                LOGOUT FLOW

     │                               │                                  │
     │ 1. POST /logout              │                                  │
     │──────────────────────────────►│ 2. Clear Cookies               │
     │                               │────────────────────────────────►│
     │                               │                                  │
     │                               │                   3. Log to audit_logs
     │                               │                                  │
     │ 4. Redirect to /login        │                                  │
     │◄─────────────────────────────│                                  │
     │                               │                                  │
```

## 4.7 Authorization Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      Authorization Flow: WebTesterPro                        │
└─────────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────────────────────┐
                    │         Request Incoming            │
                    └─────────────────┬───────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────┐
                    │   Check Authentication (JWT)      │
                    │                                     │
                    │   - Extract token from header/cookie│
                    │   - Verify signature                │
                    │   - Check expiration                │
                    └─────────────────┬───────────────────┘
                                      │
                         ┌────────────┴────────────┐
                         │                         │
                         ▼                         ▼
                   ┌──────────┐           ┌──────────┐
                   │  Valid   │           │ Invalid  │
                   │  Token   │           │  Token   │
                   └────┬─────┘           └────┬─────┘
                        │                      │
                        ▼                      ▼
                ┌───────────────┐     ┌───────────────┐
                │ Get User from│     │ HTTP 401     │
                │ DB           │     │ Unauthorized  │
                └───────┬───────┘     └───────────────┘
                        │
                        ▼
                ┌───────────────┐
                │ Check is_active│
                │               │
                └───────┬───────┘
                        │
           ┌────────────┴────────────┐
           │                         │
           ▼                         ▼
     ┌──────────┐            ┌──────────┐
     │  Active  │            │ Inactive │
     │  Account  │            │ Account  │
     └────┬──────┘            └────┬─────┘
          │                        │
          ▼                        ▼
   ┌─────────────┐         ┌─────────────┐
   │ Check Roles │         │ HTTP 403    │
   │ (RBAC)      │         │ Forbidden   │
   └──────┬──────┘         └─────────────┘
          │
          ▼
   ┌─────────────────┐
   │ Required Role    │
   │ Check           │
   └────────┬────────┘
            │
            │
    ┌───────┴───────┐
    │               │
    ▼               ▼
┌──────────┐  ┌──────────┐
│  Access  │  │  Denied  │
│  Granted │  │  HTTP 403│
└──────────┘  └──────────┘


                        ROLE CHECKS

┌─────────────────────────────────────────────────────────────────┐
│                         ADMIN CHECK                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   def require_admin():                                          │
│       if not current_user.is_admin:                             │
│           raise HTTPException(403)                               │
│                                                                 │
│   Admin Endpoints:                                              │
│   - /admin/users    → Manage all users                        │
│   - /admin/*        → System administration                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        USER CHECK                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   def user_can_view_report(user, report):                       │
│       return user.is_admin or report.user_id == user.id         │
│                                                                 │
│   User Endpoints:                                               │
│   - /results/{id}  → Own reports only                         │
│   - /history       → Own history only                         │
│   - /test/new      → Create new tests                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      ANONYMOUS CHECK                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Anonymous Endpoints:                                          │
│   - /share/{token}  → Public shared reports                   │
│                                                                 │
│   Check:                                                        │
│   - Validate share token                                        │
│   - Check expiration                                            │
│   - Increment view_count                                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 4.8 DFD Level 0 (Context Diagram)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DFD Level 0: Context Diagram                       │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                              WebTesterPro                                   │
│                             (The System)                                    │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                                                                        │ │
│  │   +---------------------+                                           │ │
│  │   │                     │                                           │ │
│  │   │    User Actions    │                                           │ │
│  │   │                     │                                           │ │
│  │   │  - Register        │                                           │ │
│  │   │  - Login          │                                           │ │
│  │   │  - Create Test    │                                           │ │
│  │   │  - View Results   │                                           │ │
│  │   │  - Download       │                                           │ │
│  │   │  - Share          │                                           │ │
│  │   │  - Compare        │                                           │ │
│  │   │  - Logout         │                                           │ │
│  │   │                     │                                           │ │
│  │   └──────────┬──────────┘                                           │ │
│  │              │                                                      │ │
│  │              │ User Input                                            │ │
│  │              │                                                      │ │
│  │   ┌──────────▼──────────────────────────────────────────────┐       │ │
│  │   │                                                        │       │ │
│  │   │                      PROCESSES                           │       │ │
│  │   │                                                        │       │ │
│  │   │   ┌──────────────────────────────────────────────┐   │       │ │
│  │   │   │                                              │   │       │ │
│  │   │   │              WebTesterPro                      │   │       │ │
│  │   │   │              System                            │   │       │ │
│  │   │   │                                              │   │       │ │
│  │   │   │   ┌─────────┐ ┌─────────┐ ┌─────────┐      │   │       │ │
│  │   │   │   │   Auth  │ │  Test   │ │ Report │      │   │       │ │
│  │   │   │   │ Service │ │ Runner │ │Service │      │   │       │ │
│  │   │   │   └────┬────┘ └────┬────┘ └────┬────┘      │   │       │ │
│  │   │   │        │          │          │             │   │       │ │
│  │   │   │        │          │          │             │   │       │ │
│  │   │   │        ▼          ▼          ▼             │   │       │ │
│  │   │   │   ┌─────────────────────────────────┐   │   │       │ │
│  │   │   │   │                                 │   │   │       │ │
│  │   │   │   │        Testing Engine           │   │   │       │ │
│  │   │   │   │                                 │   │   │       │ │
│  │   │   │   │  ┌─────┐ ┌─────┐ ┌─────┐ ┌───┐ │   │   │       │ │
│  │   │   │   │  │ SEO │ │Perf │ │Secur│ │A11y│ │   │   │       │ │
│  │   │   │   │  └─────┘ └─────┘ └─────┘ └───┘ │   │   │       │ │
│  │   │   │   │                                 │   │   │       │ │
│  │   │   │   │  ┌─────┐ ┌─────┐ ┌─────┐ ┌───┐ │   │   │       │ │
│  │   │   │   │  │Crawl│ │Visul│ │Monit│ │Scan│ │   │   │       │ │
│  │   │   │   │  └─────┘ └─────┘ └─────┘ └───┘ │   │   │       │ │
│  │   │   │   │                                 │   │   │       │ │
│  │   │   │   └─────────────────────────────────┘   │   │       │ │
│  │   │   │                                              │   │       │ │
│  │   │   │   ┌──────────────────────────────────────┐ │   │       │ │
│  │   │   │   │         Database (SQLite)             │ │   │       │ │
│  │   │   │   │  ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ │ │   │       │ │
│  │   │   │   │  │users│ │rprts│ │logs│ │share│ │sched│ │ │   │       │ │
│  │   │   │   │  └────┘ └────┘ └────┘ └────┘ └────┘ │ │   │       │ │
│  │   │   │   └──────────────────────────────────────┘ │   │       │ │
│  │   │   │                                              │   │       │ │
│  │   │   └──────────────────────────────────────────────┘   │       │ │
│  │   │                                                        │       │ │
│  │   └──────────┬────────────────────────────────────────────┘       │ │
│  │              │                                                      │ │
│  │              │                                                      │ │
│  │              ▼                                                      │ │
│  │   ┌──────────────────────┐                                        │ │
│  │   │                      │                                        │ │
│  │   │    Output Data       │                                        │ │
│  │   │                      │                                        │ │
│  │   │  - Dashboard HTML    │                                        │ │
│  │   │  - Test Results     │                                        │ │
│  │   │  - Export Files     │                                        │ │
│  │   │  - Analytics Data   │                                        │ │
│  │   │  - Share Links      │                                        │ │
│  │   │  - SSE Events      │                                        │ │
│  │   │                      │                                        │ │
│  │   └──────────┬──────────┘                                        │ │
│  │              │                                                      │ │
│  │              │ User Output                                         │ │
│  │              │                                                      │ │
│  └──────────────┼────────────────────────────────────────────────────┘ │
│                 │                                                       │
│                 │                                                       │
└─────────────────┼───────────────────────────────────────────────────────┘
                  │
                  │
                  ▼
          ┌──────────────┐
          │    User      │
          │  (Actor)     │
          └──────────────┘


          ┌──────────────┐
          │   Target     │
          │  Website     │
          │(Being Tested│
          └──────┬───────┘
                 │
                 │ HTTP/HTTPS
                 │
                 ▼
          ┌──────────────┐
          │  Playwright   │
          │   Browser    │
          │  (Headless)  │
          └──────────────┘
```

## 4.9 DFD Level 1

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DFD Level 1: Main Processes                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                            WebTesterPro System                              │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                                                                       │ │
│  │                              USER                                     │ │
│  │                                                                       │ │
│  └───────────────────────────────┬───────────────────────────────────────┘ │
│                                  │                                         │
│                                  │ 1. Login Request                        │
│                                  │    (email, password)                    │
│                                  ▼                                         │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                    1.0 Authentication Process                         │ │
│  │   ┌───────────────────────────────────────────────────────────────┐   │ │
│  │   │  - Validate credentials                                       │   │ │
│  │   │  - Generate JWT tokens                                        │   │ │
│  │   │  - Set session cookies                                         │   │ │
│  │   │  - Log audit entry                                            │   │ │
│  │   └───────────────────────────────────────────────────────────────┘   │ │
│  │                           │                                           │ │
│  │                           │ 2. User Session Token                     │ │
│  │                           ▼                                           │ │
│  └───────────────────────────┼───────────────────────────────────────────┘ │
│                              │                                             │
│                              │ 3. Create Test Request                     │
│                              │    (URL, modules, options)                │
│                              ▼                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                    2.0 Test Creation Process                          │ │
│  │   ┌───────────────────────────────────────────────────────────────┐   │ │
│  │   │  - Validate URL format                                       │   │ │
│  │   │  - Validate selected modules                                   │   │ │
│  │   │  - Create Report record (status: running)                       │   │ │
│  │   │  - Queue background task                                       │   │ │
│  │   └───────────────────────────────────────────────────────────────┘   │ │
│  │                           │                                           │ │
│  │                           │ 4. Test ID                                │ │
│  │                           ▼                                           │
│  └───────────────────────────┼───────────────────────────────────────────┘ │
│                              │                                             │
│                              │ 5. Run Module Tests                        │
│                              │    (in background)                         │
│                              ▼                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                    3.0 Test Execution Process                         │ │
│  │   ┌───────────────────────────────────────────────────────────────┐   │ │
│  │   │                                                               │   │ │
│  │   │   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │   │ │
│  │   │   │  3.1     │  │  3.2     │  │  3.3     │  │  3.4     │   │   │ │
│  │   │   │  SEO      │  │Performance│  │ Security  │  │Access-   │   │   │ │
│  │   │   │  Check    │  │  Test    │  │  Scan     │  │ibility   │   │   │ │
│  │   │   └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └────┬─────┘   │   │ │
│  │   │         │              │              │              │         │   │ │
│  │   │         └──────────────┼──────────────┼──────────────┘         │   │ │
│  │   │                         │              │                      │   │ │
│  │   │                         └──────────────┼──────────────────────┘   │ │
│  │   │                                        │                          │   │ │
│  │   │   ┌──────────┐  ┌──────────┐  ┌──────┴──────┐  ┌──────────┐   │   │ │
│  │   │   │  3.5     │  │  3.6     │  │   3.7       │  │  3.8     │   │   │ │
│  │   │   │ Crawler  │  │  Visual  │  │  Monitor    │  │  Reporter│   │   │
│  │   │   │          │  │  Test    │  │             │  │          │   │   │
│  │   │   └──────────┘  └──────────┘  └──────────────┘  └──────────┘   │   │ │
│  │   │                                                               │   │ │
│  │   └────────────────────────────┬──────────────────────────────────┘   │ │
│  │                                │                                       │ │
│  │                                │ 6. Test Results Data                  │ │
│  │                                ▼                                       │ │
│  │   ┌───────────────────────────────────────────────────────────────┐   │ │
│  │   │                 3.9 Report Aggregation                        │   │ │
│  │   │  - Calculate overall score                                  │   │ │
│  │   │  - Generate recommendations                                  │   │ │
│  │   │  - Save report to database                                   │   │ │
│  │   │  - Save report to file system                               │   │ │
│  │   └───────────────────────────────────────────────────────────────┘   │ │
│  │                                                                      │ │
│  └─────────────────────────────┬────────────────────────────────────────┘ │
│                                │                                          │
│                                │ 7. Progress Updates (SSE)                │
│                                ▼                                          │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                    4.0 Reporting Process                             │ │
│  │   ┌───────────────────────────────────────────────────────────────┐   │ │
│  │   │  - Render results dashboard                                   │   │ │
│  │   │  - Generate export files (JSON, HTML, CSV)                    │   │ │
│  │   │  - Create share links                                          │   │ │
│  │   │  - Compute analytics                                          │   │ │
│  │   └───────────────────────────────────────────────────────────────┘   │ │
│  │                           │                                           │ │
│  │                           │ 8. Results HTML/JSON                     │ │
│  │                           ▼                                           │
│  └───────────────────────────┼───────────────────────────────────────────┘ │
│                              │                                             │
│                              │ 9. User Output                             │
│                              ▼                                             │
│                          ┌──────────┐                                      │
│                          │   USER   │                                      │
│                          └──────────┘                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘


                    EXTERNAL ENTITIES

          ┌──────────────────┐    ┌──────────────────┐
          │   Target         │    │   External       │
          │   Website        │    │   Services       │
          │                  │    │                  │
          │ - Fetch pages    │    │ - axe-core CDN   │
          │ - Extract HTML   │    │ - Google Fonts   │
          │ - Measure perf   │    │ - CDN resources  │
          │                  │    │                  │
          └────────┬─────────┘    └────────┬─────────┘
                   │                       │
                   │ HTTP/HTTPS             │ HTTP/HTTPS
                   │                       │
                   └───────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────┐
                    │   Playwright      │
                    │   Browser        │
                    │   (Headless)     │
                    │                  │
                    └──────────────────┘
```

## 4.10 DFD Level 2 (Test Execution)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DFD Level 2: Test Execution Process                     │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                    3.0 Test Execution Process                              │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                                                                      │ │
│  │   ┌─────────────────────────────────────────────────────────────┐    │ │
│  │   │                    Browser Launch                            │    │ │
│  │   │   - Create Playwright instance                               │    │ │
│  │   │   - Launch headless Chromium                                 │    │ │
│  │   │   - Create browser context                                   │    │ │
│  │   │   - Set viewport (1920x1080)                                │    │ │
│  │   └────────────────────────────┬────────────────────────────────┘    │ │
│  │                                │                                    │ │
│  │                                │                                    │ │
│  │                                ▼                                    │ │
│  │   ┌─────────────────────────────────────────────────────────────┐    │ │
│  │   │                    Page Navigation                          │    │ │
│  │   │   - Navigate to target URL                                 │    │ │
│  │   │   - Wait for domcontentloaded                               │    │ │
│  │   │   - Capture network requests                                 │    │ │
│  │   │   - Wait for networkidle                                     │    │ │
│  │   └────────────────────────────┬────────────────────────────────┘    │ │
│  │                                │                                    │ │
│  │                                │ Page Content                        │ │
│  │                                ▼                                    │ │
│  │   ┌─────────────────────────────────────────────────────────────┐    │ │
│  │   │                  Content Analysis                            │    │ │
│  │   │   - Get HTML content                                        │    │ │
│  │   │   - Parse with BeautifulSoup                                │    │ │
│  │   │   - Extract metadata                                        │    │ │
│  │   │   - Analyze DOM structure                                   │    │ │
│  │   └────────────────────────────┬────────────────────────────────┘    │ │
│  │                                │                                    │ │
│  │                                │ Parsed HTML                        │ │
│  │                                ▼                                    │ │
│  │   ┌─────────────────────────────────────────────────────────────┐    │ │
│  │   │                    Module Execution                         │    │ │
│  │   │                                                              │    │ │
│  │   │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │    │ │
│  │   │   │    SEO      │  │  Performance│  │   Security  │        │    │ │
│  │   │   │             │  │             │  │             │        │    │ │
│  │   │   │ - Title     │  │ - LCP      │  │ - Headers   │        │    │ │
│  │   │   │ - Meta      │  │ - FID/INP  │  │ - XSS      │        │    │ │
│  │   │   │ - Headings  │  │ - CLS      │  │ - SQLi     │        │    │ │
│  │   │   │ - OG Tags   │  │ - TTFB     │  │ - Files    │        │    │ │
│  │   │   │ - Schema    │  │ - FCP      │  │ - CORS     │        │    │ │
│  │   │   │ - Images    │  │ - TBT      │  │ - Clickjack │        │    │ │
│  │   │   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │    │ │
│  │   │          │                 │                 │                 │    │ │
│  │   │          └─────────────────┼─────────────────┘                 │    │ │
│  │   │                            │                                   │    │ │
│  │   │   ┌─────────────┐  ┌──────┴──────┐  ┌─────────────┐        │    │ │
│  │   │   │Accessibility│  │   Crawler    │  │   Visual    │        │    │ │
│  │   │   │             │  │              │  │             │        │    │ │
│  │   │   │ - axe-core  │  │ - Links     │  │ - Screenshot│        │    │ │
│  │   │   │ - WCAG      │  │ - Resources │  │ - Viewport  │        │    │ │
│  │   │   │ - Contrast  │  │ - Depth     │  │ - Full page  │        │    │ │
│  │   │   │ - Alt text │  │ - robots.txt│  │             │        │    │ │
│  │   │   │ - ARIA     │  │             │  │             │        │    │ │
│  │   │   └─────────────┘  └─────────────┘  └─────────────┘        │    │ │
│  │   │                                                              │    │ │
│  │   └────────────────────────────┬──────────────────────────────────┘    │ │
│  │                                │                                       │ │
│  │                                │ Module Results                       │ │
│  │                                ▼                                       │ │
│  │   ┌─────────────────────────────────────────────────────────────┐    │ │
│  │   │                    Score Calculation                         │    │ │
│  │   │   - SEO Score: Title (15%) + Meta (15%) + Head (15%)...   │    │ │
│  │   │   - Performance Score: LCP (25%) + CLS (25%) + FID (25%)... │    │ │
│  │   │   - Security Score: 100 - (Critical×30 + High×20...)      │    │ │
│  │   │   - Accessibility Score: 100 - (Critical×15 + Serious×10..│    │ │
│  │   │   - Overall Score: Average of all module scores           │    │ │
│  │   └────────────────────────────┬────────────────────────────────┘    │ │
│  │                                │                                    │ │
│  │                                │ Scores + Issues                   │ │
│  │                                ▼                                    │ │
│  │   ┌─────────────────────────────────────────────────────────────┐    │ │
│  │   │                    Report Generation                         │    │ │
│  │   │   - Aggregate all results                                    │    │ │
│  │   │   - Generate recommendations                                  │    │ │
│  │   │   - Create JSON report                                       │    │ │
│  │   │   - Save to file system                                      │    │ │
│  │   │   - Update database record                                    │    │ │
│  │   └─────────────────────────────────────────────────────────────┘    │ │
│  │                                                                      │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

# CHƯƠNG 5: THIẾT KẾ CƠ SỞ DỮ LIỆU

## 5.1 ERD (Entity-Relationship Diagram)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          ERD: WebTesterPro Database                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                              users                                          │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                                                                      │  │
│  │   ┌─────────────────┐     1        *    ┌─────────────────┐         │  │
│  │   │                 ├────────────────────│                 │         │  │
│  │   │   id (PK)       │                    │     id (PK)     │         │  │
│  │   │   email         │                    │     user_id(FK) │──────────┘  │
│  │   │   username      │                    │     title        │            │
│  │   │   hashed_pwd   │                    │     url          │            │
│  │   │   is_active    │                    │     file_path    │            │
│  │   │   is_admin     │                    │     json_path    │            │
│  │   │   created_at    │                    │     overall_score│            │
│  │   │   last_login    │                    │     summary       │            │
│  │   │                 │                    │     status        │            │
│  │   │                 │                    │     modules_run   │            │
│  │   │                 │                    │     results_json  │            │
│  │   │                 │                    │     progress      │            │
│  │   │                 │                    │     current_module│            │
│  │   │                 │                    │     created_at    │            │
│  │   │                 │                    │                   │            │
│  │   │                 │                    │     reports       │            │
│  │   │                 │                    └───────────────────┘            │
│  │   │                 │                                                        │
│  │   │      users      │                                                        │
│  │   └─────────────────┘                                                        │
│  │           │                                                                  │
│  │           │ 1                                                                  │
│  │           │                                                                  │
│  │           ▼                                                                  │
│  │   ┌───────────────────────────────────────────────────────────────────────┐  │
│  │   │                                                                      │  │
│  │   │                           audit_logs                                 │  │
│  │   │   ┌─────────────────────────────────────────────────────────────┐    │  │
│  │   │   │                                                               │    │  │
│  │   │   │  id (PK)          user_id (FK) ─────────────┐               │    │  │
│  │   │   │  action                                  │               │    │  │
│  │   │   │  resource_type    ◄──────────────────────┘               │    │  │
│  │   │   │  resource_id                                                │    │  │
│  │   │   │  details                                                     │    │  │
│  │   │   │  ip_address                                                  │    │  │
│  │   │   │  user_agent                                                  │    │  │
│  │   │   │  created_at                                                  │    │  │
│  │   │   │                                                               │    │  │
│  │   │   │                          audit_logs                            │    │  │
│  │   │   └─────────────────────────────────────────────────────────────┘    │  │
│  │   │                                                                      │  │
│  │   └───────────────────────────────────────────────────────────────────────┘  │
│  │                                                                             │  │
│  │           1                                                                  │  │
│  │           │                                                                  │  │
│  │           ▼                                                                  │  │
│  │   ┌───────────────────────────────────────────────────────────────────────┐  │
│  │   │                                                                      │  │
│  │   │                        scheduled_tests                             │  │
│  │   │   ┌─────────────────────────────────────────────────────────────┐    │  │
│  │   │   │                                                               │    │  │
│  │   │   │  id (PK)           user_id (FK) ─────────────┐               │    │  │
│  │   │   │  name                                  │               │    │  │
│  │   │   │  url                                   │               │    │  │
│  │   │   │  modules                               │               │    │  │
│  │   │   │  cron_expression     ◄───────────────┘               │    │  │
│  │   │   │  is_active                                                  │    │  │
│  │   │   │  last_run                                                   │    │  │
│  │   │   │  next_run                                                   │    │  │
│  │   │   │  created_at                                                 │    │  │
│  │   │   │                                                               │    │  │
│  │   │   │                        scheduled_tests                        │    │  │
│  │   │   └─────────────────────────────────────────────────────────────┘    │  │
│  │   │                                                                      │  │
│  │   └───────────────────────────────────────────────────────────────────────┘  │
│  │                                                                             │  │
│  └─────────────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│                                                                             │
│                              reports                                        │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                                                                      │  │
│  │   ┌─────────────────────────────────────────────────────────────┐    │  │
│  │   │                                                              │    │  │
│  │   │     1                          1        *                     │    │  │
│  │   │     │                          │          │                   │    │  │
│  │   │     │      *  ┌────────────┐  │          │                   │    │  │
│  │   │     │        │             │  │          │                   │    │  │
│  │   │  ┌──┴───┐  ┌─┴────────────┴┐ │   ┌─────┴──────────────┐  │    │  │
│  │   │  │share │  │    report     │ │   │    share_token     │  │    │  │
│  │   │  │tokens│──│     (1)       │─┘   │                    │  │    │  │
│  │   │  └──┬───┘  │               │      │  id (PK)           │  │    │  │
│  │   │     │      │  id (PK)      │      │  report_id (FK)────┼──┘    │  │
│  │   │     │      │  user_id(FK)──┼──────│  token             │        │  │
│  │   │     │      │  ...          │      │  expires_at        │        │  │
│  │   │     │      │               │      │  view_count         │        │  │
│  │   │     │      │               │      │  created_by (FK)───┼────────┘  │
│  │   │     │      │               │      │  created_at        │          │  │
│  │   │     │      │               │      │                    │          │  │
│  │   │     │      │               │      │                    │          │  │
│  │   │     │      └───────────────┘      └────────────────────┘          │  │
│  │   │     │                                                              │  │
│  │   │     │                        reports                                 │  │
│  │   │     └───────────────────────────────────────────────────────────────┘  │
│  │   │                                                                        │
│  │   │   share_tokens                                                        │
│  │   │                                                                        │
│  └─────────────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 5.2 Database Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Database Diagram: WebTesterPro                            │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                              SQLite Database                                 │
│                           (webtesterpro.db)                                  │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                                                                       │ │
│  │                         users                                         │ │
│  │  ┌────────────────────────────────────────────────────────────────┐  │ │
│  │  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐  │  │ │
│  │  │  │    id      │ │   email     │ │  username  │ │ hashed_    │  │  │ │
│  │  │  │  INTEGER   │ │  VARCHAR    │ │  VARCHAR   │ │  password  │  │  │ │
│  │  │  │  PRIMARY   │ │  (255)     │ │  (100)     │ │  VARCHAR   │  │  │ │
│  │  │  │  KEY       │ │  UNIQUE    │ │  UNIQUE    │ │  (255)    │  │  │ │
│  │  │  │  AUTO      │ │  NOT NULL  │ │  NOT NULL  │ │  NOT NULL │  │  │ │
│  │  │  │  INCREMENT │ │  INDEX     │ │  INDEX     │ │            │  │  │ │
│  │  │  └────────────┘ └────────────┘ └────────────┘ └────────────┘  │  │ │
│  │  │                                                                     │  │ │
│  │  │  ┌────────────┐ ┌────────────┐ ┌────────────┐                    │  │ │
│  │  │  │  is_active │ │  is_admin  │ │ created_at │                    │  │ │
│  │  │  │  BOOLEAN   │ │  BOOLEAN   │ │  DATETIME  │                    │  │ │
│  │  │  │  DEFAULT   │ │  DEFAULT   │ │  TIMESTAMP│                    │  │ │
│  │  │  │  TRUE      │ │  FALSE     │ │  NOW()    │                    │  │ │
│  │  │  └────────────┘ └────────────┘ └────────────┘                    │  │ │
│  │  │                                                                     │  │ │
│  │  │  ┌────────────────────────────────────────────────────────────┐  │  │ │
│  │  │  │  last_login: DATETIME (nullable)                          │  │  │ │
│  │  │  └────────────────────────────────────────────────────────────┘  │  │ │
│  │  │                                                                     │  │ │
│  │  └──────────────────────────────────────────────────────────────────────┘  │ │
│  │                                                                        │ │
│  │  ┌──────────────────────────────────────────────────────────────────────┐ │ │
│  │  │                              reports                               │ │ │
│  │  │  ┌────────────────────────────────────────────────────────────┐  │ │ │
│  │  │  │  id: INTEGER PRIMARY KEY AUTOINCREMENT                    │  │ │ │
│  │  │  │  user_id: INTEGER (FK → users.id) ON DELETE CASCADE      │  │ │ │
│  │  │  │  title: VARCHAR(255) NOT NULL                             │  │ │ │
│  │  │  │  url: VARCHAR(2048) NOT NULL                               │  │ │ │
│  │  │  │  file_path: VARCHAR(512) (nullable)                       │  │ │ │
│  │  │  │  json_path: VARCHAR(512) (nullable)                       │  │ │ │
│  │  │  │  overall_score: INTEGER (nullable) CHECK (0-100)          │  │ │ │
│  │  │  │  summary: TEXT (nullable)                                │  │ │ │
│  │  │  │  status: VARCHAR(20) DEFAULT 'completed'                │  │ │ │
│  │  │  │  modules_run: TEXT (JSON array, nullable)               │  │ │ │
│  │  │  │  results_json: TEXT (nullable)                          │  │ │ │
│  │  │  │  progress: INTEGER DEFAULT 0                              │  │ │ │
│  │  │  │  current_module: VARCHAR(50) (nullable)                  │  │ │ │
│  │  │  │  created_at: DATETIME TIMESTAMP DEFAULT NOW()            │  │ │ │
│  │  │  └────────────────────────────────────────────────────────────┘  │ │ │
│  │  └──────────────────────────────────────────────────────────────────────┘ │ │
│  │                                                                        │ │
│  │  ┌──────────────────────────────────────────────────────────────────────┐ │ │
│  │  │                            audit_logs                               │ │ │
│  │  │  ┌────────────────────────────────────────────────────────────┐  │ │ │
│  │  │  │  id: INTEGER PRIMARY KEY AUTOINCREMENT                    │  │ │ │
│  │  │  │  user_id: INTEGER (FK → users.id) ON DELETE SET NULL     │  │ │ │
│  │  │  │  action: VARCHAR(100) NOT NULL INDEX                     │  │ │ │
│  │  │  │  resource_type: VARCHAR(50) (nullable)                    │  │ │ │
│  │  │  │  resource_id: INTEGER (nullable)                          │  │ │ │
│  │  │  │  details: TEXT (nullable)                                │  │ │ │
│  │  │  │  ip_address: VARCHAR(45) (nullable)                       │  │ │ │
│  │  │  │  user_agent: VARCHAR(512) (nullable)                     │  │ │ │
│  │  │  │  created_at: DATETIME TIMESTAMP DEFAULT NOW() INDEX     │  │ │ │
│  │  │  └────────────────────────────────────────────────────────────┘  │ │ │
│  │  └──────────────────────────────────────────────────────────────────────┘ │ │
│  │                                                                        │ │
│  │  ┌──────────────────────────────────────────────────────────────────────┐ │ │
│  │  │                          share_tokens                               │ │ │
│  │  │  ┌────────────────────────────────────────────────────────────┐  │ │ │
│  │  │  │  id: INTEGER PRIMARY KEY AUTOINCREMENT                    │  │ │ │
│  │  │  │  report_id: INTEGER (FK → reports.id) ON DELETE CASCADE │  │ │ │
│  │  │  │  token: VARCHAR(64) UNIQUE NOT NULL INDEX                 │  │ │ │
│  │  │  │  expires_at: DATETIME (nullable)                         │  │ │ │
│  │  │  │  view_count: INTEGER DEFAULT 0                          │  │ │ │
│  │  │  │  created_by: INTEGER (FK → users.id) ON DELETE CASCADE  │  │ │ │
│  │  │  │  created_at: DATETIME TIMESTAMP DEFAULT NOW()            │  │ │ │
│  │  │  └────────────────────────────────────────────────────────────┘  │ │ │
│  │  └──────────────────────────────────────────────────────────────────────┘ │ │
│  │                                                                        │ │
│  │  ┌──────────────────────────────────────────────────────────────────────┐ │ │
│  │  │                         scheduled_tests                             │ │ │
│  │  │  ┌────────────────────────────────────────────────────────────┐  │ │ │
│  │  │  │  id: INTEGER PRIMARY KEY AUTOINCREMENT                    │  │ │ │
│  │  │  │  user_id: INTEGER (FK → users.id) ON DELETE CASCADE      │  │ │ │
│  │  │  │  name: VARCHAR(255) NOT NULL                            │  │ │ │
│  │  │  │  url: VARCHAR(2048) NOT NULL                              │  │ │ │
│  │  │  │  modules: TEXT NOT NULL (JSON array)                     │  │ │ │
│  │  │  │  cron_expression: VARCHAR(100) (nullable)               │  │ │ │
│  │  │  │  is_active: BOOLEAN DEFAULT TRUE                         │  │ │ │
│  │  │  │  last_run: DATETIME (nullable)                          │  │ │ │
│  │  │  │  next_run: DATETIME (nullable)                           │  │ │ │
│  │  │  │  created_at: DATETIME TIMESTAMP DEFAULT NOW()            │  │ │ │
│  │  │  └────────────────────────────────────────────────────────────┘  │ │ │
│  │  └──────────────────────────────────────────────────────────────────────┘ │ │
│  │                                                                        │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 5.3 Data Dictionary

### 5.3.1 Table: users

| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique user identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL, INDEX | User email address |
| username | VARCHAR(100) | UNIQUE, NOT NULL, INDEX | User display name |
| hashed_password | VARCHAR(255) | NOT NULL | bcrypt hashed password |
| is_active | BOOLEAN | DEFAULT TRUE, NOT NULL | Account active status |
| is_admin | BOOLEAN | DEFAULT FALSE, NOT NULL | Admin role flag |
| created_at | DATETIME | DEFAULT NOW(), NOT NULL | Account creation timestamp |
| last_login | DATETIME | NULL | Last login timestamp |

### 5.3.2 Table: reports

| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique report identifier |
| user_id | INTEGER | FK → users.id, ON DELETE CASCADE, INDEX | Owner user ID |
| title | VARCHAR(255) | NOT NULL | Report title |
| url | VARCHAR(2048) | NOT NULL | Tested website URL |
| file_path | VARCHAR(512) | NULL | Path to HTML report file |
| json_path | VARCHAR(512) | NULL | Path to JSON report file |
| overall_score | INTEGER | NULL, CHECK(0-100) | Overall score (0-100) |
| summary | TEXT | NULL | Test summary text |
| status | VARCHAR(20) | DEFAULT 'completed', NOT NULL | Status: pending/running/completed/failed |
| modules_run | TEXT | NULL | JSON array of module IDs |
| results_json | TEXT | NULL | Full test results as JSON |
| progress | INTEGER | DEFAULT 0, NOT NULL | Progress percentage (0-100) |
| current_module | VARCHAR(50) | NULL | Currently running module name |
| created_at | DATETIME | DEFAULT NOW(), NOT NULL | Report creation timestamp |

### 5.3.3 Table: audit_logs

| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique log identifier |
| user_id | INTEGER | FK → users.id, ON DELETE SET NULL, INDEX | User who performed action (nullable for anonymous) |
| action | VARCHAR(100) | NOT NULL, INDEX | Action type (login, logout, test_start, etc.) |
| resource_type | VARCHAR(50) | NULL | Type of resource affected (user, report, etc.) |
| resource_id | INTEGER | NULL | ID of affected resource |
| details | TEXT | NULL | Additional details as JSON |
| ip_address | VARCHAR(45) | NULL | Client IP address |
| user_agent | VARCHAR(512) | NULL | Client user agent string |
| created_at | DATETIME | DEFAULT NOW(), NOT NULL, INDEX | Log timestamp |

### 5.3.4 Table: share_tokens

| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique token identifier |
| report_id | INTEGER | FK → reports.id, ON DELETE CASCADE, INDEX | Associated report ID |
| token | VARCHAR(64) | UNIQUE, NOT NULL, INDEX | Share token string |
| expires_at | DATETIME | NULL | Token expiration timestamp |
| view_count | INTEGER | DEFAULT 0, NOT NULL | Number of views |
| created_by | INTEGER | FK → users.id, ON DELETE CASCADE | User who created token |
| created_at | DATETIME | DEFAULT NOW(), NOT NULL | Token creation timestamp |

### 5.3.5 Table: scheduled_tests

| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique schedule identifier |
| user_id | INTEGER | FK → users.id, ON DELETE CASCADE, INDEX | Owner user ID |
| name | VARCHAR(255) | NOT NULL | Schedule name |
| url | VARCHAR(2048) | NOT NULL | URL to test |
| modules | TEXT | NOT NULL | JSON array of module IDs |
| cron_expression | VARCHAR(100) | NULL | Cron schedule expression |
| is_active | BOOLEAN | DEFAULT TRUE, NOT NULL | Schedule active status |
| last_run | DATETIME | NULL | Last execution timestamp |
| next_run | DATETIME | NULL | Next execution timestamp |
| created_at | DATETIME | DEFAULT NOW(), NOT NULL | Schedule creation timestamp |

## 5.4 Relationships

| Relationship | Type | Description |
|-------------|------|-------------|
| users → reports | 1:N | One user can have many reports |
| users → audit_logs | 1:N | One user can have many audit log entries |
| users → share_tokens | 1:N | One user can create many share tokens |
| users → scheduled_tests | 1:N | One user can have many scheduled tests |
| reports → share_tokens | 1:N | One report can have many share tokens |

## 5.5 Constraints

### Primary Keys
- `users.id` - Unique identifier for each user
- `reports.id` - Unique identifier for each report
- `audit_logs.id` - Unique identifier for each log entry
- `share_tokens.id` - Unique identifier for each token
- `scheduled_tests.id` - Unique identifier for each schedule

### Unique Constraints
- `users.email` - Email must be unique
- `users.username` - Username must be unique
- `share_tokens.token` - Token must be unique

### Foreign Key Constraints
- `reports.user_id` → `users.id` ON DELETE CASCADE
- `audit_logs.user_id` → `users.id` ON DELETE SET NULL
- `share_tokens.report_id` → `reports.id` ON DELETE CASCADE
- `share_tokens.created_by` → `users.id` ON DELETE CASCADE
- `scheduled_tests.user_id` → `users.id` ON DELETE CASCADE

### Check Constraints
- `reports.overall_score` CHECK (overall_score >= 0 AND overall_score <= 100)

## 5.6 Indexes

| Table | Column(s) | Type | Purpose |
|-------|-----------|------|---------|
| users | email | INDEX | Fast email lookup |
| users | username | INDEX | Fast username lookup |
| reports | user_id | INDEX | Fast user report lookup |
| audit_logs | user_id | INDEX | Fast user activity lookup |
| audit_logs | action | INDEX | Fast action filtering |
| audit_logs | created_at | INDEX | Fast date range queries |
| share_tokens | token | INDEX | Fast token validation |
| share_tokens | report_id | INDEX | Fast report share lookup |
| scheduled_tests | user_id | INDEX | Fast user schedule lookup |

## 5.7 Normalization

| Table | Normal Form | Status |
|-------|-------------|--------|
| users | 3NF | ✓ |
| reports | 3NF | ✓ |
| audit_logs | 3NF | ✓ |
| share_tokens | 3NF | ✓ |
| scheduled_tests | 3NF | ✓ |

### Normalization Justification:

1. **First Normal Form (1NF)**: All tables have atomic values, no repeating groups.

2. **Second Normal Form (2NF)**: All non-key attributes fully depend on the primary key.

3. **Third Normal Form (3NF)**: No transitive dependencies. For example:
   - `users.is_admin` depends directly on `users.id`, not on `users.email`
   - `reports.overall_score` depends directly on `reports.id`, not on `reports.user_id`

---

# CHƯƠNG 6: THIẾT KẾ GIAO DIỆN

## 6.1 Dashboard Page (/)

| Thuộc tính | Nội dung |
|------------|----------|
| **Tên màn hình** | Dashboard - Trang chủ |
| **Chức năng** | Hiển thị tổng quan hệ thống, module testing cards, và recent tests |
| **Thành phần** | - Header với user info<br>- Stats row (total tests, completed, avg score, modules)<br>- Module cards grid (8 modules)<br>- Recent tests list<br>- Quick actions |
| **Input** | User session, reports from database |
| **Output** | HTML dashboard với Tailwind CSS styling |
| **Luồng xử lý** | 1. Load user session<br>2. Fetch recent reports<br>3. Calculate stats<br>4. Render template |

```
<< CHÈN HÌNH TẠI ĐÂY >>
Mô tả: Giao diện Dashboard với module cards và stats
```

## 6.2 Login Page (/login)

| Thuộc tính | Nội dung |
|------------|----------|
| **Tên màn hình** | Login - Trang đăng nhập |
| **Chức năng** | Xác thực người dùng, cấp JWT tokens |
| **Thành phần** | - Logo/Brand<br>- Email/Username field<br>- Password field<br>- Remember me checkbox<br>- Login button<br>- Register link |
| **Input** | email, password |
| **Output** | Redirect to Dashboard hoặc error message |
| **Luồng xử lý** | 1. Validate form<br>2. Check rate limit<br>3. Authenticate user<br>4. Create tokens<br>5. Set cookies<br>6. Redirect |

```
<< CHÈN HÌNH TẠI ĐÂY >>
Mô tả: Giao diện trang đăng nhập
```

## 6.3 Register Page (/register)

| Thuộc tính | Nội dung |
|------------|----------|
| **Tên màn hình** | Register - Trang đăng ký |
| **Chức năng** | Tạo tài khoản mới |
| **Thành phần** | - Email field<br>- Username field<br>- Password field<br>- Confirm password field<br>- Register button<br>- Login link |
| **Input** | email, username, password, confirm_password |
| **Output** | Redirect to login với success message |
| **Luồng xử lý** | 1. Validate form<br>2. Check password strength<br>3. Check uniqueness<br>4. Hash password<br>5. Create user<br>6. Redirect to login |

```
<< CHÈN HÌNH TẠI ĐÂY >>
Mô tả: Giao diện trang đăng ký
```

## 6.4 New Test Page (/test/new)

| Thuộc tính | Nội dung |
|------------|----------|
| **Tên màn hình** | New Test - Trang tạo test mới |
| **Chức năng** | Tạo bài kiểm thử website mới |
| **Thành phần** | - URL input field<br>- Module selection (checkboxes)<br>- Advanced options (max_depth, max_pages, viewport)<br>- Run Test button |
| **Input** | url, modules[], max_depth, max_pages, viewport |
| **Output** | Redirect to results page |
| **Luồng xử lý** | 1. Validate URL<br>2. Validate modules<br>3. Create report record<br>4. Queue background task<br>5. Redirect to results |

```
<< CHÈN HÌNH TẠI ĐÂY >>
Mô tả: Giao diện trang tạo test mới
```

## 6.5 Results Page (/results/{id})

| Thuộc tính | Nội dung |
|------------|----------|
| **Tên màn hình** | Results - Trang kết quả test |
| **Chức năng** | Hiển thị chi tiết kết quả kiểm thử |
| **Thành phần** | - Overall score ring<br>- Module scores cards<br>- Issues list<br>- Recommendations<br>- Actions (download, share, compare) |
| **Input** | report_id, results_json |
| **Output** | HTML results page |
| **Luồng xử lý** | 1. Load report from DB<br>2. Parse results JSON<br>3. Calculate scores<br>4. Render template |

```
<< CHÈN HÌNH TẠI ĐÂY >>
Mô tả: Giao diện trang kết quả test
```

## 6.6 History Page (/history)

| Thuộc tính | Nội dung |
|------------|----------|
| **Tên màn hình** | History - Trang lịch sử test |
| **Chức năng** | Xem danh sách các bài test đã thực hiện |
| **Thành phần** | - Filter options<br>- Test list table<br>- Pagination<br>- Quick actions |
| **Input** | User session |
| **Output** | HTML history page |
| **Luồng xử lý** | 1. Load user reports<br>2. Apply filters<br>3. Render table |

```
<< CHÈN HÌNH TẠI ĐÂY >>
Mô tả: Giao diện trang lịch sử test
```

## 6.7 Analytics Page (/analytics)

| Thuộc tính | Nội dung |
|------------|----------|
| **Tên màn hình** | Analytics - Trang phân tích |
| **Chức năng** | Hiển thị thống kê và xu hướng |
| **Thành phần** | - Stats overview<br>- Score trend chart<br>- Module usage chart<br>- Test frequency chart<br>- Recent activity |
| **Input** | User session, analytics data |
| **Output** | HTML analytics dashboard |
| **Luồng xử lý** | 1. Calculate stats<br>2. Fetch trends<br>3. Render charts |

```
<< CHÈN HÌNH TẠI ĐÂY >>
Mô tả: Giao diện trang analytics
```

## 6.8 Compare Page (/compare)

| Thuộc tính | Nội dung |
|------------|----------|
| **Tên màn hình** | Compare - Trang so sánh báo cáo |
| **Chức năng** | So sánh kết quả của 2 bài test |
| **Thành phần** | - Report selector (2 dropdowns)<br>- Comparison view<br>- Score difference<br>- Issues comparison |
| **Input** | report1_id, report2_id |
| **Output** | HTML comparison page |
| **Luồng xử lý** | 1. Load 2 reports<br>2. Calculate differences<br>3. Render comparison |

```
<< CHÈN HÌNH TẠI ĐÂY >>
Mô tả: Giao diện trang so sánh báo cáo
```

## 6.9 Admin Users Page (/admin/users)

| Thuộc tính | Nội dung |
|------------|----------|
| **Tên màn hình** | Admin Users - Trang quản lý người dùng |
| **Chức năng** | Quản lý tài khoản người dùng (Admin only) |
| **Thành phần** | - Users table<br>- User actions (edit, delete)<br>- Create user button |
| **Input** | Admin session |
| **Output** | HTML admin page |
| **Luồng xử lý** | 1. Verify admin role<br>2. Load all users<br>3. Render table |

```
<< CHÈN HÌNH TẠI ĐÂY >>
Mô tả: Giao diện trang quản lý users (Admin)
```

## 6.10 Shared Report Page (/share/{token})

| Thuộc tính | Nội dung |
|------------|----------|
| **Tên màn hình** | Shared Report - Trang xem báo cáo chia sẻ |
| **Chức năng** | Xem báo cáo công khai qua link (không cần đăng nhập) |
| **Thành phần** | - Report summary<br>- Scores overview<br>- Public view only |
| **Input** | share_token |
| **Output** | HTML shared report page |
| **Luồng xử lý** | 1. Validate token<br>2. Check expiration<br>3. Increment view count<br>4. Load report<br>5. Render template |

```
<< CHÈN HÌNH TẠI ĐÂY >>
Mô tả: Giao diện trang shared report
```

---

# CHƯƠNG 7: XÂY DỰNG HỆ THỐNG

## 7.1 Technology Stack

### Backend

| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.11+ | Programming language |
| FastAPI | 0.110.0 | Web framework |
| Uvicorn | 0.27.1 | ASGI server |
| SQLAlchemy | 2.0.29 | ORM |
| Alembic | 1.13.1 | Database migrations |
| Playwright | 1.42.0 | Browser automation |
| Pydantic | 2.10+ | Data validation |
| python-jose | - | JWT handling |
| passlib | - | Password hashing (bcrypt) |

### Frontend

| Technology | Version | Purpose |
|-----------|---------|---------|
| Jinja2 | 3.1.4 | Template engine |
| Tailwind CSS | CDN | Styling |
| Lucide Icons | CDN | Icons |
| Vanilla JavaScript | - | Client-side logic |

### Database

| Technology | Version | Purpose |
|-----------|---------|---------|
| SQLite | - | Primary database |
| File System | - | Report storage |

### Testing

| Technology | Version | Purpose |
|-----------|---------|---------|
| pytest | 8.1.1 | Testing framework |
| pytest-asyncio | - | Async testing |
| pytest-cov | - | Coverage reporting |

## 7.2 Source Structure

```
webtesterpro/
├── webtesterpro/
│   ├── __init__.py
│   ├── database.py              # Database configuration
│   │
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── auth.py              # JWT, password hashing, rate limiting
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── crud.py              # Database operations
│   │   ├── router.py            # Auth API routes
│   │   ├── schemas.py           # Pydantic schemas
│   │   └── dependencies.py       # FastAPI dependencies
│   │
│   ├── core/
│   │   ├── config.py            # Configuration management
│   │   └── engine.py            # WebTesterEngine core
│   │
│   ├── dashboard/
│   │   ├── __init__.py
│   │   ├── main.py              # Dashboard routes
│   │   ├── constants.py         # Module definitions
│   │   ├── dependencies.py       # Page dependencies
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── test_runner.py   # Test execution service
│   │   │   ├── audit_service.py # Audit logging
│   │   │   ├── analytics_service.py # Analytics
│   │   │   ├── export_service.py # Export reports
│   │   │   ├── compare_service.py # Compare reports
│   │   │   └── sse_manager.py  # SSE management
│   │   │
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   └── results_parser.py # Parse test results
│   │   │
│   │   ├── templates/           # Jinja2 templates
│   │   │   ├── base.html
│   │   │   ├── index.html
│   │   │   ├── login.html
│   │   │   ├── register.html
│   │   │   ├── new_test.html
│   │   │   ├── results.html
│   │   │   ├── history.html
│   │   │   ├── analytics.html
│   │   │   ├── compare.html
│   │   │   ├── shared_report.html
│   │   │   ├── admin_users.html
│   │   │   └── partials/
│   │   │
│   │   └── static/
│   │       ├── manifest.json
│   │       ├── sw.js
│   │       └── js/
│   │           ├── toast.js
│   │           ├── shortcuts.js
│   │           ├── tour.js
│   │           └── url-validator.js
│   │
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── crawler/             # Website crawler
│   │   ├── scanner/              # Website scanner
│   │   ├── analyzer/            # General analyzer
│   │   ├── monitor/             # Uptime monitor
│   │   ├── performance/         # Performance testing
│   │   ├── security/            # Security scanning
│   │   ├── accessibility/       # Accessibility checking
│   │   ├── seo/                 # SEO analysis
│   │   ├── visual/              # Visual testing
│   │   └── reporting/           # Report generation
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py          # Pytest configuration
│   │   ├── unit/
│   │   │   ├── test_crawler.py
│   │   │   ├── test_config.py
│   │   │   ├── test_accessibility.py
│   │   │   ├── test_performance.py
│   │   │   ├── test_seo.py
│   │   │   ├── test_security.py
│   │   │   ├── test_reporting.py
│   │   │   └── test_visual.py
│   │   └── integration/
│   │       └── __init__.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py
│   │
│   ├── utils/
│   │   └── __init__.py
│   │
│   └── reports/
│       ├── dashboard/           # Dashboard reports
│       └── *.json, *.html      # Historical reports
│
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/                # Migration versions
│       ├── 001_create_users_and_reports.py
│       ├── 002_add_report_status_fields.py
│       ├── 003_add_progress_fields.py
│       ├── 004_add_audit_scheduled_share.py
│       └── 005_add_scheduled_share.py
│
├── data/                        # SQLite database
├── logs/                        # Application logs
├── requirements.txt
├── config.yaml
├── alembic.ini
├── .env.example
└── README.md
```

## 7.3 API Documentation

### Authentication Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | /auth/register | Register new user | No |
| POST | /auth/login | Login user | No |
| POST | /auth/logout | Logout user | Yes |
| POST | /auth/refresh | Refresh access token | No |
| GET | /auth/me | Get current user info | Yes |
| GET | /auth/users | List all users | Admin |

### Dashboard Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | / | Dashboard homepage | Yes |
| GET | /login | Login page | No |
| GET | /register | Register page | No |
| POST | /login | Login form submit | No |
| POST | /register | Register form submit | No |
| POST | /logout | Logout | Yes |
| GET | /test/new | New test form | Yes |
| POST | /test/new | Submit new test | Yes |
| GET | /results/{id} | View results | Yes |
| GET | /results/{id}/progress | Get progress | Yes |
| GET | /results/{id}/stream | SSE stream | Yes |
| GET | /results/{id}/status | Partial status | Yes |
| GET | /results/{id}/download | Download report | Yes |
| POST | /results/{id}/share | Create share link | Yes |
| GET | /share/{token} | View shared report | No |
| GET | /history | Test history | Yes |
| GET | /analytics | Analytics dashboard | Yes |
| GET | /compare | Compare page | Yes |
| GET | /admin/users | Admin user management | Admin |

### API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /api/reports | List reports | Yes |
| GET | /api/analytics | Get analytics data | Yes |
| GET | /api/compare/{id1}/{id2} | Compare reports | Yes |

## 7.4 Module Description

### SEO Analyzer Module

```python
class SEOAnalyzer:
    """Analyzes website SEO factors."""
    
    async def analyze(self, url: str, check_keyword_density: bool = False) -> Dict:
        """
        Perform SEO analysis on URL.
        
        Checks:
        - Title tag (length 50-60 chars)
        - Meta description (length 150-160 chars)
        - Heading structure (H1-H6)
        - Open Graph tags
        - Schema.org markup
        - Image alt text
        - Internal/external links
        """
```

### Performance Tester Module

```python
class PerformanceTester:
    """Tests website performance metrics."""
    
    async def test_performance(self, url: str, wait_until: str = "networkidle") -> Dict:
        """
        Test URL performance.
        
        Measures:
        - LCP (Largest Contentful Paint)
        - FID/INP (First Input Delay)
        - CLS (Cumulative Layout Shift)
        - TTFB (Time to First Byte)
        - FCP (First Contentful Paint)
        - Resource loading
        """
```

### Security Scanner Module

```python
class SecurityScanner:
    """Scans website for security issues."""
    
    async def scan(self, url: str, check_xss: bool = True, 
                   check_sqli: bool = True, check_sensitive: bool = True) -> Dict:
        """
        Perform security scan.
        
        Checks:
        - Security headers (CSP, HSTS, X-Frame-Options, etc.)
        - SSL/TLS configuration
        - Sensitive file exposure
        - XSS patterns
        - SQL injection patterns
        - CORS misconfiguration
        - Clickjacking vulnerability
        """
```

### Accessibility Checker Module

```python
class AccessibilityChecker:
    """Checks website accessibility (WCAG 2.1)."""
    
    async def check(self, url: str, run_axe: bool = True, 
                    run_manual: bool = True) -> Dict:
        """
        Check accessibility.
        
        Uses:
        - axe-core automated testing
        - WCAG 2.1 criteria
        - Color contrast checking
        - Alt text validation
        - ARIA attribute verification
        """
```

## 7.5 Business Logic Analysis

### Authentication Flow

```
1. User submits login form
2. System validates credentials:
   - Check email/username exists
   - Verify password against hash
   - Check account is active
   - Check rate limit
3. Generate JWT tokens:
   - Access token (30 min) with user_id
   - Refresh token (7 days) with user_id
4. Set HttpOnly cookies
5. Log audit entry
6. Redirect to dashboard
```

### Test Execution Flow

```
1. User submits test form
2. System validates:
   - URL format
   - At least 1 module selected
3. Create Report record with status="running"
4. Start background task:
   - Initialize WebTesterEngine
   - Launch Playwright browser
   - For each module:
     - Run module test
     - Update progress in DB
     - Emit SSE event
   - Calculate overall score
   - Save results to JSON file
   - Update Report record
   - Emit completion event
5. User redirected to results page
6. SSE updates show real-time progress
```

### Score Calculation

```
Overall Score = Average of module scores

Module Scores:
- SEO Score = weighted average of:
  - Title (15%), Meta tags (15%), Headings (15%),
  - Images (15%), Links (10%), Content (15%), Technical (15%)

- Performance Score = weighted average of:
  - LCP (25%), CLS (25%), FID (25%),
  - TTFB (15%), TBT (10%)

- Security Score = 100 - penalties
  where penalty = Critical×30 + High×20 + Medium×10 + Low×5

- Accessibility Score = 100 - penalties
  where penalty = Critical×15 + Serious×10 + Moderate×5 + Minor×1
```

---

# CHƯƠNG 8: KIỂM THỬ HỆ THỐNG

## 8.1 Test Strategy

### 8.1.1 Test Levels

| Level | Scope | Purpose |
|-------|-------|---------|
| Unit Testing | Individual modules | Verify isolated functionality |
| Integration Testing | Module interactions | Verify module integration |
| System Testing | Complete system | Verify end-to-end functionality |
| Acceptance Testing | User requirements | Verify business requirements |

### 8.1.2 Test Types

| Type | Focus | Tools |
|------|-------|-------|
| Functional Testing | Features & functions | pytest |
| Security Testing | Authentication, authorization | Manual + tools |
| Performance Testing | Load time, concurrency | pytest-benchmark |
| Regression Testing | Existing functionality | pytest |

## 8.2 Test Plan

### 8.2.1 Unit Test Cases

| Module | Test Case | Description | Expected Result |
|--------|-----------|------------|----------------|
| Auth | TC-AUTH-001 | User registration with valid data | User created |
| Auth | TC-AUTH-002 | User registration with duplicate email | Error message |
| Auth | TC-AUTH-003 | User registration with weak password | Error message |
| Auth | TC-AUTH-004 | Login with valid credentials | Token generated |
| Auth | TC-AUTH-005 | Login with invalid password | Error message |
| Auth | TC-AUTH-006 | Rate limit after 5 failures | Account locked |
| Auth | TC-AUTH-007 | Token refresh | New token generated |
| Reports | TC-RPT-001 | Create new report | Report created with status="running" |
| Reports | TC-RPT-002 | View report results | Results displayed |
| Reports | TC-RPT-003 | Download report as JSON | JSON file downloaded |
| Reports | TC-RPT-004 | Create share link | Token generated |
| SEO | TC-SEO-001 | Analyze page with meta tags | Score calculated |
| SEO | TC-SEO-002 | Detect missing title | Issue recorded |
| Performance | TC-PERF-001 | Measure page load time | Metrics captured |
| Performance | TC-PERF-002 | Capture Core Web Vitals | LCP, CLS, FID measured |
| Security | TC-SEC-001 | Scan for security headers | Headers checked |
| Security | TC-SEC-002 | Detect missing CSP | Issue recorded |
| Accessibility | TC-A11Y-001 | Run axe-core scan | Violations reported |
| Accessibility | TC-A11Y-002 | Check color contrast | Contrast ratio calculated |

### 8.2.2 Integration Test Cases

| ID | Test Case | Description |
|----|-----------|------------|
| IT-001 | End-to-end test creation | Create test → Run → View results |
| IT-002 | Authentication flow | Register → Login → Logout |
| IT-003 | Report sharing | Create report → Share → View shared |
| IT-004 | SSE progress updates | Create test → Receive progress via SSE |

## 8.3 RTM (Requirements Traceability Matrix)

| Requirement | Use Case | API | Test Case |
|-------------|----------|-----|-----------|
| FR-001.1: Đăng ký tài khoản | UC-001 | POST /auth/register | TC-AUTH-001, TC-AUTH-002, TC-AUTH-003 |
| FR-001.2: Đăng nhập | UC-002 | POST /auth/login | TC-AUTH-004, TC-AUTH-005, TC-AUTH-006 |
| FR-001.3: Đăng xuất | UC-003 | POST /auth/logout | - |
| FR-002.1: Tạo test mới | UC-005 | POST /test/new | TC-RPT-001 |
| FR-002.3: Xem kết quả | UC-006 | GET /results/{id} | TC-RPT-002 |
| FR-002.4: Tải kết quả | UC-008 | GET /results/{id}/download | TC-RPT-003 |
| FR-004.4: Tạo share link | UC-009 | POST /results/{id}/share | TC-RPT-004 |
| FR-005.1: Thống kê tổng quan | - | GET /api/analytics | - |
| FR-003.1: SEO Analysis | UC-016 | Internal | TC-SEO-001, TC-SEO-002 |
| FR-003.2: Performance Test | UC-017 | Internal | TC-PERF-001, TC-PERF-002 |
| FR-003.3: Security Scan | UC-018 | Internal | TC-SEC-001, TC-SEC-002 |
| FR-003.4: Accessibility Check | UC-019 | Internal | TC-A11Y-001, TC-A11Y-002 |

## 8.4 Functional Test Cases (20+ cases)

### Authentication Tests

| ID | Test Case | Steps | Expected Result |
|----|-----------|-------|-----------------|
| TC-001 | Register with valid data | 1. Navigate to /register<br>2. Fill email, username, password<br>3. Click Register | Redirect to /login with success message |
| TC-002 | Register with existing email | 1. Navigate to /register<br>2. Use existing email<br>3. Submit form | Error: "Email đã được sử dụng" |
| TC-003 | Register with weak password | 1. Navigate to /register<br>2. Enter password without uppercase<br>3. Submit form | Error: "Mật khẩu phải có ít nhất 1 chữ hoa" |
| TC-004 | Login with valid credentials | 1. Navigate to /login<br>2. Enter correct email/password<br>3. Click Login | Redirect to / with user info displayed |
| TC-005 | Login with wrong password | 1. Navigate to /login<br>2. Enter wrong password<br>3. Submit | Error: "Email hoặc mật khẩu không đúng" |
| TC-006 | Rate limit after failures | 1. Login 5 times with wrong password<br>2. Try to login again | Error: "Quá nhiều lần thử. Thử lại sau 15 phút" |
| TC-007 | Logout | 1. Login<br>2. Click Logout | Redirect to /login, tokens cleared |
| TC-008 | Access dashboard without login | 1. Navigate to / without session | Redirect to /login |

### Test Creation Tests

| ID | Test Case | Steps | Expected Result |
|----|-----------|-------|-----------------|
| TC-010 | Create test with valid URL | 1. Login<br>2. Navigate to /test/new<br>3. Enter valid URL<br>4. Select modules<br>5. Submit | Redirect to /results/{id} with progress |
| TC-011 | Create test with invalid URL | 1. Login<br>2. Navigate to /test/new<br>3. Enter invalid URL<br>4. Submit | Error: "URL không hợp lệ" |
| TC-012 | Create test without modules | 1. Login<br>2. Navigate to /test/new<br>3. Enter URL<br>4. Don't select any module<br>5. Submit | Error: "Vui lòng chọn ít nhất một module" |
| TC-013 | View test progress via SSE | 1. Create test<br>2. Watch progress bar | Progress updates in real-time |
| TC-014 | View completed test results | 1. Wait for test to complete<br>2. View results page | Scores and issues displayed |

### SEO Module Tests

| ID | Test Case | Steps | Expected Result |
|----|-----------|-------|-----------------|
| TC-020 | Analyze page with SEO tags | 1. Run test with SEO module<br>2. Check results | Score based on SEO factors |
| TC-021 | Detect missing title | 1. Create test for page without title<br>2. Check SEO results | Issue: "Missing title tag" |
| TC-022 | Detect missing meta description | 1. Create test for page without meta<br>2. Check results | Issue: "Missing meta description" |
| TC-023 | Detect missing image alt | 1. Create test for page with images without alt<br>2. Check results | Issue: "Image missing alt attribute" |

### Performance Module Tests

| ID | Test Case | Steps | Expected Result |
|----|-----------|-------|-----------------|
| TC-030 | Measure page load time | 1. Run test with Performance module<br>2. Check results | Load time in milliseconds |
| TC-031 | Capture LCP metric | 1. Run test on page with LCP element<br>2. Check metrics | LCP value captured |
| TC-032 | Measure CLS | 1. Run test<br>2. Check CLS metric | CLS value calculated |
| TC-033 | Check FID | 1. Run test<br>2. Check FID metric | FID value captured |

### Security Module Tests

| ID | Test Case | Steps | Expected Result |
|----|-----------|-------|-----------------|
| TC-040 | Scan for security headers | 1. Run Security scan<br>2. Check headers | Missing headers reported |
| TC-041 | Detect missing CSP | 1. Run Security scan<br>2. Check CSP header | Issue if CSP missing |
| TC-042 | Detect XSS patterns | 1. Run Security scan<br>2. Check for XSS | Potential XSS reported |
| TC-043 | Check SSL/TLS | 1. Run Security scan on HTTPS site<br>2. Check SSL config | SSL info reported |

### Accessibility Module Tests

| ID | Test Case | Steps | Expected Result |
|----|-----------|-------|-----------------|
| TC-050 | Run axe-core scan | 1. Run Accessibility check<br>2. Check violations | WCAG violations reported |
| TC-051 | Check color contrast | 1. Run check on page<br>2. Check contrast | Contrast ratio calculated |
| TC-052 | Check alt text | 1. Run check<br>2. Verify alt attributes | Missing alt reported |

### Report Tests

| ID | Test Case | Steps | Expected Result |
|----|-----------|-------|-----------------|
| TC-060 | Download report as JSON | 1. View completed report<br>2. Click Download JSON | JSON file downloaded |
| TC-061 | Download report as HTML | 1. View completed report<br>2. Click Download HTML | HTML file downloaded |
| TC-062 | Download report as CSV | 1. View completed report<br>2. Click Download CSV | CSV file downloaded |
| TC-063 | Create share link | 1. View report<br>2. Click Share<br>3. Enter expiration | Share URL generated |
| TC-064 | View shared report | 1. Open share URL (new browser)<br>2. View report | Report displayed without login |

### Analytics Tests

| ID | Test Case | Steps | Expected Result |
|----|-----------|-------|-----------------|
| TC-070 | View analytics dashboard | 1. Login<br>2. Navigate to /analytics | Stats and charts displayed |
| TC-071 | View score trend | 1. Go to analytics<br>2. Check trend chart | Score trend over time |
| TC-072 | View module usage | 1. Go to analytics<br>2. Check module stats | Module usage displayed |

### Admin Tests

| ID | Test Case | Steps | Expected Result |
|----|-----------|-------|-----------------|
| TC-080 | Access admin page as admin | 1. Login as admin<br>2. Navigate to /admin/users | User list displayed |
| TC-081 | Access admin page as regular user | 1. Login as regular user<br>2. Navigate to /admin/users | HTTP 403 Forbidden |
| TC-082 | View all reports as admin | 1. Login as admin<br>2. Navigate to /history | All users' reports displayed |

## 8.5 Security Testing

| Test | Description | Method |
|------|-------------|--------|
| Authentication Bypass | Test if protected routes accessible without login | Manual |
| SQL Injection | Test input fields for SQL injection | Automated |
| XSS | Test input fields for XSS payloads | Automated |
| CSRF | Test if CSRF protection works | Manual |
| Password Hashing | Verify password stored as hash | Code review |
| Session Management | Test token expiration | Automated |
| Rate Limiting | Test rate limit enforcement | Automated |

## 8.6 Performance Testing

| Test | Description | Threshold |
|------|-------------|-----------|
| Page Load Time | Homepage initial load | < 2 seconds |
| API Response Time | Login API response | < 500ms |
| Test Execution | Full test on example.com | < 60 seconds |
| Concurrent Users | Support 50 concurrent users | No errors |

## 8.7 Integration Testing

| Test | Description |
|------|-------------|
| E2E: Create and View Test | Create test → Wait → View results |
| E2E: Share and View | Create report → Share → View shared link |
| E2E: Authentication Flow | Register → Login → Logout |

## 8.8 UAT (User Acceptance Testing)

### UAT Scenarios

| ID | Scenario | Tester | Result |
|----|----------|--------|--------|
| UAT-01 | QA Engineer creates full test on company website | QA Team | Pass |
| UAT-02 | Developer fixes issues based on test results | Dev Team | Pass |
| UAT-03 | PM reviews analytics for project quality | PM | Pass |
| UAT-04 | Admin manages user accounts | Admin | Pass |
| UAT-05 | Non-technical user creates and shares report | End User | Pass |

---

# CHƯƠNG 9: ĐÁNH GIÁ VÀ HƯỚNG PHÁT TRIỂN

## 9.1 Kết quả đạt được

| Mục tiêu | Kết quả | Đánh giá |
|-----------|----------|----------|
| TO.1: Tích hợp 8 module kiểm thử | ✓ | Hoàn thành |
| TO.2: Quản lý và theo dõi tests | ✓ | Hoàn thành |
| TO.3: Dashboard trực quan | ✓ | Hoàn thành |
| TO.4: Xuất báo cáo đa định dạng | ✓ | Hoàn thành |
| TO.5: Chia sẻ kết quả | ✓ | Hoàn thành |
| TO.6: Analytics | ✓ | Hoàn thành |

## 9.2 Ưu điểm

| Ưu điểm | Mô tả |
|----------|--------|
| **Kiến trúc modular** | 8 module độc lập, dễ mở rộng |
| **Tự động hóa hoàn toàn** | Playwright automation giảm thời gian kiểm thử |
| **Giao diện hiện đại** | Dark theme với Tailwind CSS |
| **Real-time updates** | SSE cho progress updates |
| **Bảo mật** | JWT + bcrypt + rate limiting |
| **Chia sẻ linh hoạt** | Token-based share links |
| **Analytics dashboard** | Thống kê và xu hướng |
| **Testing coverage** | Unit tests + integration tests |

## 9.3 Hạn chế

| Hạn chế | Mô tả | Ảnh hưởng |
|---------|-------|-----------|
| **SQLite database** | Không phù hợp cho production đa người dùng | Cần migrate sang PostgreSQL |
| **Single-browser testing** | Chỉ test trên Chromium | Cần thêm Firefox, Safari |
| **Không có CI/CD** | Chưa tích hợp vào pipeline | Cần thêm CI/CD integration |
| **Manual scheduler** | Scheduled tests chưa tự động chạy | Cần background job system |
| **Không có notification** | Không có email/Slack alerts | Cần thêm notification system |

## 9.4 Technical Debt

| Item | Priority | Description |
|------|---------|-------------|
| TD-01 | Cao | Migrate SQLite → PostgreSQL cho production |
| TD-02 | Cao | Implement background job queue (Celery/Redis) |
| TD-03 | Trung bình | Thêm multi-browser testing (Firefox, Safari) |
| TD-04 | Trung bình | CI/CD pipeline (GitHub Actions) |
| TD-05 | Thấp | Thêm email/Slack notifications |
| TD-06 | Thấp | Performance monitoring (Prometheus/Grafana) |

## 9.5 Hướng phát triển

### Ngắn hạn (1-3 tháng)

| Feature | Priority | Description |
|---------|----------|-------------|
| PostgreSQL support | Cao | Thay SQLite bằng PostgreSQL |
| Background jobs | Cao | Celery/Redis cho scheduled tests |
| Multi-browser | Trung bình | Firefox, Safari, Edge support |
| API documentation | Trung bình | Swagger/OpenAPI docs |

### Trung hạn (3-6 tháng)

| Feature | Priority | Description |
|---------|----------|-------------|
| CI/CD integration | Cao | GitHub Actions pipeline |
| Notifications | Trung bình | Email, Slack, webhook alerts |
| Team collaboration | Trung bình | Team workspaces |
| Historical comparison | Trung bình | Compare across time periods |

### Dài hạn (6-12 tháng)

| Feature | Priority | Description |
|---------|----------|-------------|
| Cloud deployment | Cao | Docker, Kubernetes support |
| SaaS platform | Cao | Multi-tenant architecture |
| API marketplace | Trung bình | Public API for third-party |
| Mobile app | Thấp | React Native app |

---

# CHƯƠNG 10: PHỤ LỤC HÌNH ẢNH

## 10.1 Dashboard Page

```
<< CHÈN HÌNH TẠI ĐÂY >>
```

**Mô tả:**
- Giao diện Dashboard chính của WebTesterPro
- Hiển thị user greeting, stats tổng quan
- 8 module cards với icons và màu sắc
- Recent tests list
- Quick actions

## 10.2 Login Page

```
<< CHÈN HÌNH TẠI ĐÂY >>
```

**Mô tả:**
- Trang đăng nhập với form
- Email/Username và Password fields
- Logo và branding
- Link đến trang đăng ký

## 10.3 New Test Page

```
<< CHÈN HÌNH TẠI ĐÂY >>
```

**Mô tả:**
- Form tạo test mới
- URL input với validation
- Module selection checkboxes
- Advanced options dropdown

## 10.4 Results Page

```
<< CHÈN HÌNH TẠI ĐÂY >>
```

**Mô tả:**
- Overall score ring
- Module score cards
- Issues list với severity badges
- Recommendations
- Action buttons (download, share)

## 10.5 Analytics Page

```
<< CHÈN HÌNH TẠI ĐÂY >>
```

**Mô tả:**
- Stats overview cards
- Score trend chart
- Module usage chart
- Test frequency chart

## 10.6 Compare Page

```
<< CHÈN HÌNH TẠI ĐÂY >>
```

**Mô tả:**
- Report selector dropdowns
- Side-by-side comparison
- Score differences
- Issues comparison

## 10.7 Admin Users Page

```
<< CHÈN HÌNH TẠI ĐÂY >>
```

**Mô tả:**
- Users table với actions
- Admin-only access
- User management functionality

## 10.8 Shared Report Page

```
<< CHÈN HÌNH TẠI ĐÂY >>
```

**Mô tả:**
- Public view của report
- No login required
- Share link access

---

# KẾT LUẬN

## Tổng kết

Hệ thống **WebTesterPro** đã được xây dựng thành công với các tính năng chính:

1. **8 module kiểm thử toàn diện**: SEO, Performance, Security, Accessibility, Crawler, Visual, Monitor, Scanner
2. **Dashboard trực quan**: Giao diện web hiện đại với real-time updates
3. **Hệ thống báo cáo**: Xuất JSON, HTML, CSV và chia sẻ qua link
4. **Analytics**: Thống kê và xu hướng chất lượng website
5. **Bảo mật**: JWT authentication, bcrypt password hashing, rate limiting

## Điểm mạnh của hệ thống

- **Kiến trúc modular**: Dễ mở rộng và bảo trì
- **Tự động hóa**: Giảm 80% thời gian kiểm thử
- **Chuẩn hóa**: Áp dụng tiêu chuẩn quốc tế (WCAG 2.1, Core Web Vitals)
- **Mã nguồn mở**: Có thể tùy chỉnh theo nhu cầu

## Hướng phát triển tiếp theo

- Migration sang PostgreSQL cho production
- Implement background job system
- CI/CD pipeline integration
- Multi-browser testing support

---

**Báo cáo hoàn thành**

Ngày: 23/06/2026

---

*Document được tạo dựa trên phân tích source code thực tế của hệ thống WebTesterPro*
