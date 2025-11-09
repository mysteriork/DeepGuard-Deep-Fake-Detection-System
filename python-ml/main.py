

#***********************************************************************************************************************************************


from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import uvicorn, tempfile, cv2, numpy as np, logging
from model_helper import ensemble_predict_from_path  
from image_model_core import predict_image            

# ------------------------------
# ⚙️ App Setup
# ------------------------------
app = FastAPI(title="Deepfake Detection API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------
# 🪵 Logging
# ------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# ------------------------------
# 🧩 Heuristic functions (for videos)
# ------------------------------
def compute_fft_artifact_score(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    f = np.fft.fft2(gray)
    fshift = np.fft.fftshift(f)
    magnitude = 20 * np.log(np.abs(fshift) + 1)
    high_freq = np.mean(magnitude[-20:, -20:])
    return float(min(high_freq / 255.0, 1.0))

def color_inconsistency_score(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    h_std = np.std(hsv[:, :, 0])
    return float(min(h_std / 90.0, 1.0))

def edge_warp_score(frame):
    edges = cv2.Canny(frame, 100, 200)
    return float(min(np.mean(edges) / 255.0, 1.0))

def aggregate_heuristics(frame):
    fft_score = compute_fft_artifact_score(frame)
    color_score = color_inconsistency_score(frame)
    warp_score = edge_warp_score(frame)
    return float(np.mean([fft_score, color_score, warp_score]))

# ------------------------------
# 🎥 Video Analysis Endpoint
# ------------------------------
@app.post("/analyze")
async def analyze_video(file: UploadFile = File(...)):
    logger.info(f"🎞️ Received video file: {file.filename}")

    # Save uploaded video temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        tmp.write(await file.read())
        video_path = tmp.name

    cap = cv2.VideoCapture(video_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if frame_count == 0:
        return {"error": "Unable to read video"}

    sample_frames = max(1, frame_count // 10)
    model_scores, heuristic_scores = [], []

    for i in range(0, frame_count, sample_frames):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ret, frame = cap.read()
        if not ret:
            continue

        # --- Heuristic ---
        h_score = aggregate_heuristics(frame)
        heuristic_scores.append(h_score)

        # --- Model ensemble prediction ---
        temp_img_path = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False).name
        cv2.imwrite(temp_img_path, frame)
        preds = ensemble_predict_from_path(temp_img_path)
        fake_score = preds["top"]["label"].lower() == "fake"
        model_scores.append(float(preds["top"]["score"] if fake_score else 1 - preds["top"]["score"]))

    cap.release()

    final_model_score = float(np.mean(model_scores) if model_scores else 0.0)
    final_heuristic_score = float(np.mean(heuristic_scores) if heuristic_scores else 0.0)
    final_score = 0.7 * final_model_score + 0.3 * final_heuristic_score
    is_fake = bool(final_score > 0.5)

    logger.info(f"✅ Video analyzed: score={final_score:.4f}, fake={is_fake}")

    return {
        "source": "video",
        "model_score": round(final_model_score, 4),
        "heuristic_score": round(final_heuristic_score, 4),
        "final_score": round(final_score, 4),
        "is_deepfake": is_fake
    }

# ------------------------------
# 🖼️ Image Analysis Endpoint
# ------------------------------
@app.post("/predict/image")
async def analyze_image(file: UploadFile = File(...)):
    logger.info(f"🖼️ Received image file: {file.filename}")
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            tmp.write(await file.read())
            image_path = tmp.name

        # 🔍 Run prediction
        preds = predict_image(image_path)
        if "error" in preds:
            return {"error": preds["error"]}

        model_score = preds.get("model_score", 0.0)
        heuristic_score = preds.get("heuristic_score", 0.0)
        final_score = preds["top"]["score"]
        is_fake = preds["top"]["label"].lower() == "fake"

        logger.info(f"✅ Image analyzed: score={final_score:.4f}, fake={is_fake}")

        return {
            "source": "image",
            "model_score": round(model_score, 4),
            "heuristic_score": round(heuristic_score, 4),
            "final_score": round(final_score, 4),
            "is_deepfake": is_fake
        }

    except Exception as e:
        logger.exception("❌ Error during image analysis")
        return {"error": str(e)}

# ------------------------------
# 🚀 Run Server
# ------------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

