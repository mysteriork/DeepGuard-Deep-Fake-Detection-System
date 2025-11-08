import React from "react";
import "./home.css";
import HomeImg from "./images/jon_snow_one.jpg";
import HomeImg2 from "./images/jhon_Cena.jpg";
import { useNavigate } from "react-router-dom";

function Home() {
  const Navigate = useNavigate();
  return (
    <>
      <div className="home-container">
        <nav className="navbar1">
          <a href="/" className="imgsection">
            <label
              className="imgseclabel"
              style={{
                color: "white",
                fontSize: "x-large",
                fontWeight: "600",
                fontFamily: "calibri",
              }}
            >
              DeepGuard
            </label>
          </a>
          <section className="nav-section">
            <button className="btn1" onClick={() => Navigate("/detector")}>
              DeepGuardDetection
            </button>
            <button className="btn">AboutUs</button>
            <button className="btn">Contact</button>
          </section>
        </nav>
        <section className="hero homeContainer flex">
          <div className="text1 ">
            <h1 id="textmain">Welcome to DeepGuard</h1>
            <h2 className="subHead" style={{ color: "rgb(200, 32, 119)" }}>
              "Validate Reality, Defeat Deepfakes"
            </h2>
            <p id="textmain2">
              DeepGuard is an advanced, ensemble-driven deepfake forensics
              platform. Upload, Analyze, and Receive high-certainty,
              probabilistic outputs to instantly validate media integrity in an
              era of proliferating synthetic content.
            </p>
          </div>
          <div className="heroimg flex">
            <div className="shadow">
              <div className="box1">Real</div>
              <div className="box2">Fake</div>
            </div>
            <img src={HomeImg} alt="/" className="heroimg1" />
            <img src={HomeImg2} alt="/" className="heroimg1" />
          </div>
        </section>
        <section className="hero1 homeContainer flex">
          <button className="mainButton" onClick={() => Navigate("/detector")}>
            Use Detector
          </button>
        </section>
        <main className="main ">
          <div className="div1 flex">
            <p className="subhead2">
              What is a <strong>Deepfake ?</strong>
            </p>
            <p className="story1">
              <strong>"Deepfake"</strong> is a portmanteau of "deep learning"
              and "fake." It refers to synthetic media (images, videos, or
              audio) that have been created by Artificial Intelligence,
              primarily using algorithms like{" "}
              <strong
                style={{
                  color: "rgb(200, 32, 119)",
                  textDecoration: "underline",
                }}
              >
                Generative Adversarial Networks (GANs)
              </strong>{" "}
              .These fakes are highly realistic, making them a potent threat
              across information security and public trust.
            </p>
          </div>
        </main>

        <footer className="footer1 flex">
          <div className="footer2 flex">
            <big>DeepGuard</big>
            <article className="article1 flex">
              <h2>Everything you can imagine is real</h2>
              <p className="footp">
                "We are committed to ethical AI deployment. All uploaded files
                are processed temporarily and immediately deleted post-analysis,
                ensuring complete user privacy and consent."
              </p>
              <h5
                style={{
                  fontWeight: "600",
                  fontFamily: "sans-serif",
                  color: "white",
                  fontSize: "smaller",
                }}
              >
                2026 © DEEPGUARD : All Rights are Reserved{" "}
              </h5>
            </article>
            <article className="article2 flex">
              <ul>
                <li>contact</li>
                <li>help</li>
                <li>support</li>
                <li>email</li>
              </ul>
            </article>
          </div>
        </footer>
      </div>
    </>
  );
}

export default Home;
