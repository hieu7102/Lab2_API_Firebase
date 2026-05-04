# Note App - API & Firebase

## 1. Giới thiệu

Đây là ứng dụng **Note App** đơn giản được xây dựng theo kiến trúc full-stack nhằm minh họa luồng hoạt động giữa:

* **Frontend**: Streamlit
* **Backend**: FastAPI
* **Authentication**: Firebase Authentication
* **Database**: Firebase Firestore

Ứng dụng cho phép người dùng đăng ký / đăng nhập bằng Firebase Authentication, sau đó thực hiện các thao tác quản lý ghi chú cá nhân như:

* Tạo ghi chú
* Xem danh sách ghi chú
* Cập nhật ghi chú
* Xóa ghi chú

Mỗi ghi chú được gắn với tài khoản người dùng hiện tại thông qua `user_id`, giúp dữ liệu của từng người dùng được tách biệt hoàn toàn.

---

## 2. Công nghệ sử dụng

## Frontend

* Streamlit
* Requests
* Python-dotenv

## Backend

* FastAPI
* Uvicorn
* Firebase Admin SDK
* Pydantic

## Authentication

* Firebase Authentication
* Email / Password Login

## Database

* Firebase Firestore

---

## 3. Chức năng chính

## 3.1 Authentication

Ứng dụng hỗ trợ:

* Đăng ký tài khoản bằng email/password
* Đăng nhập bằng Firebase Authentication
* Đăng xuất
* Lấy thông tin người dùng hiện tại từ Firebase ID Token

Frontend sử dụng Firebase Web API để đăng nhập và nhận về `idToken`.

Backend sử dụng Firebase Admin SDK để xác thực token trước khi xử lý dữ liệu.

---

## 3.2 Note Management

Sau khi đăng nhập, người dùng có thể:

* Tạo note mới
* Xem danh sách note của chính mình
* Cập nhật nội dung note
* Xóa note

Tất cả dữ liệu note được lưu trên Firebase Firestore và được gắn với `user_id` của người dùng đang đăng nhập.

---

## 4. Luồng hoạt động hệ thống

```text
Người dùng đăng nhập trên frontend
        ↓
Firebase Authentication trả về ID Token
        ↓
Frontend gửi request kèm Authorization Bearer Token đến backend
        ↓
Backend xác thực token bằng Firebase Admin SDK
        ↓
Backend xử lý CRUD note
        ↓
Dữ liệu được lưu / đọc từ Firestore
        ↓
Backend trả kết quả về frontend
        ↓
Frontend hiển thị kết quả cho người dùng
```

---

## 5. Cấu trúc thư mục

```text
Lab2_API-Firebase/
│
├── backend/
│   ├── main.py
│   └── serviceAccountKey.json
│
├── frontend/
│   ├── app.py
│   └── .env
│
├── requirements.txt
├── .gitignore
└── README.md
```

### Giải thích

* `backend/main.py`: API FastAPI xử lý xác thực và CRUD notes
* `serviceAccountKey.json`: Firebase Admin SDK private key (không được push GitHub)
* `frontend/app.py`: giao diện người dùng bằng Streamlit
* `frontend/.env`: lưu biến môi trường cho Firebase Web API Key và backend URL

---

## 6. API Endpoints

## 6.1 System

| Method | Endpoint  | Mô tả                           |
| ------ | --------- | ------------------------------- |
| GET    | `/`       | Kiểm tra backend đang hoạt động |
| GET    | `/health` | Kiểm tra trạng thái hệ thống    |

Ví dụ response:

```json
{
  "status": "ok",
  "message": "Backend running"
}
```

---

## 6.2 Authentication

| Method | Endpoint   | Mô tả                                            |
| ------ | ---------- | ------------------------------------------------ |
| GET    | `/auth/me` | Lấy thông tin user hiện tại từ Firebase ID Token |

Header bắt buộc:

```text
Authorization: Bearer <Firebase_ID_Token>
```

Ví dụ response:

```json
{
  "user_id": "firebase_uid",
  "email": "example@gmail.com"
}
```

---

## 6.3 Notes

| Method | Endpoint           | Mô tả                 |
| ------ | ------------------ | --------------------- |
| POST   | `/notes`           | Tạo ghi chú mới       |
| GET    | `/notes`           | Lấy danh sách ghi chú |
| PUT    | `/notes/{note_id}` | Cập nhật ghi chú      |
| DELETE | `/notes/{note_id}` | Xóa ghi chú           |

Tất cả endpoint liên quan đến note đều yêu cầu:

```text
Authorization: Bearer <Firebase_ID_Token>
```

---

## 7. Request / Response Models

## 7.1 Create Note

### Request

```json
{
  "content": "Hôm nay học FastAPI"
}
```

### Response

```json
{
  "id": "note_document_id",
  "user_id": "firebase_uid",
  "content": "Hôm nay học FastAPI",
  "created_at": "2026-05-04T10:30:00"
}
```

---

## 7.2 Update Note

### Request

```json
{
  "content": "Nội dung đã chỉnh sửa"
}
```

### Response

```json
{
  "status": "success",
  "message": "Note updated"
}
```

---

## 7.3 Delete Note

### Response

```json
{
  "status": "success",
  "message": "Note deleted"
}
```

---

## 8. Cấu trúc dữ liệu Firestore

Collection:

```text
notes
```

Mỗi document có cấu trúc:

```json
{
  "id": "note_document_id",
  "user_id": "firebase_user_uid",
  "content": "Nội dung ghi chú",
  "created_at": "2026-05-04T10:00:00",
  "updated_at": "2026-05-04T10:10:00"
}
```

> `updated_at` chỉ xuất hiện sau khi người dùng thực hiện chỉnh sửa note.

---

## 9. Hướng dẫn cài đặt

## 9.1 Clone repository

```bash
git clone https://github.com/your-repository/Lab2_API-Firebase.git
cd Lab2_API-Firebase
```

---

## 9.2 Tạo môi trường ảo

```bash
python -m venv venv
```

---

## 9.3 Kích hoạt môi trường ảo

### Windows

```bash
venv\Scripts\activate
```

### Mac/Linux

```bash
source venv/bin/activate
```

---

## 9.4 Cài đặt thư viện

```bash
pip install -r requirements.txt
```

---

## 10. Cấu hình Firebase

## 10.1 Bật Firebase Authentication

1. Truy cập Firebase Console
2. Chọn project Firebase
3. Vào **Authentication**
4. Chọn **Sign-in method**
5. Bật phương thức **Email/Password**

---

## 10.2 Tạo Firestore Database

1. Vào **Firestore Database**
2. Chọn **Create database**
3. Chọn chế độ phù hợp để test
4. Tạo database để lưu dữ liệu note

---

## 10.3 Tạo Firebase Admin SDK Key

1. Vào **Project Settings**
2. Chọn tab **Service Accounts**
3. Chọn **Generate new private key**
4. Tải file JSON về
5. Đổi tên thành:

```text
serviceAccountKey.json
```

6. Đặt file vào thư mục:

```text
backend/serviceAccountKey.json
```

> File này chứa private key nên tuyệt đối không được upload lên GitHub.

---

## 10.4 Lấy Firebase Web API Key

1. Vào **Project Settings**
2. Tab **General**
3. Tìm phần **Web API Key**

Dùng key này cho frontend Streamlit.

---

## 11. Cấu hình Frontend (.env)

Tạo file:

```text
frontend/.env
```

Nội dung:

```env
FIREBASE_WEB_API_KEY=your_firebase_web_api_key
FASTAPI_BACKEND_URL=http://127.0.0.1:8000
```

Trong đó:

* `FIREBASE_WEB_API_KEY`: lấy từ Firebase Project Settings
* `FASTAPI_BACKEND_URL`: địa chỉ backend FastAPI đang chạy

Frontend đọc các biến này bằng:

```python
load_dotenv()
os.getenv(...)
```

---

## 12. Chạy ứng dụng

## 12.1 Chạy Backend

Từ thư mục gốc project:

```bash
cd backend
uvicorn main:app --reload
```

Backend chạy tại:

```text
http://127.0.0.1:8000
```

Kiểm tra nhanh:

```text
http://127.0.0.1:8000
```

hoặc:

```text
http://127.0.0.1:8000/health
```

Nếu thành công sẽ hiển thị:

```json
{
  "status": "ok",
  "message": "Backend running"
}
```

---

## 12.2 Chạy Frontend

Mở terminal mới:

```bash
cd frontend
streamlit run app.py
```

Frontend chạy tại:

```text
http://localhost:8501
```

---

## 13. Hướng dẫn sử dụng

1. Mở frontend tại `http://localhost:8501`
2. Chọn:

   * Login
   * hoặc Register
3. Nếu chưa có tài khoản → chọn Register để tạo tài khoản mới
4. Sau khi đăng nhập thành công, sidebar hiển thị email người dùng
5. Nhập nội dung note tại phần **Add Note**
6. Nhấn **Add** để tạo note mới
7. Danh sách note sẽ hiển thị ở phần **Your Notes**
8. Có thể:

   * Edit note
   * Delete note
9. Dữ liệu được lưu trên Firebase Firestore theo từng tài khoản riêng biệt

---

## 14. Lưu ý bảo mật

* Không push `serviceAccountKey.json` lên GitHub
* Không commit file `.env`
* Không public Firebase private key
* Chỉ user sở hữu note mới có quyền sửa / xóa note của chính mình

Backend đã kiểm tra quyền sở hữu note thông qua:

```python
if data.get("user_id") != user_id:
    raise HTTPException(status_code=403, detail="Not authorized")
```

---

## 15. Video demo

Link video demo:

```text
https://drive.google.com/drive/folders/1sXamwhaVQ6-3BcFnkhlT7HZMOmQLxaDA
```

---

## 16. Tác giả

- Họ tên: Trần Hùng Nhân
- MSSV: 24120401
- Trường: Đại học Khoa học Tự nhiên - ĐHQG-HCM
- Môn học: Tư duy tính toán
