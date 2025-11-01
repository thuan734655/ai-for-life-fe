# JobMatcherAPI

## Chạy dự án
1. Tạo và kích hoạt venv (tùy chọn)
2. Cài đặt: `pip install -r requirements.txt`
3. Chạy server: `uvicorn app.main:app --reload`

## API
- POST /jobs
- GET  /jobs
- POST /users
- POST /match
- GET  /health

## Ví dụ body match
```json
{
  "desired_position": "se",
  "skills": ["react", "javascript"],
  "years_experience": 3,
  "summary": "..."
}
```
