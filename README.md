# DeepGuard : DEEP-FAKE DETECTION SYSTEM  

### 🎯 Overview  
**DeepGuard** is a production-grade **Deepfake Detection System** that leverages **AI + Deep Learning** to identify manipulated or synthetic content in both images and videos.  
It integrates a **Python-based ML engine** with a better improved ensemble core logic , a **Node.js backend**, and a **modern React frontend** — providing users with a seamless, accurate, and interactive deepfake verification experience.  

<img width="270" height="150" alt="Screenshot 2025-10-05 132956" src="https://github.com/user-attachments/assets/5a2521d9-687b-4695-aa2b-168335a10cb3" />

---

## 📂 Project Structure  

<img width="788" height="674" alt="Screenshot 2025-11-08 221557" src="https://github.com/user-attachments/assets/162c5c3b-e602-41df-ab43-39dbd49ee617" />



---

## ⚙️ Tech Stack  

### 🔹 Frontend  
- **React.js (Vite)** — Modern reactive UI framework  
- **TailwindCSS** — Minimal and responsive design system  
- **Framer Motion** — Smooth animations and transitions  
- **Axios / Fetch API** — Communication with Node.js backend  

### 🔹 Backend (Node.js)  
- **Express.js** — Lightweight API gateway and request handler  
- **Multer** — File upload management  
- **CORS & Body-parser** — Middleware for cross-origin and data parsing  
- **Integration Layer** — Connects to Python ML service for inference  

### 🔹 Machine Learning Core (Python)  
- **FastAPI** — High-performance ML microservice  
- **PyTorch / torchvision / timm** — Deep learning frameworks  
- **OpenCV + Pillow + NumPy** — Image and video frame processing  
- **FFmpeg-python** — Video decoding and frame extraction  
- **Facenet-pytorch** — Face localization and alignment  

---

# MODULE EXPLANATION :
<img width="658" height="717" alt="image" src="https://github.com/user-attachments/assets/b0b405df-aa6d-42e2-a5e0-ff6e75424825" />


## 🧩 Workflow  

1. **Frontend (React)** — User uploads image/video via clean modern UI.  
2. **Backend (Node.js)** — Handles file upload, stores it temporarily, and calls the Python service.  
3. **ML Engine (Python)** — Performs deepfake detection using pretrained CNN + temporal models.  
4. **Results Returned** — Node backend sends structured response back to frontend for visualization.  

# WORKFLOW DIAGRAM :
1- <img width="2400" height="1600" alt="blockD" src="https://github.com/user-attachments/assets/1abcd26d-2549-4a49-b6ef-f77277cbd83d" />
2- [ DFD ]
<img width="1536" height="1024" alt="DFD backend" src="https://github.com/user-attachments/assets/abc48af4-d1d7-4cab-97fe-eabe2f140482" />


## 🚀 Getting Started  

### 1️⃣ Clone the Repository

git clone https://github.com/<your-username>/DeepGuard_detection_system.git
cd DeepGuard_detection_system

2️⃣ Setup Python ML Service

cd python-ml
python -m venv venv
venv\Scripts\activate        # On Windows
pip install -r requirements.txt
python main.py

3️⃣ Setup Node.js Backend

cd ../backend-node
npm install
node server.js

4️⃣ Setup React Frontend

cd ../frontend
npm install
npm run dev

Access the app at:
👉 http://localhost:5173 For Local Only.

## 🛡️ Key Features

✅ Real-time deepfake detection for images and videos
✅ Modular 3-tier architecture (Frontend + Node API + Python ML)
✅ Fast and accurate inference using CNN and temporal models
✅ Modern and responsive UI with progress tracking and animations
✅ RESTful API integration for scalability and deployment flexibility

# ACCURACY ANALYSIS :

<img width="1980" height="1180" alt="graph_image_real" src="https://github.com/user-attachments/assets/72a707d3-b079-42c3-84c1-324448e9e773" />


### PROJECT S N A P S H O T S : 
📸 Snapshots

1. MAIN PAGE :

<img width="1920" height="2477" alt="image" src="https://github.com/user-attachments/assets/b4214c19-989c-4aca-ba23-0f498418a7f2" />

2. DETECTOR PAGE :

<img width="716" height="404" alt="image" src="https://github.com/user-attachments/assets/0d79dda8-bd3e-40fa-ad94-f234ee03c8a0" />


🧠 Future Improvements

    Will Integrate transformer-based video forgery models

    To add deepfake probability heatmaps

    To support streaming input and live camera detection

    Implementing user authentication and analysis history

🪪 License

This project is licensed under the MIT License — feel free to use and modify for research and educational purposes.
👨‍💻 Author

Rachit Kumar
B.Tech – Computer Science & Engineering (CYBER FORENSICS) 
💻 Python | C++ | MERN Stack | AI/ML Enthusiast
