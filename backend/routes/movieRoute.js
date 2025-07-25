const express = require("express");
const axios = require("axios");
const movies = require("../models/movieModels");

const router = express.Router();

const FASTAPI_URL = process.env.FASTAPI_URL;

// get movies from db
router.get("/", async (req, res) => {
    try {
        const movie = await movies.find();
        res.json(movie);
    } catch (error) {
        res.status(500).json({ error: "Database Error" });
    }
});
// console.log("abcde");
// get recommendations from fastapi
router.get("/recommend/:name", async (req, res) => {
    try {
        const { name } = req.params;
        const response = await axios.get(`${FASTAPI_URL}/recommend/${encodeURIComponent(name)}`);
        res.json(response.data);
    } catch (error) {
        res.status(500).json({ error: "Error fetching recommendations" });
    }
});

module.exports = router;