import React, { useState } from 'react'
import '../styles/home.css'

const Home = () => {

    const [movie, setMovie] = useState([]);
    const [input, setInput] = useState('');

    const addMovie = () => {
        if (input === '') return;
        setMovie([...movie, input]);
        setInput('');
    }

    const removeMovie = (index) => {
        setMovie(movie.filter((_, i) => i !== index));
    }

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

                {/* Submit btn */}
            </div>
            <div className='container'>
                <button className='surprise-btn'>Surprise Me</button>

                {/* Background image */}
                <div className='img'>
                    <img src="/pic1.png" alt="Pic" />
                </div>

            </div>
        </>
    )
}

export default Home
