/**
 * History and favorites management
 */

document.addEventListener('DOMContentLoaded', function() {
    const clearHistoryBtn = document.getElementById('clearHistoryBtn');
    const exportFavoritesBtn = document.getElementById('exportFavoritesBtn');

    clearHistoryBtn.addEventListener('click', clearNonFavorites);
    exportFavoritesBtn.addEventListener('click', exportFavorites);
});

/**
 * Clear non-favorite generations
 */
function clearNonFavorites() {
    if (confirm('Are you sure you want to clear all non-favorite generations?')) {
        const history = getHistory();
        const favorites = history.filter(item => item.isFavorite);
        saveHistory(favorites);
        updateHistoryDisplay();
        showSuccess('Non-favorite generations cleared');
    }
}

/**
 * Export favorites as JSON file
 */
function exportFavorites() {
    try {
        const history = getHistory();
        const favorites = history.filter(item => item.isFavorite);

        if (favorites.length === 0) {
            showError('No favorites to export');
            return;
        }

        // Create export data
        const exportData = {
            version: '1.0',
            exportDate: new Date().toISOString(),
            favorites: favorites
        };

        // Create blob
        const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });

        // Create download link
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;

        // Generate timestamped filename
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
        link.download = `favorites_${timestamp}.json`;

        // Trigger download
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        // Clean up
        URL.revokeObjectURL(url);

        showSuccess(`Exported ${favorites.length} favorite(s)`);

    } catch (error) {
        showError('Export failed: ' + error.message);
    }
}
