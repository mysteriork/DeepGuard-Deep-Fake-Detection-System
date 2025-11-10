# -----------------------------
# 🧠 DeepGuard - Python ML Backend (Optimized for Hugging Face)
# -----------------------------
FROM python:3.10-slim

# Prevent interactive prompts during install
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies for OpenCV, ffmpeg, and git
RUN apt-get update && apt-get install -y \
    ffmpeg libsm6 libxext6 libglib2.0-0 git && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependency files first for better caching
COPY requirements.txt .

# Upgrade pip and install dependencies efficiently
RUN pip install --upgrade pip && \
    pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# Copy rest of the application
COPY . .

# Expose default Hugging Face port
EXPOSE 7860

# Run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
