function stripDiacritics(str) {
    return str.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
}

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

    class Combobox {
        constructor({ inputId, listboxId, placeholder }) {
            this.input = document.getElementById(inputId);
            this.listbox = document.getElementById(listboxId);
            this.hidden = this.input.parentElement.querySelector('input[type="hidden"]');
            this.liveRegion = this.input.parentElement.querySelector('.combobox-live');
            this.wrapper = this.input.parentElement;
            this.placeholder = placeholder;

            this.cities = [];
            this.flatOptions = [];
            this.selectedId = '';
            this.activeIndex = -1;
            this.isOpen = false;
            this.onChange = null;

            this._bindEvents();
        }

        _bindEvents() {
            this.input.addEventListener('focus', () => {
                if (this.selectedId) {
                    this.input.select();
                }
                this._open();
            });

            this.input.addEventListener('input', () => {
                this.hidden.value = '';
                this.selectedId = '';
                this._filter(this.input.value);
                if (!this.isOpen) this._open();
            });

            this.input.addEventListener('keydown', (e) => this._onKeydown(e));

            this.input.addEventListener('blur', () => {
                requestAnimationFrame(() => {
                    if (this.wrapper.contains(document.activeElement)) return;
                    this._close();
                });
            });

            this.listbox.addEventListener('mousedown', (e) => {
                e.preventDefault();
                const option = e.target.closest('[role="option"]');
                if (option) {
                    this.selectCity(option.dataset.cityId);
                }
            });

            this.listbox.addEventListener('mousemove', (e) => {
                const option = e.target.closest('[role="option"]');
                if (option) {
                    const idx = this.flatOptions.indexOf(option);
                    if (idx !== -1 && idx !== this.activeIndex) {
                        this._setActiveIndex(idx);
                    }
                }
            });

            document.addEventListener('mousedown', (e) => {
                if (this.isOpen && !this.wrapper.contains(e.target)) {
                    this._close();
                }
            });
        }

        _onKeydown(e) {
            switch (e.key) {
                case 'ArrowDown':
                    e.preventDefault();
                    if (!this.isOpen) { this._open(); return; }
                    this._setActiveIndex(this.activeIndex < this.flatOptions.length - 1 ? this.activeIndex + 1 : 0);
                    break;
                case 'ArrowUp':
                    e.preventDefault();
                    if (!this.isOpen) { this._open(); return; }
                    this._setActiveIndex(this.activeIndex > 0 ? this.activeIndex - 1 : this.flatOptions.length - 1);
                    break;
                case 'Enter':
                    if (this.isOpen && this.activeIndex >= 0) {
                        e.preventDefault();
                        const opt = this.flatOptions[this.activeIndex];
                        if (opt) this.selectCity(opt.dataset.cityId);
                    }
                    break;
                case 'Escape':
                    if (this.isOpen) {
                        e.preventDefault();
                        this._close();
                    }
                    break;
                case 'Tab':
                    if (this.isOpen && this.activeIndex >= 0) {
                        const opt = this.flatOptions[this.activeIndex];
                        if (opt) this.selectCity(opt.dataset.cityId);
                    }
                    break;
                case 'Home':
                    if (this.isOpen && this.flatOptions.length > 0) {
                        e.preventDefault();
                        this._setActiveIndex(0);
                    }
                    break;
                case 'End':
                    if (this.isOpen && this.flatOptions.length > 0) {
                        e.preventDefault();
                        this._setActiveIndex(this.flatOptions.length - 1);
                    }
                    break;
            }
        }

        _open() {
            if (this.isOpen) return;
            this.isOpen = true;
            this.input.setAttribute('aria-expanded', 'true');
            this._filter(this.input.value === this._getNameById(this.selectedId) ? '' : this.input.value);
            this.listbox.hidden = false;
        }

        _close() {
            if (!this.isOpen) return;
            this.isOpen = false;
            this.input.setAttribute('aria-expanded', 'false');
            this.listbox.hidden = true;
            this.activeIndex = -1;
            this.input.setAttribute('aria-activedescendant', '');

            if (this.selectedId) {
                this.input.value = this._getNameById(this.selectedId);
            } else {
                const typed = this.input.value.trim().toLowerCase();
                const match = this.cities.find(c => c.name.toLowerCase() === typed);
                if (match) {
                    this.selectCity(match.id);
                } else {
                    this.input.value = '';
                    this.hidden.value = '';
                }
            }
        }

        _filter(query) {
            const q = stripDiacritics((query || '').trim().toLowerCase());
            const filtered = q
                ? this.cities.filter(c => stripDiacritics(c.name.toLowerCase()).includes(q))
                : this.cities;

            this._renderOptions(filtered, q);
        }

        _renderOptions(cities, query) {
            const listboxId = this.listbox.id;
            const byId = new Map(cities.map(c => [c.id, c]));
            const popular = POPULAR_CITY_IDS.map(id => byId.get(id)).filter(Boolean);
            const rest = cities.filter(c => !POPULAR_CITY_IDS.includes(c.id))
                .sort((a, b) => a.name.localeCompare(b.name));

            let html = '';
            const addGroup = (label, items) => {
                if (items.length === 0) return;
                html += `<li role="presentation" class="combobox-group-label">${label}</li>`;
                items.forEach(city => {
                    const optId = `${listboxId}-opt-${city.id}`;
                    const selected = city.id === this.selectedId ? ' aria-selected="true"' : '';
                    const displayName = query ? this._highlightMatch(city.name, query) : city.name;
                    html += `<li role="option" id="${optId}" class="combobox-option" data-city-id="${city.id}"${selected}>${displayName}</li>`;
                });
            };

            addGroup('Popular', popular);
            addGroup('Other cities', rest);

            if (cities.length === 0) {
                html = '<li class="combobox-no-results" role="presentation">No cities found</li>';
            }

            this.listbox.innerHTML = html;
            this.flatOptions = Array.from(this.listbox.querySelectorAll('[role="option"]'));
            this.activeIndex = -1;
            this.input.setAttribute('aria-activedescendant', '');

            const count = cities.length;
            this.liveRegion.textContent = count === 0
                ? 'No cities found'
                : `${count} ${count === 1 ? 'city' : 'cities'} available`;
        }

        _highlightMatch(name, query) {
            const idx = stripDiacritics(name.toLowerCase()).indexOf(query);
            if (idx === -1) return name;
            const before = name.slice(0, idx);
            const match = name.slice(idx, idx + query.length);
            const after = name.slice(idx + query.length);
            return `${before}<mark>${match}</mark>${after}`;
        }

        _setActiveIndex(index) {
            if (this.activeIndex >= 0 && this.activeIndex < this.flatOptions.length) {
                this.flatOptions[this.activeIndex].classList.remove('combobox-option--active');
            }
            this.activeIndex = index;
            const opt = this.flatOptions[index];
            if (opt) {
                opt.classList.add('combobox-option--active');
                this.input.setAttribute('aria-activedescendant', opt.id);
                opt.scrollIntoView({ block: 'nearest' });
            }
        }

        selectCity(cityId) {
            this.selectedId = cityId;
            this.hidden.value = cityId;
            this.input.value = this._getNameById(cityId);
            this._close();
            if (this.onChange) this.onChange(cityId);
        }

        setCities(cities) {
            this.cities = cities;
            if (this.selectedId && !cities.some(c => c.id === this.selectedId)) {
                this.selectedId = '';
                this.hidden.value = '';
                this.input.value = '';
            }
            if (this.isOpen) {
                this._filter(this.input.value === this._getNameById(this.selectedId) ? '' : this.input.value);
            }
        }

        setValue(cityId) {
            const city = this.cities.find(c => c.id === cityId);
            if (city) {
                this.selectedId = cityId;
                this.hidden.value = cityId;
                this.input.value = city.name;
            }
        }

        getSelectedId() {
            return this.selectedId;
        }

        _getNameById(id) {
            const city = this.cities.find(c => c.id === id);
            return city ? city.name : '';
        }
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

    const startCombobox = new Combobox({
        inputId: 'start-station',
        listboxId: 'start-station-listbox',
        placeholder: 'Select departure city...',
    });

    const endCombobox = new Combobox({
        inputId: 'end-station',
        listboxId: 'end-station-listbox',
        placeholder: 'Select destination city...',
    });

    function getDestinationCities(fromCityId) {
        const allowedIds = (cityConnections && fromCityId) ? cityConnections[fromCityId] : null;
        return Array.isArray(allowedIds) && allowedIds.length > 0
            ? allCities.filter(city => allowedIds.includes(city.id))
            : allCities;
    }

    startCombobox.onChange = (cityId) => {
        endCombobox.setCities(getDestinationCities(cityId));
    };

    const loadCities = async () => {
        try {
            const response = await fetch('/api/stations');
            const result = await response.json();

            if (result.status === 'success') {
                allCities = Array.isArray(result.data) ? result.data : [];
                cityConnections = result.connections || {};

                startCombobox.setCities(allCities);
                startCombobox.input.placeholder = 'Select departure city...';

                const pragueId = 'prague';
                const amsterdamId = 'amsterdam';

                if (allCities.some(city => city.id === pragueId)) {
                    startCombobox.setValue(pragueId);
                }

                endCombobox.setCities(getDestinationCities(startCombobox.getSelectedId()));
                endCombobox.input.placeholder = 'Select destination city...';

                const fromId = startCombobox.getSelectedId();
                const canDefaultToAmsterdam =
                    fromId &&
                    allCities.some(city => city.id === amsterdamId) &&
                    Array.isArray(cityConnections[fromId]) &&
                    cityConnections[fromId].includes(amsterdamId);

                if (canDefaultToAmsterdam) {
                    endCombobox.setValue(amsterdamId);
                }
            }
        } catch (error) {
            console.error('Failed to load cities:', error);
            startCombobox.input.placeholder = 'Error loading cities';
            endCombobox.input.placeholder = 'Error loading cities';
        }
    };

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
                showFormError(result.message || 'An error occurred while fetching trips.');
                noResultsState.classList.remove('hidden');
            }
        } catch (error) {
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
