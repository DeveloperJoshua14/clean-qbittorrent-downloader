// Function to display a notification message
function showNotification(message) {
    hideNotification();
    const notification = document.getElementById("notification");
    notification.textContent = message;
    notification.style.display = "block";
}

// Function to hide the notification
function hideNotification() {
    const notification = document.getElementById("notification");
    notification.style.display = "none";
}

// Reference to input and button
const searchInput = document.getElementById('searchInput');
const searchButton = document.getElementById('searchButton');

// Trigger search on button click
searchButton.addEventListener('click', performSearch);

// Trigger search on Enter key press
searchInput.addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
        performSearch();
    }
});

// Function to perform the search
async function performSearch() {
    const searchTerm = searchInput.value.trim();

    if (!searchTerm) {
        showNotification('Please enter a search term.');
        return;
    }
    hideNotification();

    // Fetch movies from the OMDb API
    fetch(`https://www.omdbapi.com/?apikey=82186d11&s=${searchTerm}`)
        .then(response => response.json())
        .then(data => {
            const results = document.getElementById('results');
            results.innerHTML = ''; // Clear previous results

            if (data.Response === 'False') {
                results.innerHTML = `<p>No results found for "${searchTerm}".</p>`;
                return;
            }

            // Render results with clickable images
            data.Search.forEach(movie => {
                if (movie.Poster === 'N/A') {
                    movie.Poster = "media/nocover.png";
                }
            
                // Create movie card
                const movieCard = document.createElement('div');
                movieCard.classList.add('movie-card');
                movieCard.innerHTML = `
                    <img src="${movie.Poster}" alt="${movie.Title}" class="movie-image">
                    <h3>${movie.Title}</h3>
                    <p>${movie.Year}</p>
                    <button class="select-button" data-movie='${JSON.stringify(movie)
                        .replace(/'/g, '&#39;')
                        .replace(/"/g, '&quot;')}'>
                        Download
                    </button>
                `;
            
                // Add click event to the image
                movieCard.querySelector('.movie-image').addEventListener('click', function(event) {
                    event.stopPropagation(); // Prevent bubbling to parent elements
                    const imdbUrl = `https://imdb.com/title/${movie.imdbID}/`;
                    window.open(imdbUrl, '_blank'); // Open IMDb page in a new tab
                });
            
                results.appendChild(movieCard);
            });
            
            // Add event listeners to the "Download" buttons
            document.querySelectorAll('.select-button').forEach(button => {
                button.addEventListener('click', function(event) {
                    event.stopPropagation(); // Prevent bubbling to the parent card
                    const movie = JSON.parse(this.dataset.movie); // Parse the JSON string back to an object
                    
                    showNotification("Loading...");
                    // Prepare the payload
                    const payload = { movie };
            
                    // Send the movie data to the backend
                    fetch('https://movie.nafzigers.us/download.php', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(payload)
                    })
                        .then(response => {
                            hideNotification();
                            if (response.status === 300) {
                                showNotification('Movie Download Queued!');
                            } else if (response.status === 301) {
                                showNotification('Show Download Queued!');
                            } else if (response.status === 302) {
                                showNotification('That is not a Moive or Show!');
                            } else {
                                showNotification('Failed. Please Conntact Joshua.');
                            }
                        })
                        .catch(error => {
                            hideNotification();
                            console.error('Error downloading: ', error);
                            showNotification('Failed. Please Conntact Joshua.');
                        });
                });
            });
        })
        .catch(error => {
            showNotification('Failed. Please Conntact Joshua.');
            console.error('Error fetching movie data: ', error);
        });
    
    await new Promise((resolve) => setTimeout(resolve, 3000));
    hideNotification();
}