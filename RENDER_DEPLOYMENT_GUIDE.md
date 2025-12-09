# 🚀 Render 서버 배포 가이드

시연/테스트용 Render 배포 가이드입니다.

---

## 📋 사전 준비사항

### 1. GitHub Release에 모델 파일 업로드

1. GitHub 저장소 → **Releases** → **Create a new release**
2. **Tag**: `v1.0.0` (또는 원하는 버전)
3. **Release title**: `AI Models v1.0.0`
4. **모델 파일 업로드**:
   - `seg_model.pth` (분할 모델, 355MB)
   - `clf_model.pth` (분류 모델, 281MB)
   - 또는 압축 파일: `models.zip`

**중요**: 모델 파일 이름에 `seg` 또는 `clf`가 포함되어야 자동으로 인식됩니다.

---

## 🔧 서비스별 배포 설정

### 1단계: Express 서버 배포

#### Render 설정
- **Service Type**: Web Service
- **Name**: `medi-kit-express` (또는 원하는 이름)
- **Environment**: Node
- **Branch**: `fix/fastapi-file-upload` (또는 메인 브랜치)
- **Root Directory**: `Final_Back/express`
- **Build Command**: `npm install`
- **Start Command**: `npm start`

#### 환경 변수 (Environment Variables)
```
MONGODB_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/medical-ai?retryWrites=true&w=majority
MONGODB_DB=medical-ai
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
PORT=5001
FASTAPI_URL=https://medi-kit-fastapi.onrender.com
```

**⚠️ 주의**: `FASTAPI_URL`은 FastAPI 서버 배포 후 업데이트해야 합니다.

---

### 2단계: FastAPI 서버 배포

#### Render 설정
- **Service Type**: Web Service
- **Name**: `medi-kit-fastapi` (또는 원하는 이름)
- **Environment**: Python 3
- **Branch**: `fix/fastapi-file-upload` (또는 메인 브랜치)
- **Root Directory**: `Final_Back/fastapi`
- **Build Command**: `pip install -r requirements.txt && python download_models.py`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

#### 환경 변수 (Environment Variables)
```
PORT=8000
MONGODB_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/medical-ai?retryWrites=true&w=majority
MONGODB_DB=medical-ai
GITHUB_REPO=KimJoohyung4232/final-project
MODEL_RELEASE_TAG=v1.0.0
```

**중요**: 
- `GITHUB_REPO`: 본인의 GitHub 저장소로 변경
- `MODEL_RELEASE_TAG`: GitHub Release 태그와 일치해야 함

---

### 3단계: React 프론트엔드 배포

#### Render 설정
- **Service Type**: Static Site
- **Name**: `medi-kit-frontend` (또는 원하는 이름)
- **Branch**: `fix/fastapi-file-upload` (또는 메인 브랜치)
- **Root Directory**: `Final_Front4`
- **Build Command**: `npm install && npm run build`
- **Publish Directory**: `build`

#### 환경 변수 (Environment Variables)
```
REACT_APP_API_BASE_URL=https://medi-kit-express.onrender.com
REACT_APP_FASTAPI_URL=https://medi-kit-fastapi.onrender.com
```

**⚠️ 주의**: 
- Express와 FastAPI 서버 배포 후 URL을 확인하여 설정
- 환경 변수 변경 후 **반드시 재빌드** 필요

---

## 📝 배포 순서

1. **GitHub Release에 모델 파일 업로드**
2. **Express 서버 배포** (먼저 배포)
3. **FastAPI 서버 배포** (Express 배포 후)
4. **Express 서버의 `FASTAPI_URL` 환경 변수 업데이트**
5. **React 프론트엔드 배포** (Express, FastAPI URL 확인 후)

---

## ✅ 배포 후 확인사항

### Express 서버
- URL: `https://medi-kit-express.onrender.com`
- Health Check: `https://medi-kit-express.onrender.com/`

### FastAPI 서버
- URL: `https://medi-kit-fastapi.onrender.com`
- Health Check: `https://medi-kit-fastapi.onrender.com/api/ai/health`
- 모델 로드 확인: 로그에서 "✅ AI 모델 로드 완료" 메시지 확인

### React 프론트엔드
- URL: `https://medi-kit-frontend.onrender.com`
- 브라우저에서 접속하여 기능 테스트

---

## 🔍 문제 해결

### 모델 다운로드 실패
- GitHub Release가 생성되었는지 확인
- Release 태그가 `MODEL_RELEASE_TAG`와 일치하는지 확인
- 모델 파일 이름에 `seg` 또는 `clf`가 포함되어 있는지 확인

### CORS 오류
- Express와 FastAPI에서 CORS 설정 확인
- 프론트엔드 도메인이 허용되어 있는지 확인

### 환경 변수 오류
- 모든 환경 변수가 올바르게 설정되었는지 확인
- React 프론트엔드는 환경 변수 변경 후 재빌드 필요

---

## 💡 참고사항

### Render 무료 플랜 제한
- **Sleep 모드**: 15분간 요청이 없으면 sleep
- **첫 요청 지연**: 약 30초 정도 소요
- **해결책**: 시연 전 워밍업 요청 전송

### 모델 파일 크기
- 분할 모델: 355MB
- 분류 모델: 281MB
- 총: 약 636MB
- GitHub Release 사용으로 저장소 크기 문제 해결

---

## 📞 추가 도움

문제가 발생하면:
1. Render 로그 확인
2. GitHub Release 확인
3. 환경 변수 확인
4. 서버 Health Check 확인



