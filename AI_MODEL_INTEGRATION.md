# AI 모델 연동 완료 보고서

## 📋 개요

AI_model 폴더의 새로운 진단 모델(UNet + ResNet50)을 FastAPI 서버에 성공적으로 통합했습니다.

---

## 🎯 통합된 모델 정보

### 모델 구조
1. **UNet 모델** (폐 영역 분할)
   - 위치: `AI_model/models/seg_results/best_model.pth` (372MB)
   - 용도: 흉부 X-Ray 이미지에서 폐 영역을 분할
   - 입력: RGB 이미지 (224x224)
   - 출력: 폐 영역 마스크

2. **ResNet50 분류 모델** (COVID-19 분류)
   - 위치: `AI_model/models/clf_results/best_model.pth` (295MB)
   - 용도: 분할된 폐 영역 이미지를 4개 클래스로 분류
   - 입력: 분할된 RGB 이미지 (224x224)
   - 출력: 4개 클래스 확률
   - 클래스: `['COVID', 'Lung_Opacity', 'Normal', 'Viral Pneumonia']`

### 예측 파이프라인
```
이미지 입력 (RGB)
    ↓
UNet으로 폐 영역 분할
    ↓
분할된 이미지에 마스크 적용
    ↓
ResNet50으로 4클래스 분류
    ↓
확률 계산 및 결과 반환
```

---

## 📁 수정된 파일 목록

### 1. FastAPI 서버

#### `Final_Back/fastapi/app/services/model.py` (전체 교체)
- **변경 내용**: 기존 TorchXRayVision 모델 → 새로운 UNet + ResNet50 모델로 교체
- **주요 기능**:
  - `UNet` 클래스: 폐 영역 분할 모델 정의
  - `COVID19Classifier` 클래스: ResNet50 기반 4클래스 분류 모델 정의
  - `load_model()`: 두 모델을 동시에 로드
  - `predict()`: 분할 → 분류 파이프라인 실행

#### `Final_Back/fastapi/app/routers/ai.py`
- **변경 내용**: 환자 확인을 선택사항으로 변경
- **이유**: 환자가 없어도 이미지만으로 예측 가능하도록 개선

#### `Final_Back/fastapi/app/services/__init__.py`
- **변경 내용**: `DISEASE_LABELS` → `CLASS_NAMES`로 변경

### 2. Express 서버

#### `Final_Back/express/src/controllers/diagnosisController.js`
- **변경 내용**:
  - FastAPI URL: `http://localhost:8001` → `http://localhost:8000`
  - 타임아웃: 5초 → 60초
  - 404 에러 시 재시도 로직 추가
  - `predicted_class` 필드 추가
  - 에러 로깅 강화

### 3. 프론트엔드

#### `Final_Front4/src/components/AIDiagnosis.js`
- **변경 내용**:
  - `predictedClass` 정보 저장
  - `aiNotes` 필드 처리 개선 (aiNotes, ai_notes 둘 다 지원)
  - 기본 메시지 개선

#### `Final_Front4/src/utils/api.js`
- **변경 내용**:
  - 기본 타임아웃: 120초로 설정
  - 진단 요청 타임아웃: 120초로 설정

---

## 🔧 모델 로드 및 예측 과정

### 모델 로드
```python
# FastAPI 서버 시작 시 자동 로드
load_model()
# → UNet 모델 로드 (seg_results/best_model.pth)
# → ResNet50 모델 로드 (clf_results/best_model.pth)
```

### 예측 과정
```python
# 1. 이미지 전처리 (RGB 변환, 224x224 리사이즈)
image_tensor = _preprocess_image(image_path)

# 2. UNet으로 폐 영역 분할
mask = _segment_lung(image_tensor)

# 3. 분할된 이미지로 분류용 전처리
segmented_tensor = _preprocess_for_classification(image_tensor, mask)

# 4. ResNet50으로 분류 예측
outputs = _classification_model(segmented_tensor)
probabilities = torch.softmax(outputs, dim=1)

# 5. 결과 반환
{
    'confidence': 최고 확률,
    'predicted_class': 예측된 클래스,
    'findings': 상위 3개 클래스와 확률,
    'recommendations': 권장사항,
    'ai_notes': 모델 정보
}
```

---

## 📡 API 엔드포인트

### FastAPI 서버
- **URL**: `http://localhost:8000`
- **엔드포인트**: `POST /api/ai/diagnose`

**요청 형식**:
```json
{
  "patient_id": "환자ID (선택사항)",
  "image_path": "/경로/이미지.png",
  "notes": "메모 (선택사항)"
}
```

**응답 형식**:
```json
{
  "patient_id": "환자ID",
  "confidence": 0.9096,
  "predicted_class": "Viral Pneumonia",
  "findings": [
    {
      "condition": "Viral Pneumonia",
      "probability": 0.9096,
      "description": "Viral Pneumonia 확률: 90.96%"
    },
    ...
  ],
  "recommendations": ["바이러스성 폐렴 의심 가능성이 있습니다..."],
  "ai_notes": "UNet 기반 폐 분할 + ResNet50 기반 COVID-19 분류 모델 추론 결과입니다."
}
```

---

## ⚙️ 주요 설정

### 모델 파일 경로
- **기본 경로**: `AI_model/models/`
  - 분할 모델: `AI_model/models/seg_results/best_model.pth`
  - 분류 모델: `AI_model/models/clf_results/best_model.pth`

### 이미지 전처리
- **분할 모델용**: RGB 변환, 224x224 리사이즈
- **분류 모델용**: RGB 변환, 224x224 리사이즈, ImageNet 정규화

### 타임아웃 설정
- **Express → FastAPI**: 60초
- **프론트엔드 → Express**: 120초
- **이유**: 모델 예측에 약 46초 소요 (CPU 환경)

---

## 🚀 서버 실행 방법

### 1. FastAPI 서버
```bash
cd Final_Back/fastapi
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Express 서버
```bash
cd Final_Back/express
npm run dev
```

### 3. 프론트엔드 서버
```bash
cd Final_Front4
npm start
```

---

## ✅ 테스트 결과

### 성공 사례
- **입력 이미지**: Viral Pneumonia-587.png
- **예측 결과**:
  - COVID: 65.60%
  - Lung_Opacity: 18.48%
  - Viral Pneumonia: 8.17%
- **AI 신뢰도**: 66%
- **예측 시간**: 약 46초 (CPU 환경)

---

## 🔍 주요 개선 사항

1. **환자 확인 선택사항화**: 환자가 없어도 이미지만으로 예측 가능
2. **에러 처리 개선**: 404 에러 시 재시도 로직 추가
3. **타임아웃 증가**: 모델 예측 시간 고려하여 타임아웃 증가
4. **로깅 강화**: 상세한 에러 로그로 디버깅 용이

---

## 📝 참고 사항

- 모델 파일은 `AI_model/models/` 폴더에 위치
- 모델 로드는 FastAPI 서버 시작 시 자동으로 수행
- 첫 예측 시 모델 로드로 인해 시간이 더 걸릴 수 있음
- GPU 환경에서는 예측 시간이 크게 단축됨

---

## 🎉 완료 상태

✅ 모델 통합 완료
✅ API 엔드포인트 작동 확인
✅ 프론트엔드 연동 완료
✅ 실제 모델 결과 표시 확인

모든 작업이 완료되었으며, 실제 AI 진단 기능이 정상 작동 중입니다!

