# 🚀 외부 서버 배포 가이드

외부 서버에 배포할 때 필요한 환경 변수 설정 가이드입니다.

## 📋 문제 상황

외부 서버에 배포했을 때 "AI 진단 서비스를 사용할 수 없습니다. FastAPI 서버를 확인해주세요." 오류가 발생하는 경우, 환경 변수 설정이 필요합니다.

## ⚙️ 환경 변수 설정

### 1. Express 백엔드 설정

**위치**: `Final_Back/express/.env`

```env
MONGODB_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/medical-ai?retryWrites=true&w=majority
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
PORT=5001

# ⚠️ 중요: 외부 서버 배포 시 이 값을 변경해야 합니다
# 예시: http://210.125.70.71:8000 또는 http://서버IP:FastAPI포트
FASTAPI_URL=http://localhost:8000
```

**외부 서버 배포 시**:
- `FASTAPI_URL`을 외부에서 접근 가능한 FastAPI 서버 주소로 변경
- 예: `http://210.125.70.71:8000` (FastAPI 서버가 8000 포트에서 실행 중인 경우)
- 같은 서버 내부에서 실행 중이면 `http://localhost:8000` 또는 `http://127.0.0.1:8000` 사용 가능

### 2. 프론트엔드 설정

**위치**: `Final_Front4/.env`

```env
# ⚠️ 중요: 외부 서버 배포 시 이 값들을 변경해야 합니다

# Express 백엔드 API URL
# 예시: http://210.125.70.71:5001 또는 http://서버IP:Express포트
REACT_APP_API_BASE_URL=http://localhost:5001

# FastAPI 서버 URL (GradCAM 이미지 등 정적 파일 접근용)
# 예시: http://210.125.70.71:8000 또는 http://서버IP:FastAPI포트
REACT_APP_FASTAPI_URL=http://localhost:8000
```

**외부 서버 배포 시**:
- `REACT_APP_API_BASE_URL`을 외부에서 접근 가능한 Express 서버 주소로 변경
- `REACT_APP_FASTAPI_URL`을 외부에서 접근 가능한 FastAPI 서버 주소로 변경
- 예: `http://210.125.70.71:5001`, `http://210.125.70.71:8000`

### 3. FastAPI 백엔드 설정

**위치**: `Final_Back/fastapi/.env`

```env
MONGODB_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/medical-ai?retryWrites=true&w=majority
MONGODB_DB=medical-ai
```

FastAPI 서버는 별도의 환경 변수가 필요하지 않지만, CORS 설정이 필요할 수 있습니다.

## 🔧 설정 방법

### Express 백엔드

```bash
cd Final_Back/express

# .env.example 파일을 복사하여 .env 파일 생성
cp .env.example .env

# .env 파일을 열어서 FASTAPI_URL 수정
# 외부 서버: http://210.125.70.71:8000
# 또는 내부 네트워크: http://localhost:8000 (같은 서버에서 실행 시)
```

### 프론트엔드

```bash
cd Final_Front4

# .env.example 파일을 복사하여 .env 파일 생성
cp .env.example .env

# .env 파일을 열어서 REACT_APP_API_BASE_URL과 REACT_APP_FASTAPI_URL 수정
# 외부 서버: 
#   REACT_APP_API_BASE_URL=http://210.125.70.71:5001
#   REACT_APP_FASTAPI_URL=http://210.125.70.71:8000
```

**⚠️ 중요**: 프론트엔드 환경 변수 변경 후 **반드시 재빌드**해야 합니다:

```bash
cd Final_Front4
npm run build
```

## 🌐 외부 서버 배포 예시

서버 IP가 `210.125.70.71`이고 포트가 다음과 같다고 가정:

- Express 서버: `210.125.70.71:5001`
- FastAPI 서버: `210.125.70.71:8000`
- 프론트엔드: `210.125.70.71:31293`

### Express 백엔드 `.env`:
```env
FASTAPI_URL=http://210.125.70.71:8000
# 또는 같은 서버 내부에서 실행 중이면:
# FASTAPI_URL=http://localhost:8000
```

### 프론트엔드 `.env`:
```env
REACT_APP_API_BASE_URL=http://210.125.70.71:5001
REACT_APP_FASTAPI_URL=http://210.125.70.71:8000
```

## ✅ 확인 사항

1. **Express 서버가 FastAPI 서버에 연결할 수 있는지 확인**:
   ```bash
   # Express 서버에서 실행
   curl http://210.125.70.71:8000/api/ai/health
   ```

2. **프론트엔드가 Express 서버에 연결할 수 있는지 확인**:
   - 브라우저 개발자 도구 → Network 탭에서 API 요청 확인
   - CORS 오류가 발생하면 Express 서버의 CORS 설정 확인

3. **FastAPI 서버가 실행 중인지 확인**:
   ```bash
   curl http://210.125.70.71:8000
   ```

## 🐛 문제 해결

### "AI 진단 서비스를 사용할 수 없습니다" 오류 (503 또는 400)

#### 1. FastAPI 서버 연결 확인

1. **FastAPI 서버가 실행 중인지 확인**
   ```bash
   curl http://210.125.70.71:8000
   # 또는
   curl http://210.125.70.71:8000/api/ai/health
   ```

2. **Express 서버의 `.env` 파일에서 `FASTAPI_URL` 확인**
   ```env
   FASTAPI_URL=http://210.125.70.71:8000
   # 또는 같은 서버 내부: http://localhost:8000
   ```

3. **네트워크 연결 확인** (방화벽, 포트 열림 여부)

#### 2. 이미지 파일 경로 문제 (400 Bad Request)

**증상**: `details: "Request failed with status code 400"` 또는 `"이미지 파일을 찾을 수 없습니다"`

**원인**: Express 서버와 FastAPI 서버가 서로 다른 파일 시스템을 사용하거나, 경로가 올바르지 않음

**해결 방법**:

1. **같은 서버에서 실행 중인 경우**:
   - Express 서버와 FastAPI 서버가 같은 서버에서 실행 중이어야 함
   - Express 서버 로그에서 이미지 경로 확인:
     ```
     FastAPI에 진단 요청 전송: { image_path: '/path/to/uploads/...', file_exists: true }
     ```
   - FastAPI 서버 로그에서 경로 확인:
     ```
     📁 이미지 경로 확인: /path/to/uploads/...
     ```

2. **다른 서버/컨테이너에서 실행 중인 경우**:
   - 공유 디렉토리 사용 (NFS, Docker Volume 등)
   - 또는 파일을 직접 전송하는 방식으로 변경 필요

3. **Express 서버 로그 확인**:
   ```bash
   # Express 서버 로그에서 다음 메시지 확인
   # "FastAPI 호출 실패:" 또는 "요청 URL: ..."
   # "이미지 경로:" 또는 "file_exists:"
   ```

4. **FastAPI 서버 로그 확인**:
   ```bash
   # FastAPI 서버 로그에서 다음 메시지 확인
   # "📁 이미지 경로 확인:" 또는 "이미지 파일을 찾을 수 없습니다"
   ```

### 프론트엔드에서 API 연결 실패

1. **프론트엔드 `.env` 파일 확인**
2. **환경 변수 변경 후 재빌드 확인**:
   ```bash
   cd Final_Front4
   npm run build
   ```
3. **브라우저 개발자 도구 → Console에서 오류 확인**

### CORS 오류

Express 서버의 `server.js`에서 CORS 설정 확인:
```javascript
app.use(cors()); // 모든 origin 허용
// 또는 특정 origin만 허용:
// app.use(cors({ origin: 'http://210.125.70.71:31293' }));
```

## 📝 참고사항

- 환경 변수 변경 후 서버를 재시작해야 합니다
- 프론트엔드 환경 변수는 **빌드 시점**에 주입되므로, 변경 후 반드시 재빌드해야 합니다
- 같은 서버 내부에서 실행 중이면 `localhost` 사용 가능
- 외부에서 접근해야 하면 서버의 실제 IP 주소나 도메인 사용

