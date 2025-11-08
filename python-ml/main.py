

# #######################################################################################################

# from fastapi import FastAPI, UploadFile, File
# from fastapi.middleware.cors import CORSMiddleware
# import shutil, os, uuid, uvicorn, time, logging, asyncio
# from rich.console import Console
# from rich.panel import Panel
# from rich.progress import Progress, SpinnerColumn, BarColumn, TimeElapsedColumn
# from rich.logging import RichHandler
# import torch

# # === Import detection cores ===
# from model_helper import ensemble_predict_from_path
# from image_model_core import predict_image

# # === Initialize console + logger ===
# console = Console()
# logging.basicConfig(level=logging.INFO, format="%(message)s", handlers=[RichHandler()])
# logger = logging.getLogger("DeepGuard")

# # === Device detection ===
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# console.rule("[bold cyan]🚀 DeepGuard ML Server Initialization")
# console.print(Panel.fit(
#     f"[green]Backend running with [bold]{device}[/bold] acceleration.",
#     title="[yellow]System Startup"
# ))

# # === FastAPI setup ===
# app = FastAPI(title="DeepGuard ML Server")
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# UPLOAD_DIR = "uploads"
# os.makedirs(UPLOAD_DIR, exist_ok=True)

# # Utility to safely write upload file
# def save_upload(file: UploadFile, prefix: str):
#     path = os.path.join(UPLOAD_DIR, f"{prefix}_{uuid.uuid4().hex}_{file.filename}")
#     with open(path, "wb") as f:
#         shutil.copyfileobj(file.file, f)
#     return path

# # === API: Image Detection ===
# @app.post("/predict/image")
# async def predict_image_api(file: UploadFile = File(...)):
#     start = time.time()
#     path = save_upload(file, "img")
#     console.print("[cyan]🔍 Running deepfake image detection...[/cyan]")
#     with Progress(SpinnerColumn(), BarColumn(), TimeElapsedColumn(), transient=True) as prog:
#         task = prog.add_task("[yellow]Analyzing image...", total=None)
#         res = await asyncio.to_thread(predict_image, path)
#         prog.update(task, completed=100)
#     os.remove(path)
#     console.print(f"[green]✅ Image analysis completed in {time.time() - start:.2f}s[/green]")
#     return {"status": "success", "time_taken": round(time.time() - start, 2), **res}

# # === API: Video Detection ===
# @app.post("/predict/video")
# async def predict_video_api(file: UploadFile = File(...)):
#     start = time.time()
#     path = save_upload(file, "vid")
#     console.rule("[bold blue]🎬 Deepfake Video Analysis Started")

#     with Progress(SpinnerColumn(), BarColumn(), TimeElapsedColumn(), transient=True) as prog:
#         task = prog.add_task("[cyan]Processing video frames...", total=None)
#         # Run heavy model in thread to prevent async blocking
#         res = await asyncio.to_thread(ensemble_predict_from_path, path)
#         prog.update(task, completed=100)

#     os.remove(path)
#     console.print(f"[green]✅ Video analysis completed in {time.time() - start:.2f}s[/green]")

#     # Handle potential timeouts in frontend — return immediately if result valid
#     if not res:
#         return {"status": "error", "message": "Detection failed or timeout"}
#     return {"status": "success", "time_taken": round(time.time() - start, 2), **res}

# # === Main Entrypoint ===
# if __name__ == "__main__":
#     console.rule("[bold yellow]⚡ Launching FastAPI Server")
#     uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")


###########################################################################################################################################################################################################################################################################################33333333333


# from fastapi import FastAPI, UploadFile, File
# from fastapi.middleware.cors import CORSMiddleware
# import uvicorn, tempfile, cv2, numpy as np, torch
# from PIL import Image
# import torch.nn.functional as F
# from model_helper import ensemble_predict_from_path  # ✅ import your ensemble helper

# from image_model_core import predict_image

# app = FastAPI()

# # ✅ Enable CORS for frontend
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"], 
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ------------------------------
# # 🧩 Heuristic functions
# # ------------------------------
# def compute_fft_artifact_score(frame):
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     f = np.fft.fft2(gray)
#     fshift = np.fft.fftshift(f)
#     magnitude = 20 * np.log(np.abs(fshift) + 1)
#     high_freq = np.mean(magnitude[-20:, -20:])
#     return float(min(high_freq / 255.0, 1.0))

# def color_inconsistency_score(frame):
#     hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
#     h_std = np.std(hsv[:, :, 0])
#     return float(min(h_std / 90.0, 1.0))

# def edge_warp_score(frame):
#     edges = cv2.Canny(frame, 100, 200)
#     return float(min(np.mean(edges) / 255.0, 1.0))

# def aggregate_heuristics(frame):
#     fft_score = compute_fft_artifact_score(frame)
#     color_score = color_inconsistency_score(frame)
#     warp_score = edge_warp_score(frame)
#     return float(np.mean([fft_score, color_score, warp_score]))

# # ------------------------------
# # 🎥 Main endpoint
# # ------------------------------
# @app.post("/analyze")
# async def analyze_video(file: UploadFile = File(...)):
#     # Save uploaded video temporarily
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
#         tmp.write(await file.read())
#         video_path = tmp.name

#     cap = cv2.VideoCapture(video_path)
#     frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
#     if frame_count == 0:
#         return {"error": "Unable to read video"}

#     sample_frames = max(1, frame_count // 10)
#     model_scores, heuristic_scores = [], []

#     for i in range(0, frame_count, sample_frames):
#         cap.set(cv2.CAP_PROP_POS_FRAMES, i)
#         ret, frame = cap.read()
#         if not ret:
#             continue

#         # --- Heuristic ---
#         h_score = aggregate_heuristics(frame)
#         heuristic_scores.append(h_score)

#         # --- Model ensemble prediction ---
#         temp_img_path = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False).name
#         cv2.imwrite(temp_img_path, frame)
#         preds = ensemble_predict_from_path(temp_img_path)
#         fake_score = preds["top"]["label"].lower() == "fake"
#         model_scores.append(float(preds["top"]["score"] if fake_score else 1 - preds["top"]["score"]))

#     cap.release()

#     final_model_score = float(np.mean(model_scores) if model_scores else 0.0)
#     final_heuristic_score = float(np.mean(heuristic_scores) if heuristic_scores else 0.0)
#     final_score = 0.7 * final_model_score + 0.3 * final_heuristic_score

#     return {
#         "model_score": round(final_model_score, 4),
#         "heuristic_score": round(final_heuristic_score, 4),
#         "final_score": round(final_score, 4),
#         "is_deepfake": bool(final_score > 0.5)  # Convert NumPy bool to Python bool
#     }

# # ------------------------------
# # 🚀 Run
# # ------------------------------
# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)


#***********************************************************************************************************************************************


from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import uvicorn, tempfile, cv2, numpy as np, logging
from model_helper import ensemble_predict_from_path  # ✅ video helper
from image_model_core import predict_image            # ✅ image helper

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

