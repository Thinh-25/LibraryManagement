# Thiết kế 12 nhóm chức năng Library Management System

Trạng thái: người dùng đã duyệt bằng yêu cầu “bắt đầi”; đã triển khai và kiểm chứng, xem docs/verification.md.
Nguồn: `docs/requirements-library.md`, trích từ DOCX người dùng cung cấp.

## Mục tiêu, phạm vi và hiện trạng

Xây đủ UC01–UC12: giao diện tiếng Việt, API hoạt động và lưu dữ liệu PostgreSQL, kiểm tra quyền tại backend. Tài liệu đề xuất giai đoạn ưu tiên nhưng yêu cầu hiện tại bao gồm toàn bộ 12 nhóm; chia thứ tự thi công không loại bỏ nhóm mở rộng.

Hiện chỉ có trang khởi động, healthcheck và kết nối SQLAlchemy. Database đang dùng là library_management trên 127.0.0.1:5432, baseline 0001_library_schema có 12 bảng nghiệp vụ và 35 bản ghi mẫu. ORM models, CRUD, auth, báo cáo chưa tồn tại. Giữ frontend localhost:5000 (strictPort), backend 127.0.0.1:8001, API /api/v1 và database 5432.

Không đưa thêm tự đăng ký, gia hạn lượt mượn, trả góp, cổng thanh toán, gửi thông báo/email, upload ảnh hoặc xuất Excel/PDF vào phạm vi này. Ảnh bìa dùng URL đã được kiểm tra; không fetch URL tùy ý từ backend.

## Phương án

Đề xuất: triển khai từng luồng đầy đủ từ UI đến database, bắt đầu bằng auth và ORM, sau đó master data, mượn/trả, đặt trước/phạt/báo cáo. Người dùng giao cách triển khai; đây là lựa chọn kỹ thuật đề xuất, chưa phải quyết định người dùng duyệt.

Phương án làm tất cả backend trước rồi toàn bộ UI sau sẽ phát hiện muộn vấn đề luồng thao tác. Phương án chỉ tạo màn hình dữ liệu giả không đáp ứng yêu cầu chức năng thật. Giữ monorepo và phân lớp hiện có; không chuyển framework.

## Những lựa chọn người dùng đã xác nhận

- Dùng server PostgreSQL local 5432 đang hiển thị trong pgAdmin.
- Khôi phục mật khẩu bằng yêu cầu để Admin xử lý, không gửi liên kết email.

## Quyết định đề xuất để duyệt

- Giữ mã vai trò trong database/API là ADMIN, THU_THU, DOC_GIA; UI hiển thị tiếng Việt. Không đổi dữ liệu vai trò sang LIBRARIAN/READER.
- Thẻ chỉ hợp lệ khi ACTIVE, chưa hết hạn và tài khoản độc giả đang hoạt động. Ngày hết hạn phải sau ngày cấp để khớp CHECK hiện có.
- Chưa áp dụng hạn mức số cuốn, chặn theo nợ phạt hoặc kỳ hạn mượn cố định vì tài liệu chưa quy định; thủ thư chọn hạn trả tương lai cho từng cuốn.
- Phạt nhập thủ công bởi Admin/Thủ thư, số tiền > 0, có lý do và liên kết lượt mượn. UI cảnh báo quá hạn/hỏng/mất, không tự đặt đơn giá phạt. Không tạo khoản phạt 0 đồng, không trả góp.
- Đặt trước theo FIFO: ngày đặt rồi id; chỉ yêu cầu đầu hàng đợi còn hiệu lực được chuyển READY khi có cuốn AVAILABLE. Thời gian nhận đề xuất 48 giờ, cấu hình qua môi trường. Không giữ riêng một cuốn vật lý; READY không đảm bảo giữ kho, khi xác nhận mượn vẫn kiểm tra/khóa cuốn thực tế. Staff có thể hủy yêu cầu không hợp lệ với xác nhận thao tác.
- Kết thúc thời hạn nhận: tự chuyển yêu cầu READY hết hạn sang CANCELLED khi xử lý hàng đợi; không yêu cầu background scheduler. Độc giả tạo lại yêu cầu nếu cần. Với schema hiện tại không có trạng thái EXPIRED cho đặt trước.
- Hoàn tất đặt trước gắn với phiếu mượn thực tế của chính độc giả, cùng đầu sách. Không cho staff chỉ bấm COMPLETED mà chưa có phiếu mượn tương ứng; phối hợp trong transaction.
- Không cho khóa/hạ quyền Admin đang đăng nhập hoặc Admin hoạt động cuối cùng. Tài khoản đang có phiếu mượn vẫn giữ lịch sử khi bị khóa, staff vẫn được xử lý trả.
- Tài khoản seed có hash placeholder không được phép đăng nhập. Cung cấp lệnh bootstrap đặt mật khẩu Admin cục bộ có nhập ẩn; không tự đặt mật khẩu chung hoặc in mật khẩu demo.

## UC01–UC02: tài khoản, xác thực, hồ sơ

UC01 chỉ Admin: danh sách tài khoản có tìm kiếm/phân trang, xem chi tiết, tạo THU_THU/DOC_GIA, sửa thông tin, đổi vai trò, khóa/mở khóa, đặt lại mật khẩu. Email chuẩn hóa và kiểm tra unique không phân biệt hoa thường. Không trả hash mật khẩu trong API.

UC02 mọi tài khoản hoạt động: đăng nhập, đăng xuất, xem/sửa hồ sơ bản thân, đổi mật khẩu với mật khẩu hiện tại. API hồ sơ không nhận vai trò/trạng thái để tránh tự nâng quyền. Mật khẩu hash Argon2id, JWT ngắn hạn được kiểm tra chữ ký và expiry.

Access token giữ trong bộ nhớ frontend (Zustand), không localStorage. Reload trang yêu cầu đăng nhập lại trong phiên bản này. Thêm auth_version vào tài khoản và kiểm tra ở mỗi request; khóa tài khoản, đổi mật khẩu, đổi quyền hoặc đăng xuất làm token cũ không còn hiệu lực. Đăng xuất toàn bộ phiên của tài khoản là hành vi đề xuất để tránh cần refresh/session table phức tạp.

Quên mật khẩu: form công khai nhận email, luôn trả cùng thông báo tránh tiết lộ tài khoản. Với tài khoản hợp lệ, lưu yêu cầu PENDING, không lặp yêu cầu đang chờ. Admin xem, đặt mật khẩu tạm qua cơ chế đặt lại và đánh dấu yêu cầu đã xử lý hoặc từ chối. Admin xác minh danh tính và giao mật khẩu cho người dùng qua kênh ngoài hệ thống; app không gửi email và không lưu plaintext password. Tài khoản bị reset buộc đổi mật khẩu khi đăng nhập tiếp; chỉ có quyền đổi mật khẩu/đăng xuất cho tới khi hoàn tất.

Thêm rate limit cho login/quên mật khẩu trên bản chạy một backend process, bằng số lần theo IP trong cửa sổ thời gian, trả 429. Chưa triển khai hạ tầng Redis phân tán.

## UC03: độc giả và thẻ

Admin/Thủ thư xem danh sách/chi tiết DOC_GIA, lịch sử mượn, cấp tối đa một thẻ, gia hạn thẻ, khóa/mở. Cấp thẻ chỉ cho DOC_GIA hoạt động. Trạng thái EXPIRED hiển thị theo ngày hết hạn kể cả khi cột trạng thái còn ACTIVE; không cho mượn bằng cách mở khóa thẻ đã hết hạn. Gia hạn phải đặt ngày mới sau ngày cấp và ngày hết hạn cũ.

Không thêm chức năng tự xóa tài khoản/độc giả có lịch sử. UC01 quản lý tài khoản; UC03 quản lý thẻ và thông tin/lịch sử độc giả theo quyền.

## UC04–UC06: sách, danh mục, tra cứu

Admin/Thủ thư CRUD thể loại, tác giả, NXB, đầu sách và bản sao. Danh sách có tìm kiếm, filter và pagination. Đầu sách liên kết nhiều tác giả; response có thể loại/NXB/tác giả và số cuốn AVAILABLE. Tra cứu theo tên/ISBN, lọc thể loại/tác giả/NXB dành cho cả ba vai trò đăng nhập.

Schema phân biệt sach và cuon_sach. Mã vạch unique theo bản sao; ISBN unique nếu có. Không xóa danh mục còn tham chiếu; không xóa đầu sách còn bản sao, đặt trước hoặc lịch sử tham chiếu. Khi xóa đầu sách không còn phụ thuộc, có thể xóa liên kết sach_tac_gia theo cascade hiện có. Không xóa bản sao có lịch sử mượn hoặc đang BORROWED. Trả lỗi nghiệp vụ rõ ràng thay vì lỗi SQL thô.

Thay đổi tình trạng bản sao bằng màn hình quản lý chỉ cho các trạng thái không BORROWED; chuyển vào/ra BORROWED bắt buộc đi qua nghiệp vụ mượn/trả. Không để sửa trạng thái phá nhất quán lượt mượn đang mở.

## UC07–UC08: mượn và trả

Tạo phiếu: chọn DOC_GIA hoạt động, thẻ hợp lệ, chọn ít nhất một cuốn không trùng và hạn trả tương lai từng cuốn. ID thủ thư lấy từ tài khoản đăng nhập, không tin id gửi từ client. Admin cũng được lập phiếu theo ma trận quyền. Khóa các cuốn theo thứ tự id ổn định, kiểm tra AVAILABLE, insert phieu_muon/chi_tiet_muon và cập nhật BORROWED trong cùng transaction. Unique index hiện có là lớp bảo vệ bổ sung; xung đột trả 409, không để tạo phiếu một phần.

Trả từng cuốn: khóa chi_tiet_muon và cuon_sach, chỉ cho lượt BORROWED. Ngày trả lấy server; quá hạn là ngày trả > han_tra. Tình trạng GOOD chuyển lượt RETURNED và cuốn AVAILABLE; DAMAGED chuyển lượt RETURNED và cuốn DAMAGED; LOST chuyển lượt LOST, ngay_tra=NULL theo CHECK và cuốn LOST. Không trả lần hai. Khoản phạt tùy chọn nhập lúc trả chỉ được > 0, có lý do, tạo trong cùng transaction. Báo mất là kết thúc xử lý cuốn đó; không tự mở cho mượn lại.

Theo tài liệu, hoàn tất đặt trước có thể được tích hợp vào cùng transaction lập phiếu khi staff chọn yêu cầu READY phù hợp; không tự hoàn tất yêu cầu của người khác.

## UC09–UC11: đặt trước, phạt và dữ liệu cá nhân

Độc giả chỉ tạo/xem/hủy đặt trước của mình; không nhận doc_gia_id tùy ý. Chặn hai yêu cầu PENDING/READY cùng đầu sách bằng quy tắc và index hiện có. Admin/Thủ thư xem hàng đợi và xử lý READY/CANCELLED/COMPLETED theo chính sách trên, không đặt thay độc giả.

Tiền phạt: staff xem/lọc/tạo khoản phạt; xác nhận thanh toán từ UNPAID sang PAID, ngày thanh toán từ server, khóa bản ghi tránh thu lần hai. Sau khi PAID không sửa số tiền, lý do hoặc thanh toán lần nữa trong phạm vi phiên bản này. Độc giả chỉ đọc các khoản phạt của mình.

Lượt mượn cá nhân: các cuốn đang mượn, quá hạn, lịch sử RETURNED/LOST và chi tiết; backend luôn giới hạn theo id đăng nhập. Admin/Thủ thư xem lịch sử độc giả qua UC03/UC07, không sử dụng route cá nhân dành riêng độc giả.

## UC12: dashboard và báo cáo

Admin/Thủ thư xem tổng số đầu sách, bản sao, độc giả, số cuốn đang mượn/quá hạn. Lượt mượn theo tháng/năm đếm chi_tiet_muon theo ngay_muon của phiếu; biểu đồ và sách phổ biến dùng cùng định nghĩa. Độc giả đếm tài khoản DOC_GIA; tổng và số hoạt động hiển thị riêng nếu cần. Phạt đã thu lọc theo ngay_thanh_toan; phạt chưa thu lọc theo ngay_tao. Không cộng tiền bằng float, dùng Decimal/NUMERIC và hiển thị VND.

Lọc thời gian nhập ngày theo Asia/Ho_Chi_Minh, quy đổi thành khoảng UTC [đầu ngày bắt đầu, đầu ngày sau ngày kết thúc). Lưu thời điểm timezone-aware; không dùng timezone host để tính hạn hoặc báo cáo. Không tạo bảng thống kê riêng.

## UI và API

Layout Ant Design responsive: sidebar theo vai trò, header hồ sơ/đăng xuất; page title, tìm kiếm/bộ lọc, bảng phân trang, nút tạo, form/modal chi tiết. Luồng mượn dùng form chọn độc giả + danh sách cuốn; trả dùng danh sách cuốn của phiếu và xác nhận từng cuốn. Không hiển thị dashboard quản trị cho độc giả; trang đầu độc giả là tra cứu sách.

Routes dự kiến: /login, /forgot-password, /change-password, /profile; /dashboard; /books và /books/:id; /categories, /authors, /publishers; /readers, /borrowings, /reservations, /fines; /users, /password-reset-requests; /my-borrowings, /my-reservations, /my-fines.

API /api/v1 chia theo các nhóm tương ứng. Router nhận schema/kiểm tra auth, service quản lý nghiệp vụ và transaction, repository truy vấn. List dùng page/page_size có giới hạn, trả items/total/page/page_size. 401 token sai/hết hạn; 403 sai vai trò; 404 bản ghi không tồn tại hoặc không thuộc phạm vi cá nhân; 409 trạng thái xung đột; 422 dữ liệu không hợp lệ. Lỗi không xuất SQL, DSN, mật khẩu hoặc token. Không cho mass assignment trường nhạy cảm.

Frontend dùng Axios chung, TanStack Query cho server state và invalidate sau mutation, Zustand chỉ giữ phiên đăng nhập. Hiển thị loading/error/empty; dialog xác nhận thao tác quan trọng; không toast thành công trước khi API hoàn tất. Tất cả nút có nhãn rõ, form liên kết label và lỗi, hỗ trợ bàn phím.

## Database và migration

Ánh xạ đầy đủ 12 bảng hiện có trước khi bật autogenerate. Giữ dữ liệu mẫu và baseline SQL nguyên vẹn. Migration cộng thêm auth_version, must_change_password và bảng password_reset_request có FK người yêu cầu, trạng thái, thời điểm yêu cầu/xử lý, Admin xử lý; chưa cần bảng refresh token. Không drop/rename bảng/cột hiện có. Không sửa hash seed tự động.

“Giữ 12 bảng hiện có” nghĩa là bảo toàn chúng và dữ liệu, không giới hạn tổng số bảng ở 12. Đề xuất bổ sung một bảng nghiệp vụ kỹ thuật password_reset_request, tổng cộng 13 bảng chức năng ngoài alembic_version. Việc bổ sung này nằm trong phạm vi thiết kế chờ duyệt.

Giữ index unique email không phân biệt hoa thường, unique mượn chưa trả, unique đặt trước đang hoạt động. Mọi transaction mượn/trả/thanh toán/hoàn tất đặt trước có rollback khi lỗi. Có migration riêng được review trước khi áp dụng lên database thật; kiểm thử trên database test biệt lập, không truncate database người dùng.

## Thứ tự và tiêu chí nghiệm thu

1. ORM + auth + hồ sơ + UC01/UC02: đăng nhập đúng quyền, khóa/reset/đổi quyền vô hiệu token, tài khoản seed không đăng nhập được, yêu cầu khôi phục chỉ Admin xử lý.
2. UC03–UC06: CRUD và tìm kiếm thực tế, bản sao/đầu sách đúng mô hình, thẻ hợp lệ, chặn xóa có tham chiếu.
3. UC07/UC08/UC11: mượn nhiều cuốn atomic, hai request đồng thời không mượn cùng cuốn; trả/mất/hỏng đúng trạng thái; dữ liệu cá nhân cách ly.
4. UC09/UC10/UC12: FIFO/expiry/hoàn tất đặt trước, thanh toán một lần, thống kê đúng dữ liệu và múi giờ.
5. Kiểm tra toàn luồng qua UI, responsive, backend pytest, TypeScript, frontend production build, API contract và migration trên DB test.

Mỗi UC phải có API thật, giao diện sử dụng được và test success/failure/permission phù hợp. Không coi module xong nếu chỉ có thư mục, mock data hoặc nút chưa có hành vi. Browser runtime sẽ được kiểm tra bằng công cụ có sẵn; nếu chưa có browser tool sẽ báo NOT RUN, không tuyên bố giao diện đã được kiểm chứng.

## Việc giao cho implementer

Tự chọn tên file và chia module cụ thể theo kiến trúc đã có; chi tiết token TTL (đề xuất 30 phút), page_size tối đa (100), giới hạn rate limit hợp lý, wording UI, chỉ số biểu đồ và cách bố trí form. Ghi rõ cấu hình trong .env.example và README. Không tự cài dịch vụ gửi mail hoặc đổi chính sách nghiệp vụ nêu trên.
