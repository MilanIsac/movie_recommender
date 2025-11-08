const express = require("express");
const axios = require("axios");
const movies = require("../models/movieModels");

const router = express.Router();

const FASTAPI_URL = process.env.FASTAPI_URL;

router.get("/", async (req, res) => {
  try {
    const allMovies = await movies.find();
    res.json(allMovies);
  } catch (error) {
    res.status(500).json({ error: "Database Error" });
  }
});

router.get("/recommend/:name", async (req, res) => {
  try {
    const { name } = req.params;
    const response = await axios.get(`${FASTAPI_URL}/recommend/${encodeURIComponent(name)}`);
    res.json(response.data);
  } catch (error) {
    console.error("Error fetching recommendations:", error.message);
    res.status(500).json({ error: "FastAPI recommendation failed" });
  }
});

router.post("/refresh", async (req, res) => {
  try {
    const response = await axios.post(`${FASTAPI_URL}/refresh`);
    res.json(response.data);
  } catch (err) {
    console.error("Error calling FastAPI refresh:", err.message);
    res.status(500).json({ error: "FastAPI refresh failed" });
  }
});

router.post("/run-training", async (req, res) => {
  try {
    const response = await axios.post(`${FASTAPI_URL}/run-training`);
    res.json(response.data);
  } catch (err) {
    console.error("Error calling FastAPI training:", err.message);
    res.status(500).json({ error: "FastAPI training failed" });
  }
});

module.exports = router;
