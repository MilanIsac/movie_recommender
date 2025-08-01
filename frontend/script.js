async function getRecommendations() {
    const movie_name = document.getElementById("movie_name").value;
    if (!movie_name) {
        alert("Please enter a movie name");
        return;
    }

    try {
        const response = await fetch(`http://localhost:8001/recommend/${encodeURIComponent(movie_name)}`);
        const data = await response.json();
        displayResults(data.recommendations);
    } catch (error) {
        console.log("Error fetching the recommendations: ", error);
        alert("Failed to fetch recommendations", error);
    }
}

function displayResults(movies) {
    const resultsDiv = document.getElementById("results");
    resultsDiv.innerHTML = ""; // Clear previous results

    if (movies.length === 0) {
        resultsDiv.innerHTML = "<p>No recommendations found</p>";
        return;
    }

    movies.forEach(movie => {
        const movieElement = document.createElement("div");
        movieElement.classList.add("movie-card");

        const genreNames = movie.genres && Array.isArray(movie.genres)
            ? movie.genres.map(genre => genre.name).join(", ")
            : "Unknown";

        // console.log(typeof movie.genres);
        // console.log("Parsed Genres:", genreNames);

        const response = await fetch(`http://localhost:8001/recommend/${encodeURIComponent(movie_name)}`);
        const movie_title = 

        movieElement.innerHTML = `
            <h3>${movie.title}</h3>
            <p><strong>Genres:</strong> ${genreNames}</p>
            <p><strong>Tagline:</strong> ${movie.tagline}</p>
            <p><strong>Similarity Score:</strong> ${movie.similarity_score.toFixed(2)}</p>
            <p><strong>Rating:</strong> ${movie.vote_average.toFixed(1)}/10 (${movie.vote_count} votes)</p>
            <p><strong>Overview:</strong> ${movie.overview}</p>`;

        resultsDiv.appendChild(movieElement);
    });
}

document.getElementById("movie_name").addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
        getRecommendations();
    }
});
