import React from 'react'
import '../styles/card.css'

const MovieCard = ({movie}) => {
    return (
        <div className='movie-card'>
            <img src={movie.poster_path || 'https://placehold.co/300x450?text=No+Image'}
                alt="Movie Image"
                className='movie-poster'
            />

            <h3 className='movie-title'>{movie.title}</h3>

            <p className="movie-genres">
                <strong>Genres:</strong>{" "}
                {movie.genres?.map(g => g.name).join(", ") || "Unknown"}
            </p>

            {movie.tagline && (
                <p className="movie-tagline">“{movie.tagline}”</p>
            )}

            <p className="movie-overview">
                {movie.overview || "No overview available."}
            </p>

        </div>
    )
}

export default MovieCard
