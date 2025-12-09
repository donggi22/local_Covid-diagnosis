# final-project

최종프로젝트

---

## 🎯 처음 시작하는 팀원을 위한 가이드

**처음 프로젝트를 받는 팀원은 여기부터 시작하세요!**

### 1️⃣ 필요한 프로그램 설치

#### Git 설치 확인
```bash
git --version
```
설치되어 있지 않다면:
- **Mac**: `brew install git` 또는 https://git-scm.com/download/mac
- **Windows**: https://git-scm.com/download/win

#### Node.js 설치 확인
```bash
node --version
npm --version
```
설치되어 있지 않다면:
- https://nodejs.org/ 에서 LTS 버전 다운로드

#### Python 설치 확인 (FastAPI용)
```bash
python3 --version
```
설치되어 있지 않다면:
- **Mac**: `brew install python3`
- **Windows**: https://www.python.org/downloads/

---

### 2️⃣ 프로젝트 받기 (Clone)

**처음 프로젝트를 받을 때:**

```bash
# 원하는 폴더로 이동 (예: Desktop)
cd ~/Desktop

# 프로젝트 클론 (다운로드)
git clone https://github.com/KimJoohyung4232/final-project.git

# 프로젝트 폴더로 이동
cd final-project
```

**이제 프로젝트가 내 컴퓨터에 다운로드되었습니다!**

---

### 3️⃣ 환경 변수 파일(.env) 설정

**⚠️ 중요: MongoDB Atlas 연결 정보가 필요합니다!**

팀장이나 팀원에게 MongoDB Atlas 연결 문자열을 받아서 설정하세요.

#### Express 백엔드 설정
```bash
cd Final_Back/express

# .env.example 파일을 복사해서 .env 파일 생성
cp .env.example .env

# .env 파일을 열어서 실제 연결 문자열로 수정
# 텍스트 에디터로 .env 파일 열기
```

`.env` 파일 내용 예시:
```env
MONGODB_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/medical-ai?retryWrites=true&w=majority
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
PORT=5001
```

#### FastAPI 백엔드 설정
```bash
cd Final_Back/fastapi

# .env.example 파일을 복사해서 .env 파일 생성
cp .env.example .env

# .env 파일을 열어서 실제 연결 문자열로 수정
```

`.env` 파일 내용 예시:
```env
MONGODB_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/medical-ai?retryWrites=true&w=majority
MONGODB_DB=medical-ai
```

---

### 4️⃣ 의존성 설치

#### Express 백엔드
```bash
cd Final_Back/express
npm install
```

#### React 프론트엔드
```bash
cd Final_Front
npm install
```

#### FastAPI 백엔드
```bash
cd Final_Back/fastapi

# 가상환경 생성 (처음 한 번만)
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate  # Mac/Linux
# 또는
venv\Scripts\activate  # Windows

# 패키지 설치
pip install -r requirements.txt
```

---

### 5️⃣ 초기 데이터 설정 (테스트 계정 생성)

```bash
cd Final_Back/express
npm run seed
```

이 명령어로 테스트 계정이 자동 생성됩니다:
- 이메일: `doctor@test.com` / 비밀번호: `test1234`

---

### 6️⃣ 서버 실행

**터미널 4개를 열어서 각각 실행:**

**터미널 1 - Express 백엔드:**
```bash
cd Final_Back/express
npm run dev
```

**터미널 2 - FastAPI 백엔드:**
```bash
cd Final_Back/fastapi
source venv/bin/activate  # Mac/Linux
uvicorn app.main:app --reload --port 8000
```

**터미널 3 - React 프론트엔드:**
```bash
cd Final_Front
npm start
```

**터미널 4 - (선택사항) 로컬 MongoDB 사용 시:**
```bash
mongod
```

---

### 7️⃣ 브라우저에서 확인

- 프론트엔드: http://localhost:3000
- Express 백엔드: http://localhost:5001
- FastAPI 백엔드: http://localhost:8000

---

## 📥 팀원의 변경사항 받기 (Git Pull)

팀원이 GitHub에 푸시한 최신 변경사항을 받는 방법입니다.

### 기본 명령어

```bash
git pull origin main
```

### 단계별 가이드

#### 1️⃣ 현재 상태 확인
```bash
git status
```

#### 2️⃣ 최신 변경사항 가져오기
```bash
git pull origin main
```

#### 3️⃣ 변경사항 확인 (선택사항)
```bash
git log --oneline -5
```

---

## ⚠️ 주의사항

### 로컬에 수정한 파일이 있는 경우

**방법 1: 변경사항 커밋 후 Pull**
```bash
git add .
git commit -m "작업 내용"
git pull origin main
```

**방법 2: 변경사항 임시 저장 후 Pull**
```bash
git stash          # 변경사항 임시 저장
git pull origin main
git stash pop      # 저장한 변경사항 다시 적용
```

### 충돌(Conflict) 발생 시

1. Git이 충돌 파일을 표시합니다
2. 파일을 열어서 충돌 부분을 수정합니다
   - `<<<<<<<`, `=======`, `>>>>>>>` 표시가 있는 부분
3. 충돌 해결 후:
```bash
git add [충돌 파일명]
git commit -m "충돌 해결"
```

---

## 🚀 프로젝트 실행 방법

### 0. MongoDB Atlas 설정 (클라우드 데이터베이스)

**⚠️ 중요: 팀원들이 모두 같은 데이터베이스를 공유하려면 MongoDB Atlas를 사용하세요!**

#### MongoDB Atlas 계정 생성 및 클러스터 생성

1. **MongoDB Atlas 가입**
   - https://www.mongodb.com/cloud/atlas 접속
   - "Try Free" 클릭하여 무료 계정 생성

2. **클러스터 생성**
   - "Build a Database" 클릭
   - "FREE" (M0) 플랜 선택
   - 클라우드 제공자와 지역 선택 (가장 가까운 지역 권장)
   - 클러스터 이름 설정 (예: `Cluster0`)
   - "Create" 클릭

3. **데이터베이스 사용자 생성**
   - 좌측 메뉴에서 "Database Access" 클릭
   - "Add New Database User" 클릭
   - Authentication Method: "Password" 선택
   - Username과 Password 입력 (기억해두세요!)
   - Database User Privileges: "Atlas admin" 선택
   - "Add User" 클릭

4. **네트워크 접근 설정 (IP 화이트리스트)**
   - 좌측 메뉴에서 "Network Access" 클릭
   - "Add IP Address" 클릭
   - **팀원 모두 접근 가능하도록:**
     - "Allow Access from Anywhere" 선택 (0.0.0.0/0)
     - 또는 각자의 IP 주소 추가
   - "Confirm" 클릭

5. **연결 문자열(Connection String) 얻기**
   - 좌측 메뉴에서 "Database" 클릭
   - "Connect" 버튼 클릭
   - "Connect your application" 선택
   - Driver: "Node.js", Version: "5.5 or later" 선택
   - 연결 문자열 복사
   - 예시: `mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority`
   - `<username>`과 `<password>`를 실제 값으로 변경
   - 데이터베이스 이름 추가: `...mongodb.net/medical-ai?retryWrites=true&w=majority`

6. **환경 변수 파일(.env) 생성**

   **Express 백엔드:**
   ```bash
   cd Final_Back/express
   # .env 파일 생성
   touch .env
   ```

   `.env` 파일에 다음 내용 추가:
   ```env
   MONGODB_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/medical-ai?retryWrites=true&w=majority
   JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
   PORT=5001
   ```

   **FastAPI 백엔드:**
   ```bash
   cd Final_Back/fastapi
   # .env 파일 생성
   touch .env
   ```

   `.env` 파일에 다음 내용 추가:
   ```env
   MONGODB_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/medical-ai?retryWrites=true&w=majority
   MONGODB_DB=medical-ai
   ```

   **⚠️ 주의:**
   - `.env` 파일은 절대 GitHub에 올리지 마세요! (이미 .gitignore에 포함됨)
   - 실제 username과 password로 변경하세요
   - 팀원들은 모두 같은 연결 문자열을 사용합니다

#### 로컬 MongoDB 사용 (선택사항)

MongoDB Atlas 대신 로컬 MongoDB를 사용하려면:
```bash
mongod
# 또는
brew services start mongodb-community
```

그리고 `.env` 파일에:
```env
MONGODB_URI=mongodb://localhost:27017/medical-ai
```

---

### 1. MongoDB 실행 (로컬 사용 시만)
```bash
mongod
# 또는
brew services start mongodb-community
```

**MongoDB Atlas를 사용하는 경우 이 단계는 건너뛰세요!**

### 2. Express 백엔드 실행
```bash
cd Final_Back/express
npm install  # 처음 실행 시에만
npm run dev  # 개발 모드
```

### 3. FastAPI 백엔드 실행 (AI 서비스)
```bash
cd Final_Back/fastapi
source venv/bin/activate  # 가상환경 활성화
uvicorn app.main:app --reload --port 8000
```

### 4. React 프론트엔드 실행
```bash
cd Final_Front
npm install  # 처음 실행 시에만
npm start
```

### 5. 초기 데이터 설정 (테스트 계정 생성)

**⚠️ 중요: 처음 프로젝트를 실행하거나 데이터베이스가 비어있을 때 필수!**

```bash
cd Final_Back/express
npm run seed
```

이 명령어를 실행하면 다음 테스트 계정들이 자동으로 생성됩니다:

| 이메일 | 비밀번호 | 역할 | 설명 |
|--------|----------|------|------|
| `doctor@test.com` | `test1234` | 의사 | 일반 의사 계정 |
| `admin@test.com` | `admin1234` | 관리자 | 관리자 계정 |
| `kim@test.com` | `test1234` | 의사 | 테스트 의사 계정 |

**로그인 방법:**
1. 프론트엔드 실행 후 `http://localhost:3000` 접속
2. 위의 테스트 계정 중 하나로 로그인
3. 또는 회원가입 기능을 사용하여 새 계정 생성

---

## 📤 변경사항 업로드하기 (Git Push)

### 1. 변경사항 추가
```bash
git add .
# 또는 특정 파일만
git add 파일명
```

### 2. 커밋
```bash
git commit -m "작업 내용 설명"
```

### 3. GitHub에 푸시
```bash
git push origin main
```

### 원격 저장소에 새로운 변경사항이 있는 경우
```bash
git pull origin main  # 먼저 가져오기
git push origin main  # 그 다음 푸시
```

---

## 🔗 저장소 정보

- GitHub: https://github.com/KimJoohyung4232/final-project.git
- 브랜치: `main`
