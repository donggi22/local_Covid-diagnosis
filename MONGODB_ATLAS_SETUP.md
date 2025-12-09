# 🔗 MongoDB Atlas 연결 정보

## 📋 팀원 공유용 안내

MongoDB Atlas가 설정되었습니다! 이제 팀원 모두가 같은 데이터베이스를 사용할 수 있습니다.

---

## ⚙️ 설정 방법

### 1. Express 백엔드 설정

```bash
cd Final_Back/express
cp .env.example .env
```

`.env` 파일을 열어서 다음 내용으로 수정:

```env
MONGODB_URI=mongodb+srv://wngud4232_db_user:4B6fnbhObvIC37ZG@cluster0.mmjhan4.mongodb.net/medical-ai?retryWrites=true&w=majority
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
PORT=5001
```

### 2. FastAPI 백엔드 설정

```bash
cd Final_Back/fastapi
cp .env.example .env
```

`.env` 파일을 열어서 다음 내용으로 수정:

```env
MONGODB_URI=mongodb+srv://wngud4232_db_user:4B6fnbhObvIC37ZG@cluster0.mmjhan4.mongodb.net/medical-ai?retryWrites=true&w=majority
MONGODB_DB=medical-ai
```

---

## ✅ 확인 사항

1. `.env` 파일이 제대로 생성되었는지 확인
2. 서버 실행 시 "✅ MongoDB 연결 성공" 메시지가 나오는지 확인
3. 브라우저에서 http://localhost:3000 접속하여 로그인 테스트

---

## 📝 참고사항

- **로컬 MongoDB에 데이터가 있는 경우:**
  ```bash
  cd Final_Back/express
  npm run migrate
  ```
  이 명령어로 로컬 데이터를 Atlas로 옮길 수 있습니다.

- **초기 테스트 계정 생성:**
  ```bash
  cd Final_Back/express
  npm run seed
  ```

---

## 🆘 문제 해결

**연결이 안 될 때:**
1. `.env` 파일이 올바른 위치에 있는지 확인
2. 연결 문자열에 공백이나 줄바꿈이 없는지 확인
3. MongoDB Atlas에서 IP 화이트리스트 설정 확인 (0.0.0.0/0으로 모든 IP 허용)

**질문이 있으면 팀장에게 문의하세요!**





