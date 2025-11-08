# # image_model_core.py
# import os
# import logging
# import warnings
# import numpy as np
# from PIL import Image
# import cv2
# import torch
# from transformers import AutoImageProcessor, AutoModelForImageClassification

# warnings.filterwarnings("ignore")
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)

# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# logger.info(f"Using device: {device}")

# # --- Face detector: prefer RetinaFace if installed, otherwise fallback to MTCNN ---
# USE_RETINA = False
# try:
#     # retina-face package (pip install retina-face)
#     from retinaface import RetinaFace
#     USE_RETINA = True
#     logger.info("Using RetinaFace for face detection (retina-face).")
# except Exception:
#     try:
#         # alternative retinaface implementation
#         from retinaface_pytorch import RetinaFaceDetector  # optional naming
#         USE_RETINA = True
#         logger.info("Using retinaface-pytorch for face detection.")
#     except Exception:
#         USE_RETINA = False

# if not USE_RETINA:
#     try:
#         from facenet_pytorch import MTCNN
#         mtcnn = MTCNN(keep_all=False, device=device)
#         logger.info("RetinaFace not available — falling back to MTCNN.")
#     except Exception:
#         mtcnn = None
#         logger.warning("No RetinaFace or MTCNN available — face detection will be very basic.")


# # ---------- Models ----------
# # Replace the invalid non-existing model id with a working prithiv model or other public deepfake models.
# MODEL_PATHS = [
#     # balanced ensemble: CNN-style deepfake (prithiv), ViT-based and BEiT-based
#     "prithivMLmods/deepfake-detector-model-v1",   # (public prithiv variant) — fallback to a valid prithiv model
#     "Wvolf/ViT_Deepfake_Detection",
#     "microsoft/beit-large-patch16-224-pt22k-ft22k"
# ]

# models = []
# processors = []
# for mid in MODEL_PATHS:
#     try:
#         proc = AutoImageProcessor.from_pretrained(mid)
#         model = AutoModelForImageClassification.from_pretrained(mid).to(device)
#         model.eval()
#         models.append(model)
#         processors.append(proc)
#         logger.info(f"✅ Loaded image model: {mid}")
#     except Exception as e:
#         logger.warning(f"⚠️ Failed to load model {mid}: {e}")

# if len(models) == 0:
#     logger.error("No models could be loaded. Please check MODEL_PATHS and internet / HF auth.")


# # ---------- Heuristics (optimized) ----------
# def _frequency_artifact_score(face_bgr):
#     # faster but stable frequency heuristic
#     gray = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2GRAY)
#     # downsample to small size for FFT to speed up
#     small = cv2.resize(gray, (64, 64), interpolation=cv2.INTER_LINEAR)
#     f = np.fft.fft2(small)
#     fshift = np.fft.fftshift(f)
#     mag = np.log(np.abs(fshift) + 1)
#     high_freq = np.mean(mag[32:, 32:])
#     return float(np.clip(high_freq / 6.0, 0, 1))


# def _illumination_consistency(face_bgr):
#     lab = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2LAB)
#     l_std = np.std(lab[:, :, 0])
#     return float(np.clip(l_std / 64.0, 0, 1))


# def _edge_density(face_bgr):
#     gray = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2GRAY)
#     edges = cv2.Canny(gray, 80, 160)
#     return float(np.clip(np.mean(edges) / 255.0 * 2.0, 0, 1))


# def aggregate_heuristics(face_bgr):
#     # compute all using the same precomputed gray if needed
#     try:
#         return float(np.mean([
#             _frequency_artifact_score(face_bgr),
#             _illumination_consistency(face_bgr),
#             _edge_density(face_bgr)
#         ]))
#     except Exception as e:
#         logger.warning(f"Heuristic error: {e}")
#         return 0.0


# # ---------- Face extraction (robust) ----------
# def _detect_face_boxes(img_bgr):
#     """
#     Return list of bounding boxes in x1,y1,x2,y2 format.
#     """
#     h, w = img_bgr.shape[:2]
#     boxes = []
#     if USE_RETINA:
#         try:
#             # retinaface returns dict or list depending on implementation
#             dets = RetinaFace.detect_faces(img_bgr, align=False)
#             # for many retinaface wrappers dets is dict with keys being faceIDs
#             if isinstance(dets, dict):
#                 for k, v in dets.items():
#                     bb = v.get("facial_area") or v.get("bbox") or None
#                     if bb:
#                         x1, y1, x2, y2 = bb
#                         boxes.append([max(0, int(x1)), max(0, int(y1)), min(w, int(x2)), min(h, int(y2))])
#             elif isinstance(dets, list):
#                 for d in dets:
#                     if len(d) >= 4:
#                         x1, y1, x2, y2 = d[:4]
#                         boxes.append([max(0, int(x1)), max(0, int(y1)), min(w, int(x2)), min(h, int(y2))])
#         except Exception:
#             # some retina wrappers expect RGB; attempt conversion fallback
#             try:
#                 dets = RetinaFace.detect_faces(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB), align=False)
#                 if isinstance(dets, dict):
#                     for k, v in dets.items():
#                         bb = v.get("facial_area") or v.get("bbox") or None
#                         if bb:
#                             x1, y1, x2, y2 = bb
#                             boxes.append([max(0, int(x1)), max(0, int(y1)), min(w, int(x2)), min(h, int(y2))])
#             except Exception as ex:
#                 logger.warning(f"RetinaFace detect exception: {ex}")
#     else:
#         if mtcnn is not None:
#             try:
#                 # mtcnn.detect expects RGB
#                 boxes_mt, _ = mtcnn.detect(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))
#                 if boxes_mt is not None:
#                     for b in boxes_mt:
#                         x1, y1, x2, y2 = [int(max(0, val)) for val in b]
#                         boxes.append([x1, y1, x2, y2])
#             except Exception as e:
#                 logger.warning(f"MTCNN detect failure: {e}")
#     # clamp and filter
#     clean_boxes = []
#     for (x1, y1, x2, y2) in boxes:
#         if x2 - x1 < 10 or y2 - y1 < 10:  # tiny box
#             continue
#         if x1 < 0 or y1 < 0 or x2 <= x1 or y2 <= y1:
#             continue
#         clean_boxes.append([x1, y1, x2, y2])
#     return clean_boxes


# def _extract_face_region(img_bgr):
#     boxes = _detect_face_boxes(img_bgr)
#     if not boxes:
#         return None
#     # pick the largest box
#     boxes = sorted(boxes, key=lambda b: (b[2] - b[0]) * (b[3] - b[1]), reverse=True)
#     x1, y1, x2, y2 = boxes[0]
#     # safe clamp
#     h, w = img_bgr.shape[:2]
#     x1, y1, x2, y2 = max(0, x1), max(0, y1), min(w, x2), min(h, y2)
#     face = img_bgr[y1:y2, x1:x2]
#     if face is None or face.size == 0:
#         return None
#     face = cv2.resize(face, (224, 224), interpolation=cv2.INTER_AREA)
#     return face


# # ---------- Batched inference helper ----------
# def _batched_model_predict(pil_images, batch_size=8):
#     """
#     pil_images: list[PIL.Image]
#     returns: list of per-image composite scores between 0..1 where higher means more "fake"
#     """
#     if len(models) == 0:
#         return [0.0] * len(pil_images)

#     # For each model, produce per-image probabilities; then ensemble across models
#     all_model_scores = []  # shape: (n_models, n_images)
#     for model, proc in zip(models, processors):
#         try:
#             inputs = proc(images=pil_images, return_tensors="pt", padding=True).to(device)
#             # If inputs are large, split by batch
#             logits = None
#             with torch.no_grad():
#                 logits = model(**inputs).logits  # (batch, classes)
#                 probs = torch.nn.functional.softmax(logits, dim=-1).cpu().numpy()
#             # pick predicted class confidence mapped to "fakeness"
#             id2label = model.config.id2label
#             per_img_scores = []
#             for p in probs:
#                 label_idx = int(np.argmax(p))
#                 label = str(id2label.get(str(label_idx), id2label.get(label_idx, "unknown"))).lower()
#                 is_fake = any(k in label for k in ["fake", "manipulated", "forged", "edited"])
#                 conf = float(p[label_idx])
#                 score = conf if is_fake else 1.0 - conf
#                 per_img_scores.append(score)
#             all_model_scores.append(per_img_scores)
#         except Exception as e:
#             logger.warning(f"Model batch predict failed: {e}")
#             # fallback: zeros
#             all_model_scores.append([0.0] * len(pil_images))

#     # ensemble across models
#     all_model_scores = np.array(all_model_scores)  # shape (m, n)
#     # weights proportional to number of models loaded (keep default relative weights)
#     base_weights = np.array([0.4, 0.35, 0.25])[:all_model_scores.shape[0]]
#     if base_weights.sum() == 0:
#         base_weights = np.ones(all_model_scores.shape[0]) / all_model_scores.shape[0]
#     else:
#         base_weights = base_weights / base_weights.sum()
#     weighted = np.dot(base_weights, all_model_scores)  # size n
#     return weighted.tolist()


# # ---------- Public API ----------
# def predict_image(image_path):
#     """
#     Main image-level API (synchronous)
#     Returns dict compatible with your existing responses:
#       { "top": {"label": "fake"/"real", "score": 0.xx}, "model_score": ..., "heuristic_score": ..., "source":"image" }
#     """
#     try:
#         img_bgr = cv2.imread(image_path)
#         if img_bgr is None:
#             return {"error": "cannot_read_image"}

#         face = _extract_face_region(img_bgr)
#         if face is None:
#             # fallback: resize whole image
#             try:
#                 face = cv2.resize(img_bgr, (224, 224), interpolation=cv2.INTER_AREA)
#             except Exception:
#                 return {"error": "no_face_detected"}

#         pil = Image.fromarray(cv2.cvtColor(face, cv2.COLOR_BGR2RGB))
#         model_scores = _batched_model_predict([pil])  # returns list len 1
#         model_score = float(model_scores[0])
#         heuristic_score = aggregate_heuristics(face)
#         final = float(np.clip(0.85 * model_score + 0.15 * heuristic_score, 0, 1))
#         label = "fake" if final > 0.55 else "real"

#         return {
#             "top": {"label": label, "score": round(final, 4)},
#             "model_score": round(model_score, 4),
#             "heuristic_score": round(heuristic_score, 4),
#             "source": "image"
#         }
#     except Exception as e:
#         logger.exception("predict_image failed")
#         return {"error": str(e)}


# ############################3333333333333333333333333333333333333333333333333#############################################################################################################################################333333333333333333


# image_model_core.py
"""
Image detection core (accuracy-first).
- Uses RetinaFace preferred, otherwise MTCNN.
- Runs batched inference (but for single image it's small).
- Uses more model weight on model outputs (0.85) and heuristics 0.15.
"""

import os
import logging
import warnings
import numpy as np
from PIL import Image
import cv2
import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification

warnings.filterwarnings("ignore")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logger.info(f"Device for image_model_core: {device}")

# Prefer RetinaFace, else MTCNN (same approach as model_helper)
USE_RETINA = False
try:
    from retinaface import RetinaFace
    USE_RETINA = True
    logger.info("Using RetinaFace for image face detection.")
except Exception:
    try:
        from facenet_pytorch import MTCNN
        mtcnn = MTCNN(keep_all=False, device=device)
        logger.info("RetinaFace not available — falling back to MTCNN for image pipeline.")
    except Exception:
        mtcnn = None
        logger.warning("No RetinaFace or MTCNN available — image face detection will be basic.")

# models (same ensemble)
MODEL_PATHS = [
    "prithivMLmods/deepfake-detector-model-v1",
    "Wvolf/ViT_Deepfake_Detection",
    "microsoft/beit-large-patch16-224-pt22k-ft22k"
]

models = []
processors = []
def load_image_models():
    global models, processors
    models = []
    processors = []
    for mid in MODEL_PATHS:
        try:
            proc = AutoImageProcessor.from_pretrained(mid, trust_remote_code=False)
            model = AutoModelForImageClassification.from_pretrained(mid).to(device)
            model.eval()
            models.append(model)
            processors.append(proc)
            logger.info(f"✅ Loaded image model: {mid}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to load model {mid}: {e}")

load_image_models()
if len(models) == 0:
    logger.error("No image models loaded. Image detection disabled until models are present.")


# --------------- heuristics ----------------
def _frequency_artifact_score(face_bgr):
    gray = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2GRAY)
    small = cv2.resize(gray, (64,64), interpolation=cv2.INTER_LINEAR)
    f = np.fft.fft2(small)
    fshift = np.fft.fftshift(f)
    mag = np.log(np.abs(fshift) + 1)
    high_freq = np.mean(mag[32:, 32:]) if mag.shape[0] > 32 else np.mean(mag)
    return float(np.clip(high_freq / 6.0, 0, 1))


def _illumination_consistency(face_bgr):
    lab = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2LAB)
    l_std = np.std(lab[:,:,0])
    return float(np.clip(l_std / 64.0, 0, 1))


def _edge_density(face_bgr):
    gray = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 80, 160)
    return float(np.clip(np.mean(edges) / 255.0 * 2.0, 0, 1))


def aggregate_heuristics(face_bgr):
    try:
        return float(np.mean([_frequency_artifact_score(face_bgr),
                              _illumination_consistency(face_bgr),
                              _edge_density(face_bgr)]))
    except Exception as e:
        logger.warning(f"Heuristic error: {e}")
        return 0.0


# ---------------- face extraction -------------
def _detect_face_boxes(img_bgr):
    h,w = img_bgr.shape[:2]
    boxes = []
    if USE_RETINA:
        try:
            dets = RetinaFace.detect_faces(img_bgr, align=False)
            if isinstance(dets, dict):
                for k,v in dets.items():
                    bb = v.get("facial_area") or v.get("bbox")
                    if bb:
                        x1,y1,x2,y2 = bb
                        boxes.append([max(0,int(x1)), max(0,int(y1)), min(w,int(x2)), min(h,int(y2))])
            elif isinstance(dets, list):
                for d in dets:
                    if len(d) >= 4:
                        x1,y1,x2,y2 = d[:4]
                        boxes.append([max(0,int(x1)), max(0,int(y1)), min(w,int(x2)), min(h,int(y2))])
        except Exception as e:
            logger.debug(f"RetinaFace detection error (image): {e}")
    elif 'mtcnn' in globals() and mtcnn is not None:
        try:
            boxes_mt, _ = mtcnn.detect(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))
            if boxes_mt is not None:
                for b in boxes_mt:
                    x1,y1,x2,y2 = [int(max(0,val)) for val in b]
                    boxes.append([x1,y1,x2,y2])
        except Exception as e:
            logger.debug(f"MTCNN detection error (image): {e}")
    cleaned = []
    for x1,y1,x2,y2 in boxes:
        if x2-x1 < 12 or y2-y1 < 12: continue
        if x1<0 or y1<0 or x2<=x1 or y2<=y1: continue
        cleaned.append([x1,y1,x2,y2])
    return cleaned


def _extract_face_region(img_bgr):
    boxes = _detect_face_boxes(img_bgr)
    if not boxes:
        return None
    boxes = sorted(boxes, key=lambda b: (b[2]-b[0])*(b[3]-b[1]), reverse=True)
    x1,y1,x2,y2 = boxes[0]
    h,w = img_bgr.shape[:2]
    x1,y1,x2,y2 = max(0,x1), max(0,y1), min(w,x2), min(h,y2)
    face = img_bgr[y1:y2, x1:x2]
    if face is None or face.size == 0: return None
    face = cv2.resize(face, (224,224), interpolation=cv2.INTER_AREA)
    return face


# ---------------- batched inference helper -------------
def _batched_model_predict(pil_images):
    if len(models) == 0:
        return [0.0] * len(pil_images)
    per_model_outputs = []
    for model, proc in zip(models, processors):
        try:
            inputs = proc(images=pil_images, return_tensors="pt", padding=True).to(device)
            with torch.no_grad():
                if device.type == "cuda":
                    with torch.cuda.amp.autocast():
                        logits = model(**inputs).logits
                else:
                    logits = model(**inputs).logits
                probs = torch.nn.functional.softmax(logits, dim=-1).cpu().numpy()
            id2label = getattr(model.config, "id2label", {}) or {}
            out_scores = []
            for p in probs:
                idx = int(np.argmax(p))
                label = str(id2label.get(str(idx), id2label.get(idx, "unknown"))).lower()
                is_fake = any(k in label for k in ["fake","manipulated","forged","edited"])
                conf = float(p[idx])
                out_scores.append(conf if is_fake else 1.0 - conf)
            per_model_outputs.append(out_scores)
        except Exception as e:
            logger.warning(f"Model batch predict failed (image): {e}")
            per_model_outputs.append([0.0]*len(pil_images))

    all_scores = np.array(per_model_outputs)
    base_weights = np.array([0.4, 0.35, 0.25])[:all_scores.shape[0]]
    if base_weights.sum() == 0:
        base_weights = np.ones(all_scores.shape[0]) / all_scores.shape[0]
    else:
        base_weights = base_weights / base_weights.sum()
    weighted = np.dot(base_weights, all_scores)
    return weighted.tolist()


# ---------------- public API ----------------
def predict_image(image_path):
    try:
        img_bgr = cv2.imread(image_path)
        if img_bgr is None:
            return {"error": "cannot_read_image"}
        face = _extract_face_region(img_bgr)
        if face is None:
            # fallback: whole image attempted
            try:
                face = cv2.resize(img_bgr, (224,224), interpolation=cv2.INTER_AREA)
            except Exception:
                return {"error": "no_face_detected"}

        pil = Image.fromarray(cv2.cvtColor(face, cv2.COLOR_BGR2RGB))
        model_scores = _batched_model_predict([pil])
        model_score = float(model_scores[0])
        heuristic_score = aggregate_heuristics(face)
        final = float(np.clip(0.85 * model_score + 0.15 * heuristic_score, 0, 1))
        label = "fake" if final > 0.55 else "real"
        return {
            "top": {"label": label, "score": round(final, 4)},
            "model_score": round(model_score, 4),
            "heuristic_score": round(heuristic_score, 4),
            "source": "image"
        }
    except Exception as e:
        logger.exception("predict_image failed")
        return {"error": str(e)}
