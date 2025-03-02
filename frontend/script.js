console.log("abcd")

async function getRecommendations() {
    const movie_name = document.getElementById("movie_name").value;  
    // Corrected variable name
    if (!movie_name) {
        alert("Please enter a movie name");
        return;
    }

    try {
        const response = await fetch(`http://localhost:8001/recommend/${encodeURIComponent(movie_name)}`);
        // console.log(`Fetching recommendations from: http://localhost:8001/recommend/${encodeURIComponent(movie_name)}`);
        const data = await response.json();
        console.log(data);
        displayResults(data.recommendations);
    } catch (error) {
        console.log("Error fetching the recommendations: ", error);
        alert("Failed to fetch recommendations", error);
    }
}

function displayResults(movies) {
    const resultsDiv = document.getElementById("results");
    resultsDiv.innerHTML = "";

    if (movies.length === 0) {
        resultsDiv.innerHTML = "No recommendations found";
        return;
    }

    movies.forEach(movie => {
        const movieElement = document.createElement("div");
        
        // Split genres by '|' and join them with ', '
        const genreNames = movie.genres.split('|').join(", ");
        
        movieElement.innerHTML = `
            <h3>${movie.title}</h3>
            <p><strong>Genres:</strong> ${genreNames}</p>
            <p><strong>Tagline:</strong> ${movie.tagline}</p>
            <hr>`;
        resultsDiv.appendChild(movieElement);
    });
}


// uvicorn recommendation.model:app --host 0.0.0.0 --port 8001 --reload
