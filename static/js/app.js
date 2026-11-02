document.addEventListener('DOMContentLoaded', () => {
  let allMovies = [];
  let selectedMovies = [];
  let currentGenre = 'all';

  // DOM Elements
  const searchInput = document.getElementById('movieSearchInput');
  const clearSearchBtn = document.getElementById('clearSearchBtn');
  const autocompleteDropdown = document.getElementById('autocompleteDropdown');
  const selectedPillsContainer = document.getElementById('selectedPillsContainer');
  const selectedPillsList = document.getElementById('selectedPillsList');
  const recommendBtn = document.getElementById('recommendBtn');
  const recommendationsSection = document.getElementById('recommendationsSection');
  const recommendationsGrid = document.getElementById('recommendationsGrid');
  const recomHeading = document.getElementById('recomHeading');
  const recomBadgeInfo = document.getElementById('recomBadgeInfo');
  const trendingGrid = document.getElementById('trendingGrid');
  const genreChips = document.querySelectorAll('.genre-chip');
  const algoOptions = document.querySelectorAll('.algo-option');
  const movieModal = document.getElementById('movieModal');
  const modalBody = document.getElementById('modalBody');
  const closeModalBtn = document.getElementById('closeModalBtn');

  // 1. Initial Load: Fetch All Movies & Top Rated Catalog
  fetchMoviesCatalog();
  fetchTrendingMovies();

  async function fetchMoviesCatalog() {
    try {
      const res = await fetch('/api/movies');
      const data = await res.json();
      if (data.success) {
        allMovies = data.movies;
      }
    } catch (err) {
      console.error('Error fetching catalog:', err);
    }
  }

  async function fetchTrendingMovies() {
    try {
      const res = await fetch('/api/trending?limit=16');
      const data = await res.json();
      if (data.success) {
        renderMoviesGrid(trendingGrid, data.movies, false);
      }
    } catch (err) {
      console.error('Error fetching trending:', err);
    }
  }

  // 2. Search & Autocomplete
  searchInput.addEventListener('input', (e) => {
    const query = e.target.value.trim().toLowerCase();
    if (query.length > 0) {
      clearSearchBtn.classList.remove('d-none');
      const matches = allMovies.filter(m => m.title.toLowerCase().includes(query)).slice(0, 8);
      renderAutocomplete(matches);
    } else {
      clearSearchBtn.classList.add('d-none');
      autocompleteDropdown.classList.add('d-none');
    }
  });

  clearSearchBtn.addEventListener('click', () => {
    searchInput.value = '';
    clearSearchBtn.classList.add('d-none');
    autocompleteDropdown.classList.add('d-none');
    searchInput.focus();
  });

  document.addEventListener('click', (e) => {
    if (!e.target.closest('.search-box-wrapper')) {
      autocompleteDropdown.classList.add('d-none');
    }
  });

  function renderAutocomplete(matches) {
    if (matches.length === 0) {
      autocompleteDropdown.innerHTML = '<div class="autocomplete-item text-muted">No matching movies found</div>';
      autocompleteDropdown.classList.remove('d-none');
      return;
    }

    autocompleteDropdown.innerHTML = matches.map(m => `
      <div class="autocomplete-item" data-title="${encodeURIComponent(m.title)}">
        <div>
          <strong>${m.title}</strong>
          <span class="small text-muted ms-2">(${m.genres_list.slice(0, 2).join(', ')})</span>
        </div>
        <span class="badge-add"><i class="bi bi-plus-lg"></i> Select</span>
      </div>
    `).join('');
    autocompleteDropdown.classList.remove('d-none');

    autocompleteDropdown.querySelectorAll('.autocomplete-item').forEach(item => {
      item.addEventListener('click', () => {
        const title = decodeURIComponent(item.getAttribute('data-title'));
        addSelectedMovie(title);
        searchInput.value = '';
        clearSearchBtn.classList.add('d-none');
        autocompleteDropdown.classList.add('d-none');
      });
    });
  }

  // 3. Manage Selected Movies
  function addSelectedMovie(title) {
    if (!selectedMovies.includes(title)) {
      selectedMovies.push(title);
      updateSelectedPills();
      showToast(`Added "${title}" to your favorites!`);
      // Auto trigger recommendation if 1st selection
      if (selectedMovies.length === 1) {
        getRecommendations();
      }
    }
  }

  function removeSelectedMovie(title) {
    selectedMovies = selectedMovies.filter(t => t !== title);
    updateSelectedPills();
    if (selectedMovies.length > 0) {
      getRecommendations();
    } else {
      recommendationsSection.classList.add('d-none');
    }
  }

  function updateSelectedPills() {
    if (selectedMovies.length === 0) {
      selectedPillsContainer.classList.add('d-none');
      selectedPillsList.innerHTML = '';
      return;
    }

    selectedPillsContainer.classList.remove('d-none');
    selectedPillsList.innerHTML = selectedMovies.map(title => `
      <div class="movie-pill">
        <span>${title}</span>
        <i class="bi bi-x-circle-fill movie-pill-remove" onclick="window.removePill('${encodeURIComponent(title)}')"></i>
      </div>
    `).join('');
  }

  window.removePill = (encodedTitle) => {
    removeSelectedMovie(decodeURIComponent(encodedTitle));
  };

  recommendBtn.addEventListener('click', () => {
    getRecommendations();
  });

  // 4. Algorithm Switcher
  algoOptions.forEach(opt => {
    opt.addEventListener('click', () => {
      algoOptions.forEach(o => o.classList.remove('active'));
      opt.classList.add('active');
      const radio = opt.querySelector('input');
      radio.checked = true;
      if (selectedMovies.length > 0) {
        getRecommendations();
      }
    });
  });

  function getSelectedMode() {
    const checked = document.querySelector('input[name="recomMode"]:checked');
    return checked ? checked.value : 'hybrid';
  }

  // 5. Fetch & Display Recommendations
  async function getRecommendations(sourceTitle = null) {
    if (sourceTitle) {
      selectedMovies = [sourceTitle];
      updateSelectedPills();
    }

    if (selectedMovies.length === 0) return;

    const mode = getSelectedMode();
    recommendBtn.disabled = true;
    recommendBtn.innerHTML = '<i class="bi bi-hourglass-split me-1"></i> Computing Vectors...';

    try {
      const res = await fetch('/api/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          titles: selectedMovies,
          mode: mode,
          top_n: 8
        })
      });

      const data = await res.json();
      if (data.success && data.recommendations.length > 0) {
        recomHeading.textContent = `Recommended Based on: ${selectedMovies.join(', ')}`;
        recomBadgeInfo.innerHTML = `<i class="bi bi-check2-circle text-success"></i> ${mode.toUpperCase()} Engine • ${data.recommendations.length} Results`;
        renderMoviesGrid(recommendationsGrid, data.recommendations, true);
        recommendationsSection.classList.remove('d-none');
        recommendationsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    } catch (err) {
      console.error('Recommendation Error:', err);
      showToast('Error computing recommendations.');
    } finally {
      recommendBtn.disabled = false;
      recommendBtn.innerHTML = '<i class="bi bi-lightning-charge-fill me-1"></i> Generate Recommendations';
    }
  }

  // 6. Genre Chips Filter
  genreChips.forEach(chip => {
    chip.addEventListener('click', async () => {
      genreChips.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      const genre = chip.getAttribute('data-genre');
      currentGenre = genre;

      if (genre === 'all') {
        fetchTrendingMovies();
      } else {
        try {
          const res = await fetch(`/api/genre?name=${encodeURIComponent(genre)}&limit=16`);
          const data = await res.json();
          if (data.success) {
            renderMoviesGrid(trendingGrid, data.movies, false);
          }
        } catch (err) {
          console.error('Genre filter error:', err);
        }
      }
    });
  });

  // 7. Render Movies Cards Grid
  function renderMoviesGrid(container, movies, isRecommendation = false) {
    container.innerHTML = movies.map(m => {
      const matchBadge = isRecommendation && m.match_score 
        ? `<div class="match-badge"><i class="bi bi-fire"></i> ${m.match_score}% Match</div>`
        : '';

      const ratingBadge = `<div class="rating-badge"><i class="bi bi-star-fill"></i> ${m.rating}</div>`;

      const genresHtml = (m.genres_list || []).slice(0, 3).map(g => `<span class="genre-tag">${g}</span>`).join('');

      return `
        <div class="movie-card">
          <div class="poster-wrapper">
            <img src="${m.poster_url}" class="poster-img" alt="${m.title}" loading="lazy" onerror="this.src='https://via.placeholder.com/300x450/111827/94a3b8?text=${encodeURIComponent(m.title)}'">
            <div class="poster-gradient"></div>
            ${matchBadge}
            ${ratingBadge}
          </div>
          <div class="card-details">
            <div>
              <h4 class="movie-title">${m.title}</h4>
              <div class="movie-meta"><i class="bi bi-person me-1"></i> ${m.director} • ${m.year}</div>
              <div class="genre-tags">${genresHtml}</div>
            </div>
            <div class="card-actions">
              <button class="btn-recommend-this" onclick="window.triggerRecommend('${encodeURIComponent(m.title)}')">
                <i class="bi bi-stars"></i> More Like This
              </button>
              <button class="btn-info-modal" onclick="window.openModal(${m.movieId})">
                <i class="bi bi-info-circle"></i>
              </button>
            </div>
          </div>
        </div>
      `;
    }).join('');
  }

  window.triggerRecommend = (encodedTitle) => {
    const title = decodeURIComponent(encodedTitle);
    getRecommendations(title);
  };

  // 8. Movie Details Modal
  window.openModal = (movieId) => {
    const movie = allMovies.find(m => m.movieId === movieId);
    if (!movie) return;

    modalBody.innerHTML = `
      <div class="modal-grid">
        <img src="${movie.poster_url}" class="modal-poster" alt="${movie.title}">
        <div>
          <div class="d-flex align-items-center gap-2 mb-2">
            <span class="badge bg-danger px-2 py-1"><i class="bi bi-star-fill text-warning me-1"></i>${movie.rating} / 10</span>
            <span class="small text-muted">${movie.year}</span>
          </div>
          <h2 class="fw-bold mb-2">${movie.title}</h2>
          <p class="small text-muted mb-3"><i class="bi bi-camera-reels me-1"></i>Directed by <strong>${movie.director}</strong></p>
          <div class="genre-tags mb-3">
            ${(movie.genres_list || []).map(g => `<span class="genre-tag">${g}</span>`).join('')}
          </div>
          <h6 class="fw-bold text-light mb-1">Storyline Overview</h6>
          <p class="small text-muted mb-4" style="line-height: 1.6;">${movie.overview}</p>
          <div class="d-flex gap-2">
            <button class="btn-primary-action w-100" onclick="window.triggerRecommend('${encodeURIComponent(movie.title)}'); window.closeModal();">
              <i class="bi bi-lightning-charge-fill me-1"></i> Find Similar Movies
            </button>
          </div>
        </div>
      </div>
    `;
    movieModal.classList.remove('d-none');
  };

  window.closeModal = () => {
    movieModal.classList.add('d-none');
  };

  closeModalBtn.addEventListener('click', window.closeModal);
  movieModal.addEventListener('click', (e) => {
    if (e.target === movieModal) window.closeModal();
  });

  // 9. Toast Notification
  function showToast(msg) {
    const toast = document.getElementById('toastNotification');
    const toastMsg = document.getElementById('toastMessage');
    toastMsg.textContent = msg;
    toast.classList.remove('d-none');
    setTimeout(() => {
      toast.classList.add('d-none');
    }, 3000);
  }
});
