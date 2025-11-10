// ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// // backend/server.js
// require('dotenv').config();
// const express = require("express");
// const multer = require("multer");
// const axios = require("axios");
// const FormData = require("form-data");
// const cors = require("cors");
// const fs = require("fs");
// const path = require("path");

// const app = express();
// app.use(
//   cors({
//     origin: [
//       "https://deep-fake-detection-system-6k6rkxctu-mysteriorks-projects.vercel.app/",
//       "http://localhost:3000",
//     ],
//     methods: ["GET", "POST"],
//     allowedHeaders: ["Content-Type"],
//   })
// );

// const UPLOAD_DIR = path.join(__dirname, "uploads");
// if (!fs.existsSync(UPLOAD_DIR)) fs.mkdirSync(UPLOAD_DIR);
// const upload = multer({ dest: UPLOAD_DIR });

// const PY_SERVER = process.env.SERVER || "http://localhost:8000";

// async function sendToPython(endpoint, filePath) {
//   const form = new FormData();
//   form.append("file", fs.createReadStream(filePath));
//   const headers = form.getHeaders();
//   const res = await axios.post(`${PY_SERVER}${endpoint}`, form, { headers });
//   return res.data;
// }

// app.post("/api/image", upload.single("file"), async (req, res) => {
//   const fpath = req.file.path;
//   try {
//     const data = await sendToPython("/predict/image", fpath);
//     res.json(data);
//   } catch (e) {
//     console.error(e.message);
//     res.status(500).json({ error: "Python error" });
//   } finally {
//     fs.unlinkSync(fpath);
//   }
// });

// app.post("/api/video", upload.single("file"), async (req, res) => {
//   const fpath = req.file.path;
//   try {
//     const data = await sendToPython("/analyze", fpath);
//     res.json(data);
//   } catch (e) {
//     console.error(e.message);
//     res.status(500).json({ error: "Python error" });
//   } finally {
//     fs.unlinkSync(fpath);
//   }
// });

// const PORT = process.env.PORT;
// app.listen(PORT, () => console.log(`Node server running on port ${PORT}`));

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// backend/server.js

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// backend/server.js
require("dotenv").config();
const express = require("express");
const multer = require("multer");
const axios = require("axios");
const FormData = require("form-data");
const cors = require("cors");
const fs = require("fs");
const path = require("path");

const app = express();

// ✅ Enhanced CORS setup
app.use(
  cors({
    origin: [
      "https://deep-fake-detection-system.vercel.app/",
      "https://deep-fake-detection-system.vercel.app",
       // no slash!
      "http://localhost:3000",
    ],
    methods: ["GET", "POST", "OPTIONS"],
    allowedHeaders: ["Content-Type", "Authorization"],
    credentials: true,
  })
);

// ✅ Global preflight handler (Express 5 safe)
app.use((req, res, next) => {
  res.header("Access-Control-Allow-Origin", "*");
  res.header(
    "Access-Control-Allow-Headers",
    "Origin, X-Requested-With, Content-Type, Accept, Authorization"
  );
  res.header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, DELETE");
  if (req.method === "OPTIONS") {
    return res.sendStatus(204);
  }
  next();
});

const UPLOAD_DIR = path.join(__dirname, "uploads");
if (!fs.existsSync(UPLOAD_DIR)) fs.mkdirSync(UPLOAD_DIR);
const upload = multer({ dest: UPLOAD_DIR });

// ✅ Python backend URL
const PY_SERVER = process.env.SERVER;

async function sendToPython(endpoint, filePath) {
  const form = new FormData();
  form.append("file", fs.createReadStream(filePath));
  const headers = form.getHeaders();

  const res = await axios.post(`${PY_SERVER}${endpoint}`, form, {
    headers,
    timeout: 60000,
  });
  return res.data;
}

// ------------------------------
// 🖼️ Image Endpoint
// ------------------------------
app.post("/api/image", upload.single("file"), async (req, res) => {
  const fpath = req.file.path;
  try {
    const data = await sendToPython("/predict/image", fpath);
    res.json(data);
  } catch (e) {
    console.error(e.message);
    res.status(500).json({ error: "Python error" });
  } finally {
    fs.unlinkSync(fpath);
  }
});

// ------------------------------
// 🎥 Video Endpoint
// ------------------------------
app.post("/api/video", upload.single("file"), async (req, res) => {
  const fpath = req.file.path;
  try {
    const data = await sendToPython("/analyze", fpath);
    res.json(data);
  } catch (e) {
    console.error(e.message);
    res.status(500).json({ error: "Python error" });
  } finally {
    fs.unlinkSync(fpath);
  }
});

// ------------------------------
// 🧩 Default route handler
// ------------------------------
app.use((req, res) => {
  res.status(404).json({ error: "Route not found" });
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`✅ Node server running on port ${PORT}`));
