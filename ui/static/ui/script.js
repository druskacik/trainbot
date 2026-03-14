document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('search-form');
    const returnParamsGroup = document.getElementById('return-params-group');
    const typeRadios = document.querySelectorAll('input[name="type"]');
    const searchBtn = document.getElementById('search-btn');
    const btnText = searchBtn.querySelector('.btn-text');
    const btnLoader = searchBtn.querySelector('.btn-loader');

    const resultsContainer = document.getElementById('results-container');
    const emptyState = document.getElementById('empty-state');
    const noResultsState = document.getElementById('no-results-state');

    const startStationSelect = document.getElementById('start-station');
    const endStationSelect = document.getElementById('end-station');

    // Popular stations: Prague, Amsterdam, Brussels, Berlin Hbf, Paris (display order)
    const POPULAR_STATION_IDS = ['5457076', '8400058', '8800104', '8010100', '8700015'];

    function buildStationOptionsHTML(stations) {
        const byId = new Map(stations.map(s => [s.id, s]));
        const popular = POPULAR_STATION_IDS.map(id => byId.get(id)).filter(Boolean);
        const rest = stations.filter(s => !POPULAR_STATION_IDS.includes(s.id)).sort((a, b) => a.name.localeCompare(b.name));

        let html = '';
        if (popular.length > 0) {
            html += '<optgroup label="Popular">';
            html += popular.map(s => `<option value="${s.id}">${s.name}</option>`).join('');
            html += '</optgroup>';
        }
        if (rest.length > 0) {
            html += '<optgroup label="Other stations">';
            html += rest.map(s => `<option value="${s.id}">${s.name}</option>`).join('');
            html += '</optgroup>';
        }
        return html;
    }

    // Fetch and populate stations
    const loadStations = async () => {
        try {
            const response = await fetch('/api/stations');
            const result = await response.json();
            
            if (result.status === 'success') {
                const stations = result.data;
                const optionsHTML = buildStationOptionsHTML(stations);

                const placeholderStart = '<option value="" disabled>Select departure...</option>';
                const placeholderEnd = '<option value="" disabled>Select destination...</option>';
                startStationSelect.innerHTML = placeholderStart + optionsHTML;
                endStationSelect.innerHTML = placeholderEnd + optionsHTML;

                // Set defaults if available (Prague to Amsterdam)
                const pragueId = '5457076';
                const amsterdamId = '8400058';
                if (stations.some(s => s.id === pragueId)) startStationSelect.value = pragueId;
                if (stations.some(s => s.id === amsterdamId)) endStationSelect.value = amsterdamId;
            }
        } catch (error) {
            console.error('Failed to load stations:', error);
            startStationSelect.innerHTML = '<option value="" disabled>Error loading stations</option>';
            endStationSelect.innerHTML = '<option value="" disabled>Error loading stations</option>';
        }
    };
    
    loadStations();

    // Toggle return params visibility
    typeRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            if (e.target.value === 'return') {
                returnParamsGroup.classList.remove('hidden');
                // Ensure layout animation is smooth
                returnParamsGroup.style.animation = 'fadeIn 0.3s ease-out';
            } else {
                returnParamsGroup.classList.add('hidden');
            }
        });
    });

    // Initial check
    if (document.querySelector('input[name="type"]:checked').value === 'single') {
        returnParamsGroup.classList.add('hidden');
    }

    // Format Date helper
    const formatDate = (dateStr) => {
        const options = { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' };
        return new Date(dateStr).toLocaleDateString(undefined, options);
    };

    // Render results
    const renderResults = (data, isReturn) => {
        resultsContainer.innerHTML = '';

        if (!data || data.length === 0) {
            resultsContainer.classList.add('hidden');
            noResultsState.classList.remove('hidden');
            return;
        }

        noResultsState.classList.add('hidden');
        resultsContainer.classList.remove('hidden');

        data.forEach((trip, index) => {
            const card = document.createElement('a');
            card.className = 'result-card';
            card.href = trip.booking_url;
            card.target = '_blank';
            card.style.textDecoration = 'none';
            card.style.color = 'inherit';
            card.style.display = 'block';
            card.style.animationDelay = `${index * 0.05}s`;

            const cur = trip.currency.toUpperCase();
            const currencySymbol = cur === 'EUR' ? '€' : (cur === 'CZK' ? 'Kč' : cur);

            let content = `
                <div class="price-tag">${trip.total_price.toFixed(2)} <span style="font-size: 0.5em; font-weight: normal">${currencySymbol}</span></div>
                
                <div class="journey-leg">
                    <div class="leg-label"><span style="font-size: 1.2em">➡️</span> Outbound</div>
                    <div class="leg-date">${formatDate(trip.outbound_date)}</div>
                    ${isReturn ? `<div class="leg-price">Leg Price: ${trip.outbound_price.toFixed(2)} ${currencySymbol}</div>` : ''}
                </div>
            `;

            if (isReturn && trip.return_date) {
                content += `
                    <div class="journey-leg">
                        <div class="leg-label"><span style="font-size: 1.2em">⬅️</span> Return</div>
                        <div class="leg-date">${formatDate(trip.return_date)}</div>
                        <div class="leg-price">Leg Price: ${trip.return_price.toFixed(2)} ${currencySymbol}</div>
                    </div>
                    <div class="trip-duration">⏳ Trip Duration: ${trip.duration_days} days</div>
                `;
            }

            card.innerHTML = content;
            resultsContainer.appendChild(card);
        });
    };

    // Form Submit
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // UI Loading State
        emptyState.classList.add('hidden');
        noResultsState.classList.add('hidden');
        resultsContainer.innerHTML = '';

        searchBtn.disabled = true;
        btnText.textContent = 'Searching...';
        btnLoader.classList.remove('hidden');

        const formData = new FormData(form);
        const searchParams = new URLSearchParams(formData);
        
        if (!formData.get('start_id') || !formData.get('end_id') || formData.get('start_id') === formData.get('end_id')) {
            alert('Please select valid and distinct starting and destination stations.');
            searchBtn.disabled = false;
            btnText.textContent = 'Search Lowest Fares';
            btnLoader.classList.add('hidden');
            emptyState.classList.remove('hidden');
            return;
        }

        try {
            const response = await fetch(`/api/search?${searchParams.toString()}`);
            const result = await response.json();

            if (result.status === 'success') {
                const isReturn = formData.get('type') === 'return';
                renderResults(result.routes, isReturn);
            } else {
                console.error(result.message);
                alert('An error occurred while fetching trips: ' + result.message);
                noResultsState.classList.remove('hidden');
            }
        } catch (error) {
            console.error('Fetch error:', error);
            noResultsState.classList.remove('hidden');
        } finally {
            // Restore UI
            searchBtn.disabled = false;
            btnText.textContent = 'Search Lowest Fares';
            btnLoader.classList.add('hidden');
        }
    });
});
