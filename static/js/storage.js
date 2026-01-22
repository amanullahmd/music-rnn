/**
 * Storage management utilities
 */

const STORAGE_KEYS = {
    THEME: 'theme',
    HISTORY: 'history',
    FAVORITES: 'favorites'
};

const STORAGE_LIMITS = {
    MAX_ITEMS: 10,
    MAX_STORAGE_SIZE: 5 * 1024 * 1024 // 5MB
};

/**
 * Check if storage is available
 */
function isStorageAvailable(type) {
    try {
        const storage = window[type];
        const test = '__storage_test__';
        storage.setItem(test, test);
        storage.removeItem(test);
        return true;
    } catch (e) {
        return false;
    }
}

/**
 * Get current storage size in bytes
 */
function getStorageSize() {
    let size = 0;
    for (let key in localStorage) {
        if (localStorage.hasOwnProperty(key)) {
            size += localStorage[key].length + key.length;
        }
    }
    return size;
}

/**
 * Check if storage quota is exceeded
 */
function isStorageQuotaExceeded() {
    return getStorageSize() > STORAGE_LIMITS.MAX_STORAGE_SIZE;
}

/**
 * Clean up storage by removing oldest non-favorite items
 */
function cleanupStorage() {
    if (!isStorageQuotaExceeded()) {
        return;
    }

    const history = getHistory();
    const favorites = history.filter(item => item.isFavorite);
    const nonFavorites = history.filter(item => !item.isFavorite);

    // Remove oldest non-favorites until under quota
    while (nonFavorites.length > 0 && isStorageQuotaExceeded()) {
        nonFavorites.shift();
    }

    // Combine and save
    const cleaned = [...nonFavorites, ...favorites];
    saveHistory(cleaned);
}

/**
 * Get storage statistics
 */
function getStorageStats() {
    const size = getStorageSize();
    const history = getHistory();
    const favorites = history.filter(item => item.isFavorite);

    return {
        totalSize: size,
        maxSize: STORAGE_LIMITS.MAX_STORAGE_SIZE,
        percentUsed: (size / STORAGE_LIMITS.MAX_STORAGE_SIZE) * 100,
        totalItems: history.length,
        favorites: favorites.length,
        nonFavorites: history.length - favorites.length
    };
}

/**
 * Export all data as JSON
 */
function exportAllData() {
    const history = getHistory();
    const theme = localStorage.getItem(STORAGE_KEYS.THEME) || 'light';

    return {
        version: '1.0',
        exportDate: new Date().toISOString(),
        theme: theme,
        history: history,
        stats: getStorageStats()
    };
}

/**
 * Import data from JSON
 */
function importData(data) {
    try {
        if (!data.history || !Array.isArray(data.history)) {
            throw new Error('Invalid data format');
        }

        // Merge with existing history
        const existing = getHistory();
        const merged = [...data.history, ...existing];

        // Remove duplicates by ID
        const unique = [];
        const seen = new Set();
        for (const item of merged) {
            if (!seen.has(item.id)) {
                unique.push(item);
                seen.add(item.id);
            }
        }

        // Keep only last 10
        const limited = unique.slice(0, STORAGE_LIMITS.MAX_ITEMS);

        saveHistory(limited);

        if (data.theme) {
            localStorage.setItem(STORAGE_KEYS.THEME, data.theme);
        }

        return true;
    } catch (error) {
        console.error('Import failed:', error);
        return false;
    }
}

/**
 * Clear all storage
 */
function clearAllStorage() {
    if (confirm('Are you sure you want to clear all data? This cannot be undone.')) {
        localStorage.clear();
        location.reload();
    }
}
