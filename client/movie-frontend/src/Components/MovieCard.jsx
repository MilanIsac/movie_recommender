import React, { useState } from "react";
import "../styles/card.css";

const MovieCard = ({ movie }) => {
    const [loaded, setLoaded] = useState(false);

    const poster = movie.poster_path && movie.poster_path.trim() !== ""
        ? movie.poster_path
        : "https://placehold.co/300x450?text=No+Image";
    const genres = movie.genres?.map(g => g.name || g).join(", ") || "Unknown";

    return (
        <div className="movie-card">

            {/* Poster */}
            <img
                src={poster}
                alt={movie.title}
                className={`movie-poster ${loaded ? "lazy-loaded" : ""}`}
                loading="lazy"
                onLoad={() => setLoaded(true)}
                onError={(e) => {
                    e.target.src = "https://placehold.co/300x450?text=No+Image";
                    setLoaded(true);
                }}
            />

            {/* Overlay Content (hidden until hover) */}
            <div className="movie-overlay">
                <h3>{movie.title}</h3>

                <p className="genres">
                    <strong>Genres:</strong> {genres}
                </p>

                <p className="overview">
                    <strong>Overview:</strong> &nbsp;
                    <i>{movie.overview || "No overview available."}</i>
                </p>
            </div>

        </div>
    );
};

export default MovieCard;
