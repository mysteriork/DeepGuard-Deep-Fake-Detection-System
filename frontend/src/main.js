

/////////////////////////////////////////////////////////////////////////////////////////////// TOASTIFY USED /////////////////////////////////////////////////

import React, { useState, useEffect } from "react";
import "./main.css";
import { useNavigate } from "react-router-dom";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

function Main() {
  const [mode, setMode] = useState("image");
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState(null);
  const [key, setKey] = useState(0);

  const navigate = useNavigate();

  useEffect(() => {
    let shown = false;
    if (!shown) {
      shown = true;
      setTimeout(() => {
        toast.info(
          `⚡ This ' PRODUCT ' is new and sometimes it goes DOWN on Services .
          NO WORRIES!... Our Team is working on it. If your Upload Fails, Please " TRY AGAIN " !!! Thank you 👍`,
          {
            position: "top-center",
            autoClose: 10000,
            closeOnClick: true,
            pauseOnHover: true,
            draggable: true,
            style: {
              background: "darkblue",
              color: "white",
              width:"400px"
            },
          }
        );
      }, 3000);
    }
  }, []);

  useEffect(() => {
    if (!file) {
      setPreview(null);
      return;
    }

    const objectUrl = URL.createObjectURL(file);
    setPreview(objectUrl);

    return () => {
      URL.revokeObjectURL(objectUrl);
    };
  }, [file]);

  const handleModeChange = (newMode) => {
    setMode(newMode);
    setFile(null);
    setPreview(null);
    setResult(null);
    setKey((k) => k + 1);
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setPreview(null);
      setResult(null);
      setFile(selectedFile);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      toast.warning("Choose a file first", {
        position: "top-center",
        autoClose: 4000,
        style: {
          background: "linear-gradient(90deg,#f7971e,#ffd200)",
          color: "#1e2a38",
        },
      });
      return;
    }

    setLoading(true);
    setResult(null);
    setProgress(0);

    const form = new FormData();
    form.append("file", file);

    const endpoint = mode === "image" ? "/api/image" : "/api/video";

    try {
      const xhr = new XMLHttpRequest();
      xhr.open("POST", `http://localhost:5000${endpoint}`, true);

      // const Url= process.env.REACT_APP_API_BASE
      // const xhr = new XMLHttpRequest();
      // xhr.open("POST", `${Url}${endpoint}`, true);

      xhr.upload.onprogress = (e) => {
        if (e.lengthComputable) {
          const percentComplete = Math.round((e.loaded / e.total) * 50);
          setProgress(percentComplete);
        }
      };

      xhr.onload = async () => {
        if (xhr.status === 200) {
          const data = JSON.parse(xhr.responseText);
          setProgress(100);
          setTimeout(() => {
            setResult(data);
            console.log(data);
            setLoading(false);
            setProgress(0);
          }, 500);
        } else {
          toast.error("Error during detection", {
            position: "top-center",
            autoClose: 6000,
            style: {
              background: "linear-gradient(90deg,#ff5858,#f09819)",
              color: "white",
            },
          });
          setLoading(false);
        }
      };

      xhr.onerror = () => {
        toast.error(`SORRY Upload Failed... Please Try Again !`, {
          position: "top-center",
          autoClose: 6000,
          style: {
            background: "linear-gradient(90deg,#ff5858,#f09819)",
            color: "white",
          },
        });
        setLoading(false);
      };

      xhr.send(form);
    } catch (err) {
      toast.error("Error: " + err.message, {
        position: "top-center",
        autoClose: 6000,
        style: {
          background: "linear-gradient(90deg,#ff5858,#f09819)",
          color: "white",
        },
      });
      setLoading(false);
    }
  };

  // const pretty = (o) => (o ? JSON.stringify(o, null, 2) : "No result yet!");

  return (
    <div className="deepfake-container">
      <nav className="navbar1 flex">
        <a href="/" className="imagesection">
          <label className="imgseclabel">DeepGuard</label>
        </a>
        <section className="nav-section">
          <button className="btn1" onClick={() => navigate("/detector")}>
            DeepGuardDetection
          </button>
          <button className="btn" onClick={() => navigate("/")}>
            AboutUs
          </button>
          <button className="btn">Contact</button>
        </section>
      </nav>

      <div id="Container" style={{ padding: 20 }}>
        <h1>Deep-Guard Scanner</h1>

        <div className="radio-group">
          <h3>Select the Media type :</h3>
          <section className="radio-section">
            <label>
              <input
                type="radio"
                checked={mode === "image"}
                onChange={() => handleModeChange("image")}
              />{" "}
              Image
            </label>
            <label style={{ marginLeft: 10 }}>
              <input
                type="radio"
                checked={mode === "video"}
                onChange={() => handleModeChange("video")}
              />{" "}
              Video
            </label>
          </section>
        </div>

        <form id="formSection" onSubmit={handleSubmit} key={key}>
          <input
            type="file"
            accept={mode === "image" ? "image/*" : "video/*"}
            onChange={handleFileChange}
          />
          <button type="submit" disabled={loading} style={{ marginLeft: 10 }}>
            {loading ? "Checking..." : "Upload & Check"}
          </button>
        </form>
        {/* Toast container for displaying notifications */}
        <ToastContainer />
        {preview && mode === "image" && (
          <div className="pre-section" style={{ marginTop: 20 }}>
            <h3 style={{ fontFamily: "cursive" }}>Image Preview:</h3>
            <img
              src={preview}
              alt="preview"
              style={{ maxWidth: "100%", maxHeight: 400 }}
            />
          </div>
        )}

        {preview && mode === "video" && (
          <div className="pre-video" style={{ marginTop: 20 }}>
            <h3>Video Preview:</h3>
            <video
              key={preview}
              controls
              style={{ maxWidth: "100%", maxHeight: 400 }}
            >
              <source src={preview} type={file?.type} />
              Your browser does not support the video tag.
            </video>
          </div>
        )}

        {result && result.source === "video" && (
          <div className="result-section modern-result">
            <h3>Detailed Analysis Report</h3>

            <div className="score-cards">
              <div className="score-card">
                <div
                  className="progress-circle"
                  data-score={result.model_score * 100}
                >
                  <svg>
                    <circle cx="60" cy="60" r="54"></circle>
                    <circle
                      cx="60"
                      cy="60"
                      r="54"
                      style={{
                        strokeDashoffset:
                          339 - (339 * (result.model_score * 100)) / 100,
                      }}
                    ></circle>
                  </svg>
                  <div className="score-value">
                    {(result.model_score * 100).toFixed(1)}%
                  </div>
                </div>
                <p>Model Score</p>
              </div>

              <div className="score-card">
                <div
                  className="progress-circle"
                  data-score={result.heuristic_score * 100}
                >
                  <svg>
                    <circle cx="60" cy="60" r="54"></circle>
                    <circle
                      cx="60"
                      cy="60"
                      r="54"
                      style={{
                        strokeDashoffset:
                          339 - (339 * (result.heuristic_score * 100)) / 100,
                      }}
                    ></circle>
                  </svg>
                  <div className="score-value">
                    {(result.heuristic_score * 100).toFixed(1)}%
                  </div>
                </div>
                <p>Heuristic Score</p>
              </div>

              <div className="score-card">
                <div
                  className="progress-circle"
                  data-score={result.final_score * 100}
                >
                  <svg>
                    <circle cx="60" cy="60" r="54"></circle>
                    <circle
                      cx="60"
                      cy="60"
                      r="54"
                      style={{
                        strokeDashoffset:
                          339 - (339 * (result.final_score * 100)) / 100,
                      }}
                    ></circle>
                  </svg>
                  <div className="score-value">
                    {(result.final_score * 100).toFixed(1)}%
                  </div>
                </div>
                <p>Final Score</p>
              </div>
            </div>

            <div
              className={`verdict-banner ${
                result.is_deepfake ? "fake" : "real"
              }`}
            >
              {result.is_deepfake
                ? "⚠️ Deepfake Detected"
                : "✅ Authentic Media"}
            </div>
          </div>
        )}

        {result && result.source === "image" && (
          <div className="result-section modern-result">
            <h3>Image Analysis Result</h3>
            <div className="score-cards single">
              <div className="score-card">
                <div
                  className="progress-circle"
                  data-score={result.final_score * 100}
                >
                  <svg>
                    <circle cx="60" cy="60" r="54"></circle>
                    <circle
                      cx="60"
                      cy="60"
                      r="54"
                      style={{
                        strokeDashoffset:
                          339 - (339 * (result.final_score * 100)) / 100,
                      }}
                    ></circle>
                  </svg>
                  <div className="score-value">
                    {(result.final_score * 100).toFixed(1)}%
                  </div>
                </div>
                <p>Final Confidence</p>
              </div>
            </div>

            <div
              className={`verdict-banner ${
                result.is_deepfake ? "fake" : "real"
              }`}
            >
              {result.is_deepfake
                ? "⚠️ Deepfake Detected"
                : "✅ Authentic Image"}
            </div>
          </div>
        )}
      </div>

      {/* --- LOADER OVERLAY --- */}
      {loading && (
        <div className="loader-overlay">
          <div className="loader-container">
            <div className="glow-spinner"></div>
            <div className="progress-bar-container">
              <div
                className="progress-bar-fill"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
            <p className="loading-text">
              Analyzing {mode}... ({progress}%)
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

export default Main;
