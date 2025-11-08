// // server.js
// const express = require("express");
// const multer = require("multer");
// const axios = require("axios");
// const FormData = require("form-data");
// const cors = require("cors");
// const fs = require("fs");
// const path = require("path");

// const app = express();
// app.use(cors());

// const UPLOAD_DIR = path.join(__dirname, "uploads");
// if (!fs.existsSync(UPLOAD_DIR)) fs.mkdirSync(UPLOAD_DIR);
// const upload = multer({ dest: UPLOAD_DIR });

// const PY_SERVER = "http://localhost:8000";

// async function sendToPython(endpoint, filePath) {
//   const form = new FormData();
//   form.append("file", fs.createReadStream(filePath));
//   const headers = form.getHeaders();
//   const res = await axios.post(`${PY_SERVER}${endpoint}`, form, {
//     headers,
//     timeout: 120000,
//   });
//   return res.data;
// }

// app.post("/api/predict-image", upload.single("file"), async (req, res) => {
//   const fpath = req.file.path;
//   try {
//     const data = await sendToPython("/predict/image", fpath);
//     res.json(data);
//   } catch (e) {
//     console.error(e.message || e);
//     res.status(500).json({ error: "Python error", detail: e.message || e });
//   } finally {
//     try {
//       fs.unlinkSync(fpath);
//     } catch {}
//   }
// });

// app.post("/api/predict-video", upload.single("file"), async (req, res) => {
//   const fpath = req.file.path;
//   try {
//     const data = await sendToPython("/predict/video", fpath);
//     res.json(data);
//   } catch (e) {
//     console.error(e.message || e);
//     res.status(500).json({ error: "Python error", detail: e.message || e });
//   } finally {
//     try {
//       fs.unlinkSync(fpath);
//     } catch {}
//   }
// });

// const PORT = 5000;
// app.listen(PORT, () => console.log(`Node server running on port ${PORT}`));



////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// backend/server.js
const express = require("express");
const multer = require("multer");
const axios = require("axios");
const FormData = require("form-data");
const cors = require("cors");
const fs = require("fs");
const path = require("path");

const app = express();
app.use(cors());
   

const UPLOAD_DIR = path.join(__dirname, "uploads");
if (!fs.existsSync(UPLOAD_DIR)) fs.mkdirSync(UPLOAD_DIR);
const upload = multer({ dest: UPLOAD_DIR });

const PY_SERVER = "http://localhost:8000";

async function sendToPython(endpoint, filePath) {
  const form = new FormData();
  form.append("file", fs.createReadStream(filePath));
  const headers = form.getHeaders();
  const res = await axios.post(`${PY_SERVER}${endpoint}`, form, { headers });
  return res.data;
}

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

const PORT = 5000;
app.listen(PORT, () => console.log(`Node server running on port ${PORT}`));
