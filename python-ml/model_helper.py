import torch, cv2, numpy as np
from transformers import AutoImageProcessor, AutoModelForImageClassification
from PIL import Image
from facenet_pytorch import MTCNN
from temporal_model import TemporalConsistencyModel
import warnings, logging

warnings.filterwarnings("ignore")

# ---------- Logger Setup ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ---------- Face Detector ----------
face_detector = MTCNN(keep_all=False, device=device)

# ---------- Temporal Model ----------
temporal_model = TemporalConsistencyModel(window=7, alpha=0.75)

# ---------- Model Definitions ----------
MODEL_PATHS = [
    "prithivMLmods/Deepfake-Detection-FFPP-Xception",      # CNN (FF++)
    
    "Wvolf/ViT_Deepfake_Detection",                        # ViT (DFDC)
    "microsoft/beit-large-patch16-224-pt22k-ft22k"         # BEiT (robust texture)
]

models, processors = [], []
for mid in MODEL_PATHS:
    try:
        proc = AutoImageProcessor.from_pretrained(mid)
        model = AutoModelForImageClassification.from_pretrained(mid).to(device)
        model.eval()
        models.append(model)
        processors.append(proc)
        logger.info(f"✅ Loaded model: {mid}")
    except Exception as e:
        logger.warning(f"⚠️ Failed to load {mid}: {e}")

# ---------- Heuristic ----------
def heuristic_texture_analysis(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    freq = np.fft.fft2(gray)
    freq_shift = np.fft.fftshift(freq)
    mag = np.log(np.abs(freq_shift) + 1)
    edge_var = np.var(cv2.Laplacian(gray, cv2.CV_64F))
    texture_score = np.mean(mag) / (edge_var + 1e-5)
    norm_score = np.clip(np.tanh(texture_score / 60), 0, 1)
    return float(norm_score)

# ---------- Face Cropper (Fixed) ----------
def extract_face(frame):
    boxes, _ = face_detector.detect(frame)
    if boxes is not None and len(boxes) > 0:
        x1, y1, x2, y2 = [int(b) for b in boxes[0]]
        face = frame[y1:y2, x1:x2]

        if face is None or face.size == 0:
            logger.warning("⚠️ Detected invalid face region; skipping frame.")
            return None

        return cv2.resize(face, (224, 224))
    else:
        logger.info("ℹ️ No face detected in this frame; skipping.")
        return None

# ---------- Prediction ----------
def predict_frame(frame):
    face_img = extract_face(frame)
    if face_img is None:
        return None  # skip frame gracefully

    frame_img = Image.fromarray(cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB))
    preds = []

    for model, proc in zip(models, processors):
        try:
            inputs = proc(images=frame_img, return_tensors="pt").to(device)
            with torch.no_grad():
                logits = model(**inputs).logits
                probs = torch.nn.functional.softmax(logits, dim=-1)[0].cpu().numpy()

            id2label = model.config.id2label
            label_idx = np.argmax(probs)

            if str(label_idx) in id2label:
                label = id2label[str(label_idx)].lower()
            elif label_idx in id2label:
                label = id2label[label_idx].lower()
            else:
                label = "unknown"

            is_fake = any(k in label for k in ["fake", "forged", "manipulated", "edited"])
            confidence = float(probs[label_idx])

            score = confidence if is_fake else 1 - confidence
            preds.append(score)

        except Exception as e:
            logger.warning(f"⚠️ Model prediction failed for {model.__class__.__name__}: {e}")

    if not preds:
        logger.warning("⚠️ No valid model predictions; skipping frame.")
        return None

    # Weighted average (CNN:0.4, ViT:0.35, BEiT:0.25)
    weights = np.array([0.4, 0.35, 0.25])[:len(preds)]
    weights /= weights.sum()
    weighted_score = np.dot(preds, weights)
    return float(np.clip(weighted_score, 0, 1))

# ---------- Main Pipeline ----------
def ensemble_predict_video(video_path, frame_interval=10):
    cap = cv2.VideoCapture(video_path)
    frame_preds, heuristics = [], []
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            model_score = predict_frame(frame)
            if model_score is None:
                frame_count += 1
                continue

            heuristic_score = heuristic_texture_analysis(frame)
            combined_score = 0.8 * model_score + 0.2 * heuristic_score
            temporal_score = temporal_model.update(combined_score)

            frame_preds.append(temporal_score)
            heuristics.append(heuristic_score)

        frame_count += 1

    cap.release()

    if not frame_preds:
        logger.error("❌ No valid frames processed. Returning unknown result.")
        return {"top": {"label": "unknown", "score": 0.0}}

    model_score = float(np.mean(frame_preds))
    heuristic_score = float(np.mean(heuristics))
    final_score = float(np.clip(model_score, 0, 1))

    logger.info(f"✅ Video processed | Final Score: {final_score:.4f}")

    return {
        "top": {
            "label": "fake" if final_score > 0.55 else "real",
            "score": round(final_score, 4)
        },
        "model_score": round(model_score, 4),
        "heuristic_score": round(heuristic_score, 4),
    }

# ---------- Compatibility Wrapper ----------
def ensemble_predict_from_path(video_path):
    """Compatibility wrapper for main.py"""
    return ensemble_predict_video(video_path)


#***********************************************************************************************************************************************************************************************************************

