const mongoose = require("mongoose");

const movieSchema = new mongoose.Schema({
    id: Number,
    title: String,
    genres: [String],
    release_date: String,
    vote_avg: String,
});

module.exports = mongoose.model("Movie", movieSchema);