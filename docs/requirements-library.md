# Nội dung yêu cầu từ tài liệu người dùng



Nguồn: Chuc_nang_du_an_Quan_ly_thu_vien.docx



Phần dưới là nội dung đặc tả chức năng được trích từ tài liệu, dùng làm yêu cầu sản phẩm.



ĐẶC TẢ DANH SÁCH CHỨC NĂNG

DỰ ÁN QUẢN LÝ THƯ VIỆN (LIBRARY MANAGEMENT SYSTEM)

Phiên bản 1.0  |  Cơ sở dữ liệu: PostgreSQL  |  Phạm vi: 12 nhóm Use Case

1. Tổng quan

Hệ thống hỗ trợ quản trị tài khoản, quản lý đầu sách và bản sao vật lý, độc giả và thẻ thư viện, nghiệp vụ mượn/trả, đặt trước, tiền phạt và thống kê. Ba vai trò: Admin (quản trị viên), Thủ thư và Độc giả.

Quy ước phân quyền: ✓ = được phép; — = không được phép; CN = chỉ dữ liệu cá nhân. Các thao tác phải được kiểm tra quyền ở backend, không chỉ ẩn nút trên giao diện.

2. Danh mục Use Case

Mã

Nhóm Use Case

Tác nhân

UC01

Quản lý tài khoản

Admin

UC02

Xác thực và hồ sơ cá nhân

Admin, Thủ thư, Độc giả

UC03

Quản lý độc giả và thẻ thư viện

Admin, Thủ thư

UC04

Quản lý sách

Admin, Thủ thư

UC05

Quản lý danh mục sách

Admin, Thủ thư

UC06

Tra cứu sách

Admin, Thủ thư, Độc giả

UC07

Quản lý mượn sách

Admin, Thủ thư

UC08

Quản lý trả sách

Admin, Thủ thư

UC09

Quản lý đặt trước sách

Độc giả; Admin, Thủ thư xử lý

UC10

Quản lý tiền phạt

Admin, Thủ thư; Độc giả xem cá nhân

UC11

Theo dõi mượn trả cá nhân

Độc giả

UC12

Thống kê và báo cáo

Admin, Thủ thư

3. Đặc tả chức năng chi tiết

UC01 – Quản lý tài khoản

Tác nhân: Admin

Các chức năng:

Xem danh sách, tìm kiếm và xem chi tiết tài khoản.

Tạo tài khoản Thủ thư/Độc giả; cập nhật thông tin.

Phân quyền, khóa/mở khóa và đặt lại mật khẩu.

Bảng dữ liệu: nguoi_dung

Quy tắc nghiệp vụ: Tài khoản email duy nhất; mật khẩu lưu dưới dạng hash; chỉ Admin được phân quyền.

UC02 – Xác thực và hồ sơ cá nhân

Tác nhân: Admin, Thủ thư, Độc giả

Các chức năng:

Đăng nhập và đăng xuất.

Đổi mật khẩu, yêu cầu khôi phục mật khẩu.

Xem và cập nhật thông tin hồ sơ của chính mình.

Bảng dữ liệu: nguoi_dung

Quy tắc nghiệp vụ: Người dùng chỉ sửa hồ sơ bản thân; không tự sửa vai trò hay trạng thái tài khoản.

UC03 – Quản lý độc giả và thẻ thư viện

Tác nhân: Admin, Thủ thư

Các chức năng:

Xem danh sách, tìm kiếm và xem chi tiết độc giả.

Cấp thẻ thư viện; gia hạn thời gian sử dụng.

Khóa/mở khóa thẻ; xem lịch sử mượn trả của độc giả.

Bảng dữ liệu: nguoi_dung, the_thu_vien, phieu_muon, chi_tiet_muon

Quy tắc nghiệp vụ: Mỗi độc giả tối đa một thẻ theo mô hình hiện tại; ngày hết hạn không trước ngày cấp.

UC04 – Quản lý sách

Tác nhân: Admin, Thủ thư

Các chức năng:

Xem, tìm kiếm, lọc và xem chi tiết đầu sách.

Thêm, cập nhật và xóa đầu sách khi không vi phạm ràng buộc.

Thêm bản sao; cập nhật mã vạch, vị trí kệ và tình trạng cuốn sách.

Bảng dữ liệu: sach, cuon_sach, the_loai, nha_xuat_ban, sach_tac_gia, tac_gia

Quy tắc nghiệp vụ: ISBN xác định ấn phẩm; mã vạch xác định từng bản sao; không xóa cuốn đang được mượn.

UC05 – Quản lý danh mục sách

Tác nhân: Admin, Thủ thư

Các chức năng:

Xem, thêm, sửa, xóa thể loại.

Xem, thêm, sửa, xóa tác giả.

Xem, thêm, sửa, xóa nhà xuất bản; liên kết tác giả với sách.

Bảng dữ liệu: the_loai, tac_gia, nha_xuat_ban, sach_tac_gia, sach

Quy tắc nghiệp vụ: Không xóa danh mục đang được tham chiếu nếu chưa xử lý quan hệ liên quan.

UC06 – Tra cứu sách

Tác nhân: Admin, Thủ thư, Độc giả

Các chức năng:

Xem danh sách và chi tiết sách.

Tìm theo tên sách hoặc ISBN; lọc theo thể loại, tác giả, nhà xuất bản.

Xem số bản sao có thể mượn và tình trạng sẵn có.

Bảng dữ liệu: sach, cuon_sach, the_loai, tac_gia, sach_tac_gia, nha_xuat_ban

Quy tắc nghiệp vụ: Số lượng có thể mượn được tính từ các cuốn có trạng thái AVAILABLE.

UC07 – Quản lý mượn sách

Tác nhân: Admin, Thủ thư

Các chức năng:

Xem danh sách và chi tiết phiếu mượn.

Chọn độc giả, thêm một hoặc nhiều cuốn vào phiếu mượn, đặt hạn trả.

Kiểm tra thẻ và trạng thái cuốn; xác nhận mượn, cập nhật trạng thái BORROWED.

Bảng dữ liệu: phieu_muon, chi_tiet_muon, nguoi_dung, the_thu_vien, cuon_sach

Quy tắc nghiệp vụ: Một cuốn không được có hai lượt mượn chưa kết thúc; thao tác lập phiếu và đổi trạng thái cần chạy trong một transaction.

UC08 – Quản lý trả sách

Tác nhân: Admin, Thủ thư

Các chức năng:

Tìm phiếu mượn và các cuốn chưa trả.

Ghi ngày trả, tình trạng khi trả; xác nhận trả từng cuốn.

Phát hiện quá hạn hoặc hỏng/mất, lập khoản phạt; cập nhật trạng thái cuốn.

Bảng dữ liệu: phieu_muon, chi_tiet_muon, cuon_sach, tien_phat

Quy tắc nghiệp vụ: Không trả lại hai lần; cuốn hỏng/mất không tự chuyển về AVAILABLE.

UC09 – Quản lý đặt trước sách

Tác nhân: Độc giả; Admin, Thủ thư xử lý

Các chức năng:

Độc giả tạo, xem và hủy yêu cầu đặt trước của mình.

Thủ thư xem yêu cầu; xác nhận sách sẵn sàng; cập nhật trạng thái.

Hoàn tất khi độc giả nhận sách hoặc hủy yêu cầu không hợp lệ.

Bảng dữ liệu: dat_truoc_sach, sach, nguoi_dung, cuon_sach

Quy tắc nghiệp vụ: Đặt trước theo đầu sách; cần xác định chính sách xếp hàng và thời hạn nhận.

UC10 – Quản lý tiền phạt

Tác nhân: Admin, Thủ thư; Độc giả xem cá nhân

Các chức năng:

Thủ thư xem, lập khoản phạt do quá hạn, mất hoặc hỏng.

Ghi số tiền, lý do; xác nhận thanh toán và xem lịch sử.

Độc giả xem các khoản phạt và trạng thái thanh toán của mình.

Bảng dữ liệu: tien_phat, chi_tiet_muon, phieu_muon, nguoi_dung

Quy tắc nghiệp vụ: Số tiền không âm; việc tính mức phạt theo chính sách thư viện; mô hình hiện tại chưa hỗ trợ trả góp.

UC11 – Theo dõi mượn trả cá nhân

Tác nhân: Độc giả

Các chức năng:

Xem các cuốn đang mượn, ngày mượn và hạn trả.

Xem danh sách quá hạn và chi tiết từng lượt mượn.

Xem lịch sử các cuốn đã trả.

Bảng dữ liệu: nguoi_dung, phieu_muon, chi_tiet_muon, cuon_sach, sach

Quy tắc nghiệp vụ: Chỉ xem dữ liệu mượn trả của tài khoản đang đăng nhập.

UC12 – Thống kê và báo cáo

Tác nhân: Admin, Thủ thư

Các chức năng:

Thống kê đầu sách, bản sao, độc giả, sách đang mượn và quá hạn.

Thống kê lượt mượn theo tháng/năm và sách được mượn nhiều.

Thống kê tiền phạt đã thu/chưa thu; lọc theo thời gian.

Bảng dữ liệu: sach, cuon_sach, nguoi_dung, phieu_muon, chi_tiet_muon, tien_phat

Quy tắc nghiệp vụ: Số liệu tổng hợp từ bảng nghiệp vụ, không yêu cầu bảng thống kê riêng.

4. Ma trận phân quyền

Use Case

Admin

Thủ thư

Độc giả

UC01

✓

—

—

UC02

✓

✓

✓

UC03

✓

✓

—

UC04

✓

✓

—

UC05

✓

✓

—

UC06

✓

✓

✓

UC07

✓

✓

—

UC08

✓

✓

—

UC09

Xử lý

Xử lý

Tạo/xem/hủy CN

UC10

Quản lý

Quản lý

Xem CN

UC11

—

—

✓

UC12

✓

✓

—

Ghi chú: UC11 dành cho độc giả; Admin/Thủ thư có thể tra cứu lịch sử độc giả qua UC03/UC07 theo phạm vi nghiệp vụ. UC09 không cho Admin đặt sách thay độc giả theo phạm vi đã thống nhất.

5. Danh sách bảng PostgreSQL

Bảng

Vai trò

nguoi_dung

Tài khoản, vai trò

the_thu_vien

Thẻ độc giả

the_loai

Danh mục thể loại

tac_gia

Thông tin tác giả

nha_xuat_ban

Nhà xuất bản

sach

Đầu sách

sach_tac_gia

Quan hệ nhiều-nhiều sách/tác giả

cuon_sach

Bản sao vật lý

phieu_muon

Thông tin phiếu mượn

chi_tiet_muon

Các cuốn được mượn và trả

dat_truoc_sach

Yêu cầu đặt trước

tien_phat

Khoản phạt

6. Phạm vi triển khai đề xuất

Ưu tiên triển khai: UC01–UC08 và UC11. Giai đoạn mở rộng: UC09, UC10 và UC12. Nếu triển khai thông báo, thanh toán nhiều lần hoặc gia hạn mượn, cần bổ sung bảng và nghiệp vụ tương ứng.
