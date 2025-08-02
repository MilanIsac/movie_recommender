async function getRecommendations() {
    const movie_name = document.getElementById("movie_name").value;
    if (!movie_name) {
        alert("Please enter a movie name");
        return;
    }

    try {
        const response = await fetch(`http://localhost:8001/recommend/${encodeURIComponent(movie_name)}`);
        const data = await response.json();
        // const pic = fetchData(movie_name);
        // const data1 = await pic.json();
        displayResults(data.recommendations);
    } catch (error) {
        console.log("Error fetching the recommendations: ", error);
        alert("Failed to fetch recommendations", error);
    }
}

async function fetchImage(title) {
    const url = `https://www.omdbapi.com/?apikey=c192eea2&t=${encodeURIComponent(title)}`;

    try {
        const res = await fetch(url);
        const data = await res.json();
        console.log(data);

        if (data.Poster && data.Poster !== "N/A") {
            return data.Poster;
        } else {
            return "https://via.placeholder.com/200x300?text=No+Image";
        }
    } catch (error) {
        console.error(`Error fetching image for ${title}:`, error);
        return "https://via.placeholder.com/200x300?text=No+Image";;
    }
}

async function getPlot(title) {
    const url = `https://www.omdbapi.com/?apikey=c192eea2&t=${encodeURIComponent(title)}`;

    try {
        const res = await fetch(url);
        const data = await res.json();
        if (data.Plot && data.Plot !== "N/A") {
            return data.Plot;
        }
        else {
            return "N/A";
        }
    } catch (error) {
        console.error("Error fetching plot: ", error);
        return "N/A";
    }
}


async function displayResults(movies) {
    const resultsDiv = document.getElementById("results");
    resultsDiv.innerHTML = ""; // Clear previous results

    if (movies.length === 0) {
        resultsDiv.innerHTML = "<p>No recommendations found</p>";
        return;
    }

    const movieData = await Promise.all(
        movies.map(async (movie) => {
            const [imgURL, plot] = await Promise.all([
                fetchImage(movie.title),
                getPlot(movie.title)
            ]);
            return { ...movie, imgURL, plot };
        })
    );

    for (const movie of movieData) {

        // const imgURL = await fetchImage(movie.title);
        // const plot = await getPlot(movie.title);
        // // console.log(imgURL);

        // const [imgURL, plot] = await Promise.all([
        //     fetchImage(movie.title),
        //     getPlot(movie.title)
        // ]);

        const movieElement = document.createElement("div");
        movieElement.classList.add("movie-card");

        const genreNames = movie.genres && Array.isArray(movie.genres)
            ? movie.genres.map(genre => genre.name).join(", ")
            : "Unknown";

        movieElement.innerHTML = `
            <h3>${movie.title}</h3>
            <div style="display: flex; justify-content: center;">
            <img src="${movie.imgURL}" alt="${movie.title}" style="width:200px;" />
            </div>
            <p><strong>Genres:</strong> ${genreNames}</p>
            <p><strong>Tagline:</strong> ${movie.tagline}</p>
            <p><strong>Similarity Score:</strong> ${movie.similarity_score.toFixed(2)}</p>
            <p><strong>Rating:</strong> ${movie.vote_average.toFixed(1)}/10 (${movie.vote_count} votes)</p>
            <p><strong>Overview:</strong> ${movie.plot}</p>`;

        resultsDiv.appendChild(movieElement);
    };
}

document.getElementById("movie_name").addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
        getRecommendations();
    }
});
