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
    const formError = document.getElementById('form-error');

    const startStationSelect = document.getElementById('start-station');
    const endStationSelect = document.getElementById('end-station');
    let allCities = [];
    let cityConnections = {};

    function showFormError(message) {
        formError.textContent = message;
        formError.hidden = false;
    }

    function clearFormError() {
        formError.textContent = '';
        formError.hidden = true;
    }

    const POPULAR_CITY_IDS = ['prague', 'amsterdam', 'brussels', 'berlin', 'paris', 'vienna'];

    function buildCityOptionsHTML(cities) {
        const byId = new Map(cities.map(city => [city.id, city]));
        const popular = POPULAR_CITY_IDS.map(id => byId.get(id)).filter(Boolean);
        const rest = cities.filter(city => !POPULAR_CITY_IDS.includes(city.id)).sort((a, b) => a.name.localeCompare(b.name));

        let html = '';
        if (popular.length > 0) {
            html += '<optgroup label="Popular">';
            html += popular.map(city => `<option value="${city.id}">${city.name}</option>`).join('');
            html += '</optgroup>';
        }
        if (rest.length > 0) {
            html += '<optgroup label="Other cities">';
            html += rest.map(city => `<option value="${city.id}">${city.name}</option>`).join('');
            html += '</optgroup>';
        }
        return html;
    }

    function formatPrice(amount, currency) {
        const cur = (currency || '').toUpperCase();
        const currencySymbol = cur === 'EUR' ? '€' : (cur === 'CZK' ? 'CZK' : (cur || ''));
        return `${amount.toFixed(2)} ${currencySymbol}`.trim();
    }

    function buildLegMarkup(label, date, price, currency) {
        return `
            <div class="journey-leg">
                <div class="leg-label">${label}</div>
                <div class="leg-date">${formatDate(date)}</div>
                <div class="leg-price">${formatPrice(price, currency)}</div>
            </div>
        `;
    }

    function buildProviderSummaryMarkup(trip, isReturn) {
        const sameProvider = isReturn && trip.return_provider_name &&
            trip.outbound_provider_name === trip.return_provider_name;
        if (sameProvider) {
            return `<div class="provider-pill">${trip.outbound_provider_name}</div>`;
        }
        const pills = [`<div class="provider-pill">${trip.outbound_provider_name}</div>`];
        if (isReturn && trip.return_provider_name) {
            pills.push(`<div class="provider-pill">${trip.return_provider_name}</div>`);
        }
        return pills.join('');
    }

    function buildTripNotesMarkup(trip) {
        const notes = [];
        if (trip.mixed_providers) {
            notes.push('Mixed providers');
        }
        return notes.map(note => `<div class="trip-note">${note}</div>`).join('');
    }

    function escapeHtml(value) {
        return String(value ?? '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function buildSecondaryBookingActionMarkup(trip, isReturn) {
        if (!isReturn || !trip.secondary_booking_url) {
            return '';
        }

        const providerName = trip.return_provider_name || 'return leg';
        return `
            <a
                class="booking-action"
                href="${escapeHtml(trip.secondary_booking_url)}"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="${escapeHtml(`Book return leg on ${providerName}`)}"
            >
                Book return
            </a>
        `;
    }

    function getTripAriaLabel(trip) {
        const outboundDetails = trip.outbound_leg?.booking_details || {};
        const from = (outboundDetails.from_city || '').trim() || 'Departure';
        const to = (outboundDetails.to_city || '').trim() || 'Destination';
        return `View trip ${from} to ${to}, ${formatPrice(trip.total_price, trip.currency)}`;
    }

    function createResultCard(trip) {
        const primaryBookingUrl = trip.primary_booking_url || '';
        const hasSecondaryBookingUrl = Boolean(trip.secondary_booking_url);
        let card;

        if (primaryBookingUrl && !hasSecondaryBookingUrl) {
            card = document.createElement('a');
            card.href = primaryBookingUrl;
            card.target = '_blank';
            card.rel = 'noopener noreferrer';
        } else {
            card = document.createElement('article');
            if (primaryBookingUrl) {
                card.tabIndex = 0;
                card.setAttribute('role', 'link');
                card.addEventListener('click', (event) => {
                    if (event.target.closest('.booking-action')) {
                        return;
                    }
                    window.open(primaryBookingUrl, '_blank', 'noopener,noreferrer');
                });
                card.addEventListener('keydown', (event) => {
                    if (event.target.closest('.booking-action')) {
                        return;
                    }
                    if (event.key === 'Enter' || event.key === ' ') {
                        event.preventDefault();
                        window.open(primaryBookingUrl, '_blank', 'noopener,noreferrer');
                    }
                });
            }
        }

        card.className = 'result-card';
        if (!(card instanceof HTMLAnchorElement) && primaryBookingUrl) {
            card.classList.add('is-clickable');
        }
        if (card instanceof HTMLElement) {
            card.setAttribute('aria-label', getTripAriaLabel(trip));
        }
        return card;
    }

    const buildDestinationOptionsHTML = (fromCityId) => {
        const placeholderEnd = '<option value="" disabled>Select destination city...</option>';
        const allowedIds = (cityConnections && fromCityId) ? cityConnections[fromCityId] : null;

        const baseCities = Array.isArray(allowedIds) && allowedIds.length > 0
            ? allCities.filter(city => allowedIds.includes(city.id))
            : allCities;

        const optionsHTML = buildCityOptionsHTML(baseCities);
        return placeholderEnd + optionsHTML;
    };

    const loadCities = async () => {
        try {
            const response = await fetch('/api/stations');
            const result = await response.json();
            
            if (result.status === 'success') {
                allCities = Array.isArray(result.data) ? result.data : [];
                cityConnections = result.connections || {};
                const optionsHTML = buildCityOptionsHTML(allCities);

                const placeholderStart = '<option value="" disabled>Select departure city...</option>';
                startStationSelect.innerHTML = placeholderStart + optionsHTML;

                const pragueId = 'prague';
                const amsterdamId = 'amsterdam';
                if (allCities.some(city => city.id === pragueId)) {
                    startStationSelect.value = pragueId;
                }

                const initialFromId = startStationSelect.value || '';
                endStationSelect.innerHTML = buildDestinationOptionsHTML(initialFromId);

                const canDefaultToAmsterdam =
                    initialFromId &&
                    allCities.some(city => city.id === amsterdamId) &&
                    Array.isArray(cityConnections[initialFromId]) &&
                    cityConnections[initialFromId].includes(amsterdamId);

                if (canDefaultToAmsterdam) {
                    endStationSelect.value = amsterdamId;
                }
            }
        } catch (error) {
            console.error('Failed to load cities:', error);
            startStationSelect.innerHTML = '<option value="" disabled>Error loading cities</option>';
            endStationSelect.innerHTML = '<option value="" disabled>Error loading cities</option>';
        }
    };
    
    startStationSelect.addEventListener('change', () => {
        const fromCityId = startStationSelect.value || '';
        endStationSelect.innerHTML = buildDestinationOptionsHTML(fromCityId);
        endStationSelect.value = '';
    });

    loadCities();

    // Toggle return params visibility
    typeRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            if (e.target.value === 'return') {
                returnParamsGroup.classList.remove('hidden');
                returnParamsGroup.classList.add('is-visible');
            } else {
                returnParamsGroup.classList.add('hidden');
                returnParamsGroup.classList.remove('is-visible');
            }
        });
    });

    // Initial check
    if (document.querySelector('input[name="type"]:checked').value === 'single') {
        returnParamsGroup.classList.add('hidden');
    } else {
        returnParamsGroup.classList.add('is-visible');
    }

    // Format Date helper
    const formatDate = (dateStr) => {
        if (!dateStr) {
            return '';
        }
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
        emptyState.classList.add('hidden');
        resultsContainer.classList.remove('hidden');

        data.forEach((trip, index) => {
            const card = createResultCard(trip);
            card.style.animationDelay = `${index * 0.05}s`;

            const cur = (trip.currency || '').toUpperCase();
            const currencySymbol = cur === 'EUR' ? '€' : (cur === 'CZK' ? 'CZK' : (cur || ''));

            let content = `
                <div class="price-tag">${trip.total_price.toFixed(2)} <span class="currency">${currencySymbol}</span></div>
                ${buildLegMarkup(
                    'Outbound',
                    trip.outbound_date,
                    trip.outbound_price,
                    trip.currency
                )}
            `;

            if (isReturn && trip.return_date) {
                content += `
                    ${buildLegMarkup(
                        'Return',
                        trip.return_date,
                        trip.return_price,
                        trip.currency
                    )}
                `;
            }

            content += `
                <div class="result-meta">
                    <div class="provider-summary">${buildProviderSummaryMarkup(trip, isReturn)}</div>
                    ${isReturn && trip.return_date ? `<div class="trip-duration">${trip.duration_days} ${trip.duration_days === 1 ? 'day' : 'days'}</div>` : ''}
                    ${buildTripNotesMarkup(trip)}
                    ${buildSecondaryBookingActionMarkup(trip, isReturn)}
                </div>
            `;

            card.innerHTML = content;

            card.querySelectorAll('.booking-action').forEach((action) => {
                action.addEventListener('click', (event) => {
                    event.stopPropagation();
                });
            });
            resultsContainer.appendChild(card);
        });
    };

    // Form Submit
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // UI loading state
        clearFormError();
        emptyState.classList.add('hidden');
        noResultsState.classList.add('hidden');
        resultsContainer.innerHTML = '';
        resultsContainer.setAttribute('aria-busy', 'true');

        searchBtn.disabled = true;
        btnText.textContent = 'Searching...';
        btnLoader.classList.remove('hidden');

        const formData = new FormData(form);
        const searchParams = new URLSearchParams(formData);
        
        if (!formData.get('start_id') || !formData.get('end_id') || formData.get('start_id') === formData.get('end_id')) {
            resultsContainer.setAttribute('aria-busy', 'false');
            searchBtn.disabled = false;
            btnText.textContent = 'Search Lowest Fares';
            btnLoader.classList.add('hidden');
            emptyState.classList.remove('hidden');
            showFormError('Please select valid and distinct departure and destination cities.');
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
                showFormError(result.message || 'An error occurred while fetching trips.');
                noResultsState.classList.remove('hidden');
            }
        } catch (error) {
            console.error('Fetch error:', error);
            showFormError('Network error. Please try again.');
            noResultsState.classList.remove('hidden');
        } finally {
            resultsContainer.setAttribute('aria-busy', 'false');
            searchBtn.disabled = false;
            btnText.textContent = 'Search Lowest Fares';
            btnLoader.classList.add('hidden');
        }
    });
});
