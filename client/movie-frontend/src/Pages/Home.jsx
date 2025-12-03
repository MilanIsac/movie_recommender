import React, { useState } from 'react'
import '../styles/home.css'
import MovieCard from '../Components/MovieCard';

const Home = () => {

    const [movie, setMovie] = useState([]);
    const [input, setInput] = useState('');
    const [results, setResults] = useState([]);

    const BASE_URL = import.meta.env.VITE_BASE_URL;


    const addMovie = () => {
        if (input === '') return;
        setMovie([...movie, input]);
        setInput('');
    }

    const removeMovie = (index) => {
        setMovie(movie.filter((_, i) => i !== index));
    }

    const surpriseMe = async () => {
        if(movie.length === 0) {
            alert('Please add at least one movie.');
            return;
        }
        const lastMovie = movie[movie.length - 1];

        const res = await fetch(`${BASE_URL}/api/recommend/${lastMovie}`);
        const data = await res.json();

        setResults(data.recommendations);
    };


    return (
        <>
            <div className='body'>

                {/* Logo */}
                <div className='logo'>
                    <img src="/logo.png" alt="Website Logo" />
                </div>

                {/* Heading */}
                <div className='heading'>
                    <p>Find What Fits Your</p>
                    <span className='highlight'>Watchlist.</span>
                </div>

                {/* Search box */}
                <div className='search-box'>
                    <div className='movie-list'>
                        {movie.map((movie, index) => (
                            <div className='movie' key={index}>
                                {movie}
                                <span className='remove-btn' onClick={() => removeMovie(index)}>✖</span>
                            </div>
                        ))}

                        <input
                            type="text"
                            placeholder='Type movies you liked'
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                        />
                    </div>
                    <button className='add-btn' onClick={addMovie}>+ Add</button>
                </div>

            </div>
            <div className='container'>
                {/* Submit btn */}
                <button className='surprise-btn'
                    onClick={surpriseMe}
                >Surprise Me</button>

                {results.length === 0 ? (
                    // image when no results
                    <div className="img">
                        <img src="/pic1.png" alt="Pic" />
                    </div>
                ) : (

                    // results
                    <div className="results-grid">
                        {results.map((movie, index) => (
                            <MovieCard key={index} movie={movie} />
                        ))}
                    </div>
                )}
            </div>
        </>
    )
}

export default Home