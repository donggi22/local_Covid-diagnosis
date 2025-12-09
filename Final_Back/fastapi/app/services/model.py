from __future__ import annotations

from pathlib import Path
from typing import Dict, List
import numpy as np
import os

import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms, models
import cv2

from app.core.config import get_settings


BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
AI_MODEL_DIR = BASE_DIR / 'AI_model'

# ==========================================
# 모델 정의
# ==========================================

class DoubleConv(nn.Module):
    """(convolution => [BN] => ReLU) * 2"""
    
    def __init__(self, in_channels, out_channels, mid_channels=None):
        super().__init__()
        if not mid_channels:
            mid_channels = out_channels
        self.double_conv = nn.Sequential(
            nn.Conv2d(in_channels, mid_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(mid_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(mid_channels, out_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        return self.double_conv(x)


class Down(nn.Module):
    """Downscaling with maxpool then double conv"""
    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.maxpool_conv = nn.Sequential(
            nn.MaxPool2d(2),
            DoubleConv(in_channels, out_channels)
        )

    def forward(self, x):
        return self.maxpool_conv(x)


class Up(nn.Module):
    """Upscaling then double conv"""
    def __init__(self, in_channels, out_channels, bilinear=True):
        super().__init__()
        if bilinear:
            self.up = nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True)
            self.conv = DoubleConv(in_channels, out_channels, in_channels // 2)
        else:
            self.up = nn.ConvTranspose2d(in_channels, in_channels // 2, kernel_size=2, stride=2)
            self.conv = DoubleConv(in_channels, out_channels)

    def forward(self, x1, x2):
        x1 = self.up(x1)
        diffY = x2.size()[2] - x1.size()[2]
        diffX = x2.size()[3] - x1.size()[3]
        x1 = F.pad(x1, [diffX // 2, diffX - diffX // 2,
                        diffY // 2, diffY - diffY // 2])
        x = torch.cat([x2, x1], dim=1)
        return self.conv(x)


class OutConv(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(OutConv, self).__init__()
        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size=1)

    def forward(self, x):
        return self.conv(x)


class UNet(nn.Module):
    """Standard U-Net architecture for lung segmentation"""
    def __init__(self, n_channels=3, n_classes=1, bilinear=False):
        super(UNet, self).__init__()
        self.n_channels = n_channels
        self.n_classes = n_classes
        self.bilinear = bilinear

        self.inc = DoubleConv(n_channels, 64)
        self.down1 = Down(64, 128)
        self.down2 = Down(128, 256)
        self.down3 = Down(256, 512)
        factor = 2 if bilinear else 1
        self.down4 = Down(512, 1024 // factor)
        self.up1 = Up(1024, 512 // factor, bilinear)
        self.up2 = Up(512, 256 // factor, bilinear)
        self.up3 = Up(256, 128 // factor, bilinear)
        self.up4 = Up(128, 64, bilinear)
        self.outc = OutConv(64, n_classes)

    def forward(self, x):
        x1 = self.inc(x)
        x2 = self.down1(x1)
        x3 = self.down2(x2)
        x4 = self.down3(x3)
        x5 = self.down4(x4)
        x = self.up1(x5, x4)
        x = self.up2(x, x3)
        x = self.up3(x, x2)
        x = self.up4(x, x1)
        logits = self.outc(x)
        return logits


class COVID19Classifier(nn.Module):
    """ResNet 기반 COVID-19 분류 모델"""
    
    def __init__(self, num_classes=4, pretrained=False):
        super(COVID19Classifier, self).__init__()
        if pretrained:
            self.backbone = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
        else:
            self.backbone = models.resnet50(weights=None)
        num_features = self.backbone.fc.in_features
        self.backbone.fc = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(num_features, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, num_classes)
        )
    
    def forward(self, x):
        return self.backbone(x)


# ==========================================
# 전역 변수
# ==========================================

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
_segmentation_model: UNet | None = None
_classification_model: COVID19Classifier | None = None

CLASS_NAMES = ['COVID', 'Lung_Opacity', 'Normal', 'Viral Pneumonia']

# 분류 모델용 transform
_classification_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                        std=[0.229, 0.224, 0.225])
])

# 분할 모델용 transform (RGB 이미지)
_segmentation_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                        std=[0.229, 0.224, 0.225])
])


# ==========================================
# 모델 로드 함수
# ==========================================

def load_model() -> None:
    """분할 모델과 분류 모델을 로드한다."""
    global _segmentation_model, _classification_model
    
    if _segmentation_model is not None and _classification_model is not None:
        return
    
    # 모델 경로 설정
    seg_model_path = AI_MODEL_DIR / 'models' / 'seg_results' / 'best_model.pth'
    clf_model_path = AI_MODEL_DIR / 'models' / 'clf_results' / 'best_model.pth'
    
    # 모델 파일이 없으면 다운로드 시도 (Render 배포 환경)
    if not seg_model_path.exists() or not clf_model_path.exists():
        print("⚠️  모델 파일이 없습니다. GitHub Release에서 다운로드를 시도합니다...")
        try:
            import sys
            from pathlib import Path
            # download_models.py가 있는 경로 추가
            download_script_path = Path(__file__).parent.parent.parent / 'download_models.py'
            if download_script_path.exists():
                import subprocess
                result = subprocess.run(
                    [sys.executable, str(download_script_path)],
                    capture_output=True,
                    text=True,
                    timeout=600  # 10분 타임아웃
                )
                if result.returncode == 0:
                    print("✅ 모델 파일 다운로드 완료")
                else:
                    print(f"⚠️  모델 다운로드 실패: {result.stderr}")
                    raise FileNotFoundError(f"모델 파일을 찾을 수 없고 다운로드도 실패했습니다: {seg_model_path}")
            else:
                print(f"⚠️  download_models.py를 찾을 수 없습니다: {download_script_path}")
                raise FileNotFoundError(f"모델 파일을 찾을 수 없습니다: {seg_model_path}")
        except Exception as e:
            print(f"❌ 모델 다운로드 중 오류 발생: {e}")
            raise FileNotFoundError(f"모델 파일을 찾을 수 없습니다: {seg_model_path}")
    
    # 분할 모델 로드
    if not seg_model_path.exists():
        raise FileNotFoundError(f"분할 모델 파일을 찾을 수 없습니다: {seg_model_path}")
    
    _segmentation_model = UNet(n_channels=3, n_classes=1, bilinear=False)
    seg_checkpoint = torch.load(seg_model_path, map_location=device)
    if isinstance(seg_checkpoint, dict) and 'model_state_dict' in seg_checkpoint:
        _segmentation_model.load_state_dict(seg_checkpoint['model_state_dict'], strict=False)
    else:
        _segmentation_model.load_state_dict(seg_checkpoint, strict=False)
    _segmentation_model.to(device)
    _segmentation_model.eval()
    
    # 분류 모델 로드
    if not clf_model_path.exists():
        raise FileNotFoundError(f"분류 모델 파일을 찾을 수 없습니다: {clf_model_path}")
    
    _classification_model = COVID19Classifier(num_classes=4, pretrained=False)
    clf_checkpoint = torch.load(clf_model_path, map_location=device)
    if isinstance(clf_checkpoint, dict) and 'model_state_dict' in clf_checkpoint:
        _classification_model.load_state_dict(clf_checkpoint['model_state_dict'], strict=False)
    else:
        _classification_model.load_state_dict(clf_checkpoint, strict=False)
    _classification_model.to(device)
    _classification_model.eval()
    
    # 모델 파라미터 수 확인
    seg_params = sum(p.numel() for p in _segmentation_model.parameters())
    clf_params = sum(p.numel() for p in _classification_model.parameters())
    
    print(f'✅ AI 모델 로드 완료 (device: {device})')
    print(f'  - 분할 모델: {seg_model_path}')
    print(f'    * 파라미터 수: {seg_params:,}개')
    print(f'  - 분류 모델: {clf_model_path}')
    print(f'    * 파라미터 수: {clf_params:,}개')
    print(f'  - 총 파라미터 수: {seg_params + clf_params:,}개')
    
    # 모델 가중치 샘플 확인 (실제로 로드되었는지)
    seg_first_weight = next(_segmentation_model.parameters()).data[0, 0, 0, 0].item()
    clf_first_weight = next(_classification_model.parameters()).data[0, 0, 0, 0].item()
    print(f'  - 분할 모델 첫 번째 가중치 샘플: {seg_first_weight:.6f}')
    print(f'  - 분류 모델 첫 번째 가중치 샘플: {clf_first_weight:.6f}')


def unload_model() -> None:
    """모델을 메모리에서 해제한다."""
    global _segmentation_model, _classification_model
    _segmentation_model = None
    _classification_model = None


# ==========================================
# 전처리 및 예측 함수
# ==========================================

def _segment_lung(image_tensor: torch.Tensor, threshold: float = 0.5) -> torch.Tensor:
    """폐 영역을 분할한다."""
    if _segmentation_model is None:
        load_model()
    
    assert _segmentation_model is not None
    
    print(f'  🔬 분할 모델 입력 shape: {image_tensor.shape}, device: {image_tensor.device}')
    with torch.no_grad():
        import time
        forward_start = time.time()
        mask_logits = _segmentation_model(image_tensor.to(device))
        forward_time = time.time() - forward_start
        print(f'  🔬 분할 모델 forward pass 완료: {forward_time:.4f}초')
        print(f'  🔬 분할 모델 출력 shape: {mask_logits.shape}')
        mask = torch.sigmoid(mask_logits) > threshold
        return mask.float()


def _preprocess_image(image_path: Path) -> torch.Tensor:
    """이미지를 전처리한다 (RGB로 변환)."""
    image = Image.open(image_path).convert('RGB')
    tensor = _segmentation_transform(image).unsqueeze(0)
    return tensor

# GradCAM 생성 전에 역정규화된 이미지 준비
def _denormalize_image(tensor: torch.Tensor) -> Image.Image:
    """정규화된 tensor를 원본 이미지로 복원"""
    mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
    std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)
    
    # 역정규화
    tensor = tensor.squeeze(0).cpu() * std + mean
    tensor = torch.clamp(tensor, 0, 1)
    
    # PIL Image로 변환
    return transforms.ToPILImage()(tensor)

def _preprocess_for_classification(image_path: Path, mask: torch.Tensor) -> torch.Tensor:
    """원본 이미지에 마스크 적용 후 분류용으로 전처리"""
    # 1. 원본 이미지 로드 (정규화 X)
    image = Image.open(image_path).convert('RGB')
    image = transforms.Resize((224, 224))(image)
    image_np = np.array(image).astype(np.float32) / 255.0
    
    # 2. 마스크 적용
    mask_np = mask.squeeze().cpu().numpy()
    mask_3ch = np.stack([mask_np] * 3, axis=-1)
    segmented = image_np * mask_3ch
    
    # 3. PIL로 변환 후 분류용 transform (정규화 포함)
    segmented_pil = Image.fromarray((segmented * 255).astype(np.uint8))
    tensor = _classification_transform(segmented_pil).unsqueeze(0)
    return tensor


def _generate_gradcam(model: nn.Module, input_tensor: torch.Tensor, target_class: int, layer_name: str = 'layer4') -> np.ndarray:
    """Grad-CAM 히트맵을 생성한다."""
    model.eval()
    
    # Gradient를 저장할 hook 등록
    gradients = []
    activations = []
    
    def backward_hook(module, grad_input, grad_output):
        gradients.append(grad_output[0])
    
    def forward_hook(module, input, output):
        activations.append(output)
    
    # ResNet50의 마지막 convolutional layer 찾기
    target_layer = None
    if hasattr(model, 'backbone'):
        # COVID19Classifier의 경우 backbone이 ResNet50
        if hasattr(model.backbone, layer_name):
            target_layer = getattr(model.backbone, layer_name)
        elif hasattr(model.backbone, 'layer4'):
            target_layer = model.backbone.layer4
    else:
        # 직접 접근
        if hasattr(model, layer_name):
            target_layer = getattr(model, layer_name)
    
    if target_layer is None:
        print('⚠️ Grad-CAM: target layer를 찾을 수 없습니다. layer4를 찾을 수 없습니다.')
        return None
    
    # Hook 등록
    forward_handle = target_layer.register_forward_hook(forward_hook)
    backward_handle = target_layer.register_backward_hook(backward_hook)
    
    try:
        # Forward pass
        input_tensor.requires_grad_(True)
        output = model(input_tensor)
        
        # Target class에 대한 gradient 계산
        model.zero_grad()
        target_output = output[0, target_class]
        target_output.backward()
        
        # Gradient와 activation 가져오기
        if len(gradients) == 0 or len(activations) == 0:
            return None
        
        grad = gradients[0]
        act = activations[0]
        
        # Gradient의 global average pooling
        weights = torch.mean(grad, dim=(2, 3), keepdim=True)
        
        # Weighted combination of activation maps
        cam = torch.sum(weights * act, dim=1, keepdim=True)
        cam = F.relu(cam)
        
        # Normalize
        cam = cam.squeeze().cpu().detach().numpy()
        cam = cam - cam.min()
        cam = cam / (cam.max() + 1e-8)
        
        return cam
        
    finally:
        # Hook 제거
        forward_handle.remove()
        backward_handle.remove()
        input_tensor.requires_grad_(False)


def _generate_gradcam_plus(model: nn.Module, input_tensor: torch.Tensor, target_class: int, layer_name: str = 'layer4') -> np.ndarray:
    """Grad-CAM++ 히트맵을 생성한다."""
    model.eval()
    
    gradients = []
    activations = []
    
    def backward_hook(module, grad_input, grad_output):
        gradients.append(grad_output[0])
    
    def forward_hook(module, input, output):
        activations.append(output)
    
    # 타겟 레이어 찾기
    target_layer = None
    if hasattr(model, 'backbone'):
        if hasattr(model.backbone, layer_name):
            target_layer = getattr(model.backbone, layer_name)
        elif hasattr(model.backbone, 'layer4'):
            target_layer = model.backbone.layer4
    else:
        if hasattr(model, layer_name):
            target_layer = getattr(model, layer_name)
    
    if target_layer is None:
        print('⚠️ Grad-CAM++: target layer를 찾을 수 없습니다.')
        return None
    
    forward_handle = target_layer.register_forward_hook(forward_hook)
    backward_handle = target_layer.register_backward_hook(backward_hook)
    
    try:
        input_tensor.requires_grad_(True)
        output = model(input_tensor)
        
        model.zero_grad()
        target_output = output[0, target_class]
        target_output.backward()
        
        if len(gradients) == 0 or len(activations) == 0:
            return None
        
        grad = gradients[0]
        act = activations[0]
        
        # Grad-CAM++: 올바른 alpha 계산 공식
        # alpha_ij^kc = (grad_ij^kc)^2 / (2 * (grad_ij^kc)^2 + sum_ab(act_ab^kc * grad_ab^kc))
        grad_squared = grad.pow(2)
        grad_sum = torch.sum(act * grad, dim=(2, 3), keepdim=True)
        alpha = grad_squared / (2 * grad_squared + grad_sum + 1e-8)
        alpha = F.relu(alpha)
        
        # Weighted combination: sum over spatial dimensions
        cam = torch.sum(alpha * F.relu(grad) * act, dim=1, keepdim=True)
        cam = F.relu(cam)
        
        cam = cam.squeeze().cpu().detach().numpy()
        cam = cam - cam.min()
        cam = cam / (cam.max() + 1e-8)
        
        return cam
        
    finally:
        forward_handle.remove()
        backward_handle.remove()
        input_tensor.requires_grad_(False)


def _generate_layercam(model: nn.Module, input_tensor: torch.Tensor, target_class: int, layer_name: str = 'layer4') -> np.ndarray:
    """Layer-CAM 히트맵을 생성한다."""
    model.eval()
    
    gradients = []
    activations = []
    
    def backward_hook(module, grad_input, grad_output):
        if grad_output[0] is not None:
            gradients.append(grad_output[0].clone())
    
    def forward_hook(module, input, output):
        activations.append(output.clone())
    
    # 타겟 레이어 찾기
    target_layer = None
    if hasattr(model, 'backbone'):
        if hasattr(model.backbone, layer_name):
            target_layer = getattr(model.backbone, layer_name)
        elif hasattr(model.backbone, 'layer4'):
            target_layer = model.backbone.layer4
    else:
        if hasattr(model, layer_name):
            target_layer = getattr(model, layer_name)
    
    if target_layer is None:
        print('⚠️ Layer-CAM: target layer를 찾을 수 없습니다.')
        return None
    
    forward_handle = target_layer.register_forward_hook(forward_hook)
    backward_handle = target_layer.register_backward_hook(backward_hook)
    
    try:
        input_tensor.requires_grad_(True)
        output = model(input_tensor)
        
        model.zero_grad()
        target_output = output[0, target_class]
        target_output.backward(retain_graph=False)
        
        if len(gradients) == 0 or len(activations) == 0:
            print('⚠️ Layer-CAM: gradient 또는 activation을 가져올 수 없습니다.')
            return None
        
        grad = gradients[0]
        act = activations[0]
        
        # Shape 확인 및 디버깅
        if grad.shape != act.shape:
            print(f'⚠️ Layer-CAM: gradient shape {grad.shape} != activation shape {act.shape}')
            # Shape이 다르면 activation shape에 맞춰 gradient를 조정
            if grad.shape[2:] != act.shape[2:]:
                grad = F.interpolate(grad, size=act.shape[2:], mode='bilinear', align_corners=False)
        
        # Layer-CAM 알고리즘: 
        # 1. Gradient의 양수 부분만 사용 (ReLU on gradient)
        # 2. Activation에는 ReLU를 적용하지 않음 (원본 사용)
        # 3. Gradient와 activation을 element-wise 곱
        # 4. 채널별로 합산
        # 5. 최종 결과에 ReLU 적용
        
        # Gradient에만 ReLU 적용 (양수 부분만 사용)
        grad_positive = F.relu(grad)
        
        # Activation은 원본 그대로 사용 (ReLU 적용하지 않음)
        # Layer-CAM은 activation의 음수 값도 중요할 수 있음
        
        # 디버깅: gradient와 activation의 통계 정보 출력
        print(f'    📊 Layer-CAM 디버깅:')
        print(f'      - Gradient shape: {grad.shape}, min={grad.min().item():.6f}, max={grad.max().item():.6f}, mean={grad.mean().item():.6f}')
        print(f'      - Gradient (positive) min={grad_positive.min().item():.6f}, max={grad_positive.max().item():.6f}, mean={grad_positive.mean().item():.6f}')
        print(f'      - Activation shape: {act.shape}, min={act.min().item():.6f}, max={act.max().item():.6f}, mean={act.mean().item():.6f}')
        
        # Element-wise 곱셈: ReLU(gradient) * activation
        # 이렇게 하면 gradient가 양수인 영역에서만 activation이 강조됨
        cam = grad_positive * act
        
        print(f'      - CAM (before sum) shape: {cam.shape}, min={cam.min().item():.6f}, max={cam.max().item():.6f}, mean={cam.mean().item():.6f}')
        
        # 채널 차원(dim=1)을 따라 합산하여 공간적 히트맵 생성
        cam = torch.sum(cam, dim=1, keepdim=True)
        # 최종 결과에만 ReLU 적용
        cam = F.relu(cam)
        
        print(f'      - CAM (after sum) shape: {cam.shape}, min={cam.min().item():.6f}, max={cam.max().item():.6f}, mean={cam.mean().item():.6f}')
        
        # 배치 차원 제거 및 numpy 변환
        if cam.dim() > 2:
            cam = cam.squeeze()
        if cam.dim() == 0:
            cam = cam.unsqueeze(0)
        cam = cam.cpu().detach().numpy()
        
        # 정규화
        cam_min = cam.min()
        cam_max = cam.max()
        if cam_max > cam_min:
            cam = (cam - cam_min) / (cam_max - cam_min + 1e-8)
        else:
            print(f'      ⚠️ Layer-CAM: 모든 값이 동일합니다 (값={cam_min:.6f})')
            cam = np.ones_like(cam) * 0.5  # 중간값으로 설정하여 히트맵이 보이도록
        
        print(f'      - CAM (normalized) min={cam.min():.6f}, max={cam.max():.6f}, mean={cam.mean():.6f}')
        
        # 최소값 확인 (디버깅)
        if cam.max() < 0.01:
            print(f'      ⚠️ Layer-CAM: 히트맵 값이 너무 작습니다 (max={cam.max():.6f})')
            # 히트맵이 너무 작으면 최소한의 가시성을 위해 스케일 조정
            cam = cam * (0.3 / (cam.max() + 1e-8))  # 최소 0.3까지 스케일
        
        return cam
        
    except Exception as e:
        print(f'❌ Layer-CAM 생성 중 오류: {str(e)}')
        import traceback
        traceback.print_exc()
        return None
    finally:
        forward_handle.remove()
        backward_handle.remove()
        input_tensor.requires_grad_(False)


def _save_gradcam_image(original_image: Image.Image, gradcam: np.ndarray, mask: torch.Tensor, output_path: Path) -> Path:
    """Grad-CAM 히트맵을 원본 이미지에 오버레이하여 저장한다."""
    # 원본 이미지를 numpy 배열로 변환
    original_image_resized = original_image.resize((224, 224))
    img_array = np.array(original_image_resized)
    
    # Grad-CAM을 원본 이미지 크기로 리사이즈
    gradcam_resized = cv2.resize(gradcam, (img_array.shape[1], img_array.shape[0]))
    gradcam_resized = np.uint8(255 * gradcam_resized)
    
    # 히트맵 생성 (Jet colormap)
    heatmap = cv2.applyColorMap(gradcam_resized, cv2.COLORMAP_JET)
    heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
    
    # 원본 이미지와 히트맵 오버레이 (0.4 투명도), 그레이 스케일 처리
    if len(img_array.shape) == 2:
        img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2RGB)

    # 마스크를 numpy로 변환 및 리사이즈
    mask_np = mask.squeeze().cpu().numpy()
    mask_resized = cv2.resize(mask_np, (224, 224), interpolation=cv2.INTER_NEAREST)
    
    overlayed = cv2.addWeighted(img_array, 0.6, heatmap, 0.4, 0)

    # 마스크 영역만 오버레이, 나머지는 원본 유지
    result = img_array.copy()
    mask_bool = mask_resized > 0.5
    result[mask_bool] = overlayed[mask_bool]
    
    # 이미지 저장
    output_path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(overlayed).save(output_path)
    
    return output_path


def predict(image_path: Path) -> Dict[str, object]:
    """이미지를 예측한다 (분할 → 분류 파이프라인)."""
    import time
    
    if _segmentation_model is None or _classification_model is None:
        load_model()
    
    print(f'🔍 이미지 예측 시작: {image_path}')
    
    # 1. Segmentation용 이미지 전처리 (정규화 O)
    step_start = time.time()
    image_tensor = _preprocess_image(image_path)
    print(f'  ✓ Segmentation 전처리 완료: {time.time() - step_start:.2f}초')
    
    # 2. 폐 영역 분할
    step_start = time.time()
    mask = _segment_lung(image_tensor)
    print(f'  ✓ 폐 영역 분할 완료: {time.time() - step_start:.2f}초')
    
    # 3. 원본 이미지에 마스크 적용 후 분류용 전처리 (수정!)
    step_start = time.time()
    segmented_tensor = _preprocess_for_classification(image_path, mask)  # image_path 전달!
    print(f'  ✓ 분류 전처리 완료: {time.time() - step_start:.2f}초')
    
    # 4. 분류 예측
    step_start = time.time()
    segmented_tensor_grad = segmented_tensor.clone().to(device)
    segmented_tensor_grad.requires_grad_(True)
    
    with torch.no_grad():
        outputs = _classification_model(segmented_tensor.to(device))
        probabilities = torch.softmax(outputs, dim=1).squeeze(0)
    
    print(f'  ✓ 분류 예측 완료: {time.time() - step_start:.2f}초')
    
    probs = probabilities.cpu().numpy()
    top_indices = probs.argsort()[::-1][:3]
    
    findings = []
    for idx in top_indices:
        findings.append({
            'condition': CLASS_NAMES[idx],
            'probability': float(probs[idx]),
            'description': f'{CLASS_NAMES[idx]} 확률: {probs[idx]:.2%}'
        })
    
    confidence = float(probs[top_indices[0]])
    predicted_class = CLASS_NAMES[top_indices[0]]
    predicted_class_idx = top_indices[0]
    
    # 5. GradCAM 생성 (수정!)
    gradcam_relative_path = None
    gradcam_plus_relative_path = None
    layercam_relative_path = None
    
    try:
        print(f'  🎨 CAM 생성 시작...')
        cam_start = time.time()
        
        # 역정규화된 이미지 준비 (GradCAM이 본 것과 동일한 이미지)
        # segmented_tensor를 역정규화
        # mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
        # std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)
        # denorm_tensor = segmented_tensor.squeeze(0).cpu() * std + mean
        # denorm_tensor = torch.clamp(denorm_tensor, 0, 1)
        original_image = Image.open(image_path).convert('RGB')
        
        gradcam_base = os.getenv('GRADCAM_STORAGE_PATH', str(BASE_DIR / 'Final_Back' / 'fastapi' / 'app' / 'static'))
        static_dir = Path(gradcam_base)
        gradcam_dir = static_dir / 'gradcam'
        gradcam_dir.mkdir(parents=True, exist_ok=True)
        
        # Grad-CAM 생성
        print(f'    📊 Grad-CAM 생성 중...')
        gradcam = _generate_gradcam(
            _classification_model,
            segmented_tensor_grad,
            target_class=predicted_class_idx,
            layer_name='layer4'
        )
        if gradcam is not None:
            gradcam_filename = f"gradcam_{image_path.stem}_{predicted_class_idx}.png"
            gradcam_path = gradcam_dir / gradcam_filename
            _save_gradcam_image(original_image, gradcam, mask, gradcam_path)
            gradcam_relative_path = f"/static/gradcam/{gradcam_filename}"
            print(f'    ✓ Grad-CAM 생성 완료')
        
        # Grad-CAM++ 생성
        print(f'    📊 Grad-CAM++ 생성 중...')
        gradcam_plus = _generate_gradcam_plus(
            _classification_model,
            segmented_tensor_grad,
            target_class=predicted_class_idx,
            layer_name='layer4'
        )
        if gradcam_plus is not None:
            gradcam_plus_filename = f"gradcam_plus_{image_path.stem}_{predicted_class_idx}.png"
            gradcam_plus_path = gradcam_dir / gradcam_plus_filename
            _save_gradcam_image(original_image, gradcam_plus, mask, gradcam_plus_path)
            gradcam_plus_relative_path = f"/static/gradcam/{gradcam_plus_filename}"
            print(f'    ✓ Grad-CAM++ 생성 완료')
        
        # Layer-CAM 생성
        print(f'    📊 Layer-CAM 생성 중...')
        layercam = _generate_layercam(
            _classification_model,
            segmented_tensor_grad,
            target_class=predicted_class_idx,
            layer_name='layer4'
        )
        if layercam is not None:
            layercam_filename = f"layercam_{image_path.stem}_{predicted_class_idx}.png"
            layercam_path = gradcam_dir / layercam_filename
            _save_gradcam_image(original_image, layercam, mask, layercam_path)
            layercam_relative_path = f"/static/gradcam/{layercam_filename}"
            print(f'    ✓ Layer-CAM 생성 완료')
        
        print(f'  ✓ 모든 CAM 생성 완료: {time.time() - cam_start:.2f}초')
        
    except Exception as e:
        print(f'  ⚠️ CAM 생성 중 오류 발생: {str(e)}')
        import traceback
        traceback.print_exc()
    
    recommendations = []
    if confidence > 0.7:
        if predicted_class == 'COVID':
            recommendations.append('COVID-19 의심 가능성이 높습니다. 즉시 전문의 상담 및 추가 검진을 권장합니다.')
        elif predicted_class == 'Viral Pneumonia':
            recommendations.append('바이러스성 폐렴 의심 가능성이 있습니다. 전문의 상담을 권장합니다.')
        else:
            recommendations.append('추가 검진 및 전문의 상담을 권장합니다.')
    elif confidence < 0.3:
        recommendations.append('주기적인 관찰이 필요합니다.')
    else:
        recommendations.append('추가 검진을 권장합니다.')
    
    result = {
        'confidence': confidence,
        'predicted_class': predicted_class,
        'findings': findings,
        'recommendations': recommendations,
        'ai_notes': 'UNet 기반 폐 분할 + ResNet50 기반 COVID-19 분류 모델 추론 결과입니다.'
    }
    
    if gradcam_relative_path:
        result['gradcam_path'] = gradcam_relative_path
    if gradcam_plus_relative_path:
        result['gradcam_plus_path'] = gradcam_plus_relative_path
    if layercam_relative_path:
        result['layercam_path'] = layercam_relative_path
    
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        
    return result