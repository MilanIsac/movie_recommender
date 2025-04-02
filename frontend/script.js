// async function getRecommendations() {
//     const movie_name = document.getElementById("movie_name").value;
//     // Corrected variable name
//     if (!movie_name) {
//         alert("Please enter a movie name");
//         return;
//     }

//     try {
//         const response = await fetch(`http://localhost:8001/recommend/${encodeURIComponent(movie_name)}`);
//         // console.log(`Fetching recommendations from: http://localhost:8001/recommend/${encodeURIComponent(movie_name)}`);
//         const data = await response.json();
//         console.log(data);
//         displayResults(data.recommendations);
//     } catch (error) {
//         console.log("Error fetching the recommendations: ", error);
//         alert("Failed to fetch recommendations", error);
//     }
// }

// function displayResults(movies) {
//     const resultsDiv = document.getElementById("results");
//     resultsDiv.innerHTML = ""; // Clear previous results

//     if (movies.length === 0) {
//         resultsDiv.innerHTML = "<p>No recommendations found</p>";
//         return;
//     }

//     movies.forEach(movie => {
//         const movieElement = document.createElement("div");
//         movieElement.classList.add("movie-card"); // Apply styling

//         // let genresArray = movie.genres;

//         // if (Array.isArray(genresArray)) {
//         //     // ✅ Parse each genre item if it's a string
//         //     genresArray = genresArray.map(genre => {
//         //         if (typeof genre === "string") {
//         //             try {
//         //                 return JSON.parse(genre);  // Convert string to object
//         //             } catch (e) {
//         //                 console.error("Error parsing genre:", genre, e);
//         //                 return null;  // Skip invalid genres
//         //             }
//         //         }
//         //         return genre;  // Already an object
//         //     }).filter(genre => genre && genre.name);  // Remove null values
//         // }
//         // // console.log("Raw Genres:", movie.genres);
//         // // console.log("Genres Type:", typeof movie.genres);
//         // // Format genres properly]
//         // console.log("Parsed Genres:", genresArray);
//         // // console.log("Genres Type:", typeof genresArray);

//         const genreNames = movie.genres && Array.isArray(movie.genres) ? movie.genres.map(genre => genre.name).join(", ") : "Unknown";

//         // console.log("Final Genres String:", genreNames);
//         // console.log("Genres : ", genreNames);
//         // console.log("Genres type: ", typeof movie.genres);
//         // console.log("Movie: ", movie.title);

//         movieElement.innerHTML = `
//             <h3>${movie.title}</h3>
//             <p><strong>Genres:</strong> ${genreNames}</p>
//             <p><strong>Tagline:</strong> ${movie.tagline ? movie.tagline : "No tagline available"}</p>
//             <p><strong>Similarity Score:</strong> ${movie.similarity_score.toFixed(2)}</p>
//             <p><strong>Overview:</strong> ${movie.overview ? movie.overview : "No overview available"}</p>`;

//         resultsDiv.appendChild(movieElement);
//     });
// }



// // uvicorn recommendation.model:app --host 0.0.0.0 --port 8001 --reload


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
        movieElement.classList.add("movie-card"); // Apply styling

        // Extract genre names and join them into a comma-separated string
        const genreNames = movie.genres && Array.isArray(movie.genres)
            ? movie.genres.map(genre => genre.name).join(", ")
            : "Unknown";

        // console.log(typeof movie.genres); // Debugging line
        // console.log("Parsed Genres:", genreNames); // Debugging line

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