require('dotenv').config({ path: '../.env' });
const express = require("express");
const cors = require("cors");
const connectDB = require("./config/db");
const movieRoutes = require("./routes/movieRoute");
const path = require("path");
const axios = require("axios");
const Movie = require("./models/movieModels.js");

connectDB();

const app = express();
app.use(cors({ origin: "*" }));
app.use(express.json());
app.use(express.static(path.join(__dirname, "../frontend")));

app.use("/api/movies/", movieRoutes);

// ✅ Recommendation route
app.get("/api/recommend/:title", async (req, res) => {
    try {
        const title = req.params.title;

        // Call ML service for recommendations
        const response = await axios.get(
            `${process.env.ML_SERVICE_URL}/recommend/${encodeURIComponent(title)}`
        );

        const recommended = response.data.recommendations; // array with { title, similarity_score }

        // Fetch full details from MongoDB
        const detailedMovies = await Promise.all(
            recommended.map(async (rec) => {
                const movieDoc = await Movie.findOne({ title: rec.title });
                if (!movieDoc) return null;

                return {
                    title: movieDoc.title,
                    tagline: movieDoc.tagline || "",
                    genres: movieDoc.genres || [],
                    runtime: movieDoc.runtime || 0,
                    release_date: movieDoc.release_date || "",
                    overview: movieDoc.overview || "",
                    poster_full: movieDoc.poster_full || "",
                    vote_average: movieDoc.vote_average || 0,
                    vote_count: movieDoc.vote_count || 0,
                    similarity_score: rec.similarity_score,
                };
            })
        );

        res.json({ recommendations: detailedMovies.filter(Boolean) });
    } catch (error) {
        console.error("Error fetching recommendations.", error);
        res.status(500).json({ error: "ML Service unavailable" });
    }
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
    console.log(`Server is running on PORT: ${PORT}`);
});
