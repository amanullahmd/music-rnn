/**
 * Generation interface functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    const generationForm = document.getElementById('generationForm');
    const seedInput = document.getElementById('seedInput');
    const temperatureSlider = document.getElementById('temperatureSlider');
    const temperatureValue = document.getElementById('temperatureValue');
    const lengthSlider = document.getElementById('lengthSlider');
    const lengthValue = document.getElementById('lengthValue');
    const generateBtn = document.getElementById('generateBtn');
    const generateSpinner = document.getElementById('generateSpinner');

    console.log('Generation form initialized');

    // Update temperature display
    temperatureSlider.addEventListener('input', function() {
        const value = parseFloat(this.value).toFixed(1);
        temperatureValue.textContent = value;
    });

    // Update length display
    lengthSlider.addEventListener('input', function() {
        lengthValue.textContent = this.value;
    });

    // Handle form submission
    generationForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        console.log('Form submitted');

        // Disable button and show loading state
        generateBtn.disabled = true;
        generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';

        try {
            // Collect parameters
            const seed = seedInput.value.trim();
            const temperature = parseFloat(temperatureSlider.value);
            const length = parseInt(lengthSlider.value);

            console.log('Sending request:', { seed, temperature, length });

            // Call API
            const result = await apiClient.generate({
                seed: seed,
                temperature: temperature,
                length: length
            });

            console.log('Generation result:', result);

            // Display result
            displayGeneration(result);

            // Add to history
            addToHistory(result);

            // Show success message
            showSuccess('✅ Music generated successfully!');

        } catch (error) {
            console.error('Generation error:', error);
            showError('❌ Generation failed: ' + error.message);
        } finally {
            // Re-enable button
            generateBtn.disabled = false;
            generateBtn.innerHTML = '<i class="fas fa-magic"></i> Generate Music';
        }
    });
});

/**
 * Display generated music
 */
function displayGeneration(result) {
    const musicCode = document.getElementById('musicCode');

    // Display the notation
    musicCode.textContent = result.notation;

    // Apply syntax highlighting if available
    if (typeof hljs !== 'undefined') {
        hljs.highlightElement(musicCode);
    }

    // Enable playback controls
    enablePlaybackControls();
}

/**
 * Enable playback controls
 */
function enablePlaybackControls() {
    document.getElementById('downloadAbcBtn').disabled = false;
    document.getElementById('favoriteBtn').disabled = false;
}

/**
 * Add generation to history
 */
function addToHistory(result) {
    const history = getHistory();

    // Create history item
    const item = {
        id: generateUUID(),
        notation: result.notation,
        seed: result.parameters.seed,
        temperature: result.parameters.temperature,
        length: result.parameters.length,
        timestamp: result.timestamp,
        isFavorite: false
    };

    // Add to beginning of history
    history.unshift(item);

    // Keep only last 10 items
    if (history.length > 10) {
        history.pop();
    }

    // Save to localStorage
    saveHistory(history);

    // Update history display
    updateHistoryDisplay();
    
    // Update stats
    updateStats();
}

/**
 * Get history from localStorage
 */
function getHistory() {
    const stored = localStorage.getItem('history');
    return stored ? JSON.parse(stored) : [];
}

/**
 * Save history to localStorage
 */
function saveHistory(history) {
    localStorage.setItem('history', JSON.stringify(history));
}

/**
 * Load history from localStorage
 */
function loadHistory() {
    updateHistoryDisplay();
    updateStats();
}

/**
 * Update statistics display
 */
function updateStats() {
    const history = getHistory();
    const favorites = history.filter(item => item.isFavorite);
    
    document.getElementById('totalGenerated').textContent = history.length;
    document.getElementById('totalFavorites').textContent = favorites.length;
}

/**
 * Update history display
 */
function updateHistoryDisplay() {
    const history = getHistory();
    const historyList = document.getElementById('historyList');

    if (history.length === 0) {
        historyList.innerHTML = '<p class="text-muted text-center py-4"><i class="fas fa-inbox"></i> No generations yet</p>';
        return;
    }

    historyList.innerHTML = history.map((item, index) => `
        <div class="list-group-item history-item" data-index="${index}">
            <div class="d-flex justify-content-between align-items-start">
                <div class="flex-grow-1">
                    <h6 class="mb-1"><i class="fas fa-music"></i> Generation ${history.length - index}</h6>
                    <small class="text-muted d-block">${formatTimestamp(item.timestamp)}</small>
                    <small class="text-muted d-block">
                        🔥 ${item.temperature} | 📏 ${item.length}
                    </small>
                </div>
                <button class="btn btn-sm btn-outline-warning favorite-btn" data-index="${index}" title="Add to favorites">
                    ${item.isFavorite ? '⭐' : '☆'}
                </button>
            </div>
        </div>
    `).join('');

    // Add event listeners
    document.querySelectorAll('.history-item').forEach(item => {
        item.addEventListener('click', function(e) {
            if (!e.target.closest('.favorite-btn')) {
                const index = this.dataset.index;
                loadHistoryItem(index);
            }
        });
    });

    document.querySelectorAll('.favorite-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            const index = this.dataset.index;
            toggleFavorite(index);
        });
    });
}

/**
 * Load history item
 */
function loadHistoryItem(index) {
    const history = getHistory();
    const item = history[index];

    if (item) {
        // Update display
        document.getElementById('musicCode').textContent = item.notation;
        
        if (typeof hljs !== 'undefined') {
            hljs.highlightElement(document.getElementById('musicCode'));
        }

        // Enable playback controls
        enablePlaybackControls();

        // Mark as active
        document.querySelectorAll('.history-item').forEach((el, i) => {
            el.classList.toggle('active', i === parseInt(index));
        });
    }
}

/**
 * Toggle favorite status
 */
function toggleFavorite(index) {
    const history = getHistory();
    if (history[index]) {
        history[index].isFavorite = !history[index].isFavorite;
        saveHistory(history);
        updateHistoryDisplay();
        updateStats();
    }
}

/**
 * Download ABC notation as file
 */
function downloadAbc() {
    console.log('Download ABC clicked');

    try {
        const notation = document.getElementById('musicCode').textContent;

        if (!notation || notation === '🎼 No music generated yet. Click "Generate Music" to start.') {
            showError('No music to download');
            return;
        }

        const blob = new Blob([notation], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;

        const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
        link.download = `music_${timestamp}.abc`;

        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        URL.revokeObjectURL(url);

        showSuccess('✅ ABC notation downloaded successfully!');
        console.log('ABC download completed');

    } catch (error) {
        console.error('Download error:', error);
        showError('Download failed: ' + error.message);
    }
}

/**
 * Download MP4 file from ABC notation
 */
async function downloadWav() {
    console.log('Download WAV clicked');

    try {
        const notation = document.getElementById('musicCode').textContent;

        if (!notation || notation === '🎼 No music generated yet. Click "Generate Music" to start.') {
            showError('No music to download');
            return;
        }

        // Show loading state
        const btn = document.getElementById('downloadWavBtn');
        const originalText = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';

        try {
            // Call API to generate WAV
            const response = await fetch('/api/generate-mp4', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ notation: notation })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Audio generation failed');
            }

            // Get the audio file
            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;

            const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
            link.download = `music_${timestamp}.wav`;

            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            URL.revokeObjectURL(url);

            showSuccess('✅ WAV audio downloaded successfully!');
            console.log('WAV download completed');

        } finally {
            // Restore button state
            btn.disabled = false;
            btn.innerHTML = originalText;
        }

    } catch (error) {
        console.error('WAV download error:', error);
        showError('WAV download failed: ' + error.message);
    }
}

/**
 * Download MP4 file from ABC notation
 */
async function downloadWav() {
    console.log('Download WAV clicked');

    try {
        const notation = document.getElementById('musicCode').textContent;

        if (!notation || notation === '🎼 No music generated yet. Click "Generate Music" to start.') {
            showError('No music to download');
            return;
        }

        // Show loading state
        const btn = document.getElementById('downloadWavBtn');
        const originalText = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';

        try {
            // Call API to generate WAV
            const response = await fetch('/api/generate-mp4', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ notation: notation })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Audio generation failed');
            }

            // Get the audio file
            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;

            const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
            link.download = `music_${timestamp}.wav`;

            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            URL.revokeObjectURL(url);

            showSuccess('✅ WAV audio downloaded successfully!');
            console.log('WAV download completed');

        } finally {
            // Restore button state
            btn.disabled = false;
            btn.innerHTML = originalText;
        }

    } catch (error) {
        console.error('WAV download error:', error);
        showError('WAV download failed: ' + error.message);
    }
}

// Add event listeners for download buttons
document.addEventListener('DOMContentLoaded', function() {
    const downloadAbcBtn = document.getElementById('downloadAbcBtn');

    if (downloadAbcBtn) {
        downloadAbcBtn.addEventListener('click', downloadAbc);
    }
});
