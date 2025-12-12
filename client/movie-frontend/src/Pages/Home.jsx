import React, { useEffect, useState } from 'react'
import '../styles/home.css'
import MovieCard from '../Components/MovieCard';

const Home = () => {

    const [movie, setMovie] = useState([]);
    const [input, setInput] = useState('');
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(false);
    const [searched, setSearched] = useState(false);
    const [bgImage, setBgImage] = useState("");

    useEffect(() => {
        const bgImages = [
            '/images/pic1.png',
        ];

        const idx = Math.floor(Math.random() * bgImages.length);
        setBgImage(bgImages[idx]);
    }, []);


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
        if (movie.length === 0) {
            alert("Please add at least one movie!");
            return;
        }

        setLoading(true);
        setSearched(true);

        await new Promise(res => setTimeout(res, 300));

        try {
            const res = await fetch(`${BASE_URL}/api/recommend`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ movies: movie })
            });
            if (!res.ok) {
                const errData = await res.text();
                console.error("Backend error:", errData);
                throw new Error("Server returned an error");
            }
            const data = await res.json();
            setResults(data.recommendations);
        }
        catch (error) {
            console.error("Error fetching recommendations:", error);
        }
        finally {
            setLoading(false);
        }
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

                {loading ? (
                    <div className="loading">
                        <div className="spinner"></div>
                        <p>Fetching recommendations...</p>
                    </div>
                ) : !searched ? (
                    <div className="img">
                        {bgImage ? (
                            <img src={bgImage} alt="Pic" loading="lazy" />
                        ) : null}
                    </div>
                ) : results.length === 0 ? (
                    <div className="no-results">
                        <p>No recommendations found for your selection.</p>
                    </div>
                ) : (
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