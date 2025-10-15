async function getRecommendations() {
    const movie_name = document.getElementById("movie_name").value;
    if (!movie_name) {
        alert("Please enter a movie name");
        return;
    }

    try {
        const response = await fetch(`http://localhost:8000/api/recommend/${encodeURIComponent(movie_name)}`);

        if (!response.ok) {
            const errorData = await response.json();
            alert(errorData.detail || "Unknown error occurred");
            return;
        }
        const data = await response.json();
        displayResults(data.recommendations);
    } catch (error) {
        console.log("Error fetching the recommendations: ", error);
        alert("Failed to fetch recommendations");
    }
}

function displayResults(movies) {
    const resultsDiv = document.getElementById("results");
    resultsDiv.innerHTML = ""; // Clear previous results

    if (!movies || movies.length === 0) {
        resultsDiv.innerHTML = "<p>No recommendations found</p>";
        return;
    }

    for (const movie of movies) {
        const movieElement = document.createElement("div");
        movieElement.classList.add("movie-card");

        const genreNames = movie.genres && Array.isArray(movie.genres)
            ? movie.genres.map(genre => genre.name).join(", ")
            : "Unknown";

        movieElement.innerHTML = `
            <h3>${movie.title}</h3>
            <div style="display: flex; justify-content: center;">
                <img src="${movie.poster_full || "https://via.placehold.co/200x300?text=No+Image"}" 
                     alt="${movie.title}" style="width:200px;" />
            </div>
            <p><strong>Genres:</strong> ${genreNames}</p>
            <p><strong>Tagline:</strong> ${movie.tagline || "N/A"}</p>
            <p><strong>Rating:</strong> ${movie.vote_average ? movie.vote_average.toFixed(1) : "N/A"}/10 (${movie.vote_count || 0} votes)</p>
            <p><strong>Overview:</strong> ${movie.overview || "N/A"}</p>
        `;

        resultsDiv.appendChild(movieElement);
    }
}

document.getElementById("movie_name").addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
        getRecommendations();
    }
});
