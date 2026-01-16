const express = require("express");
const axios = require("axios");
const movies = require("../models/movieModels");

const router = express.Router();

const FASTAPI_URL = process.env.FASTAPI_URL;

if(!FASTAPI_URL) {
  throw new Error('FASTAPI_URL is not defined in env');
}

router.get("/", async (req, res) => {
  try {
    const allMovies = await movies.find();
    res.json(allMovies);
  }
  catch (error) {
    res.status(500).json({ error: "Database Error" });
  }
});

router.post("/recommend", async (req, res) => {
  try {
    const { movies } = req.body;
    if (!movies || !Array.isArray(movies) || movies.length === 0) {
      return res.status(400).json({ error: "No movies provided" });
    }

    console.log("Forwarding to FastAPI:", FASTAPI_URL + "/recommend");
    console.log("Request body:", movies);

    const response = await axios.post(`${FASTAPI_URL}/api/recommend`, { movies }, { timeout: 20000 });

    return res.json(response.data);

  }
  catch (err) {
    console.error("Axios error message:", err.message);
    if (err.response) {
      console.error("FastAPI response status:", err.response.status);
      console.error("FastAPI response data:", err.response.data);
      return res.status(502).json({ error: "FastAPI error", detail: err.response.data });
    }
    else {
      console.error("No response from FastAPI (connection error or timeout).");
      return res.status(502).json({ error: "FastAPI unreachable", detail: err.message });
    }
  }
});



router.post("/refresh", async (req, res) => {
  try {
    const response = await axios.post(`${FASTAPI_URL}/api/refresh`);
    res.json(response.data);
  }
  catch (err) {
    console.error("Error calling FastAPI refresh:", err.message);
    res.status(500).json({ error: "FastAPI refresh failed" });
  }
});

router.post("/run-training", async (req, res) => {
  try {
    const response = await axios.post(`${FASTAPI_URL}/api/run-training`);
    res.json(response.data);
  }
  catch (err) {
    console.error("Error calling FastAPI training:", err.message);
    res.status(500).json({ error: "FastAPI training failed" });
  }
});

module.exports = router;
