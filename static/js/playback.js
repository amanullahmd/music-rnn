/**
 * Audio playback functionality using abcjs and Tone.js
 */

let synth = null;
let isPlaying = false;
let currentNotes = [];
let currentNoteIndex = 0;

document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing playback...');
    
    const playBtn = document.getElementById('playBtn');
    const pauseBtn = document.getElementById('pauseBtn');
    const stopBtn = document.getElementById('stopBtn');
    const downloadBtn = document.getElementById('downloadBtn');

    // Initialize Tone.js synth
    try {
        synth = new Tone.PolySynth(Tone.Synth, {
            oscillator: { type: 'triangle' },
            envelope: {
                attack: 0.01,
                decay: 0.15,
                sustain: 0.1,
                release: 0.5
            }
        }).toDestination();
        console.log('Synth initialized');
    } catch (e) {
        console.error('Failed to initialize synth:', e);
    }

    if (playBtn) playBtn.addEventListener('click', playAudio);
    if (pauseBtn) pauseBtn.addEventListener('click', pauseAudio);
    if (stopBtn) stopBtn.addEventListener('click', stopAudio);
    if (downloadBtn) downloadBtn.addEventListener('click', downloadABC);
});

/**
 * Parse ABC notation properly - handles complex ABC format with chords
 */
function parseABCNotation(notation) {
    try {
        const notes = [];
        const lines = notation.split('\n');
        
        console.log('Parsing ABC notation...');
        console.log('Total lines:', lines.length);
        
        // Skip header lines and extract note lines
        for (const line of lines) {
            // Skip header lines (X:, T:, M:, L:, K:, R:, V:)
            if (line.match(/^[A-Z]:/)) {
                console.log('Skipping header:', line.substring(0, 40));
                continue;
            }
            if (line.trim() === '') continue;
            
            console.log('Parsing line:', line.substring(0, 80));
            
            // Parse each note in the line
            let i = 0;
            while (i < line.length) {
                const char = line[i];
                
                // Skip chord annotations like "Em" or "D"
                if (char === '"') {
                    i++;
                    while (i < line.length && line[i] !== '"') {
                        i++;
                    }
                    i++; // Skip closing quote
                    console.log('Skipped chord annotation');
                    continue;
                }
                
                // Skip bar lines, repeats, and other symbols
                if (/[|:\[\]]/.test(char)) {
                    i++;
                    continue;
                }
                
                // Skip spaces
                if (char === ' ') {
                    i++;
                    continue;
                }
                
                // Skip decorations like {, }, ~, etc.
                if (/[{}~!+.]/.test(char)) {
                    i++;
                    continue;
                }
                
                // Check for note (A-G or a-g)
                if (/[A-Ga-g]/.test(char)) {
                    let note = char;
                    i++;
                    
                    // Check for accidentals (^ for sharp, _ for flat, = for natural)
                    while (i < line.length && /[\^_=]/.test(line[i])) {
                        i++;
                    }
                    
                    // Check for octave changes (' for up, , for down)
                    while (i < line.length && /[',]/.test(line[i])) {
                        note += line[i];
                        i++;
                    }
                    
                    // Check for duration
                    let duration = 1;
                    if (i < line.length && /\d/.test(line[i])) {
                        duration = parseInt(line[i]);
                        i++;
                    }
                    if (i < line.length && line[i] === '/') {
                        i++;
                        if (i < line.length && /\d/.test(line[i])) {
                            duration = duration / parseInt(line[i]);
                            i++;
                        } else {
                            duration = duration / 2;
                        }
                    }
                    
                    const pitch = noteToMIDI(note);
                    notes.push({
                        pitch: pitch,
                        duration: duration,
                        rest: false
                    });
                    
                    console.log(`Note: ${note} -> MIDI ${pitch}, Duration ${duration}`);
                    
                } else if (char === 'z') {
                    // Rest
                    let duration = 1;
                    i++;
                    if (i < line.length && /\d/.test(line[i])) {
                        duration = parseInt(line[i]);
                        i++;
                    }
                    if (i < line.length && line[i] === '/') {
                        i++;
                        if (i < line.length && /\d/.test(line[i])) {
                            duration = duration / parseInt(line[i]);
                            i++;
                        } else {
                            duration = duration / 2;
                        }
                    }
                    notes.push({
                        pitch: 0,
                        duration: duration,
                        rest: true
                    });
                    console.log(`Rest: Duration ${duration}`);
                } else {
                    i++;
                }
            }
        }
        
        console.log('Total notes parsed:', notes.length);
        if (notes.length === 0) {
            console.warn('No notes parsed, using default notes');
            return getDefaultNotes();
        }
        return notes;
        
    } catch (error) {
        console.error('Error parsing ABC:', error);
        return getDefaultNotes();
    }
}

/**
 * Convert ABC note to MIDI pitch
 */
function noteToMIDI(note) {
    // MIDI note numbers for each note in Em key
    // Using standard octave numbering where middle C = 60
    const noteMap = {
        'D': 62,   // D3
        'E': 64,   // E3
        'F': 65,   // F3
        'G': 67,   // G3
        'A': 69,   // A3
        'B': 71,   // B3
        'c': 72,   // C4 (middle C)
        'd': 74,   // D4
        'e': 76,   // E4
        'f': 77,   // F4
        'g': 79,   // G4
        'a': 81,   // A4
        'b': 83    // B4
    };
    
    let baseNote = note.replace(/[',]/g, '');
    let midi = noteMap[baseNote] || 64;
    
    // Handle octave changes
    if (note.includes("'")) {
        const octaveUp = (note.match(/'/g) || []).length;
        midi += octaveUp * 12;
    }
    if (note.includes(',')) {
        const octaveDown = (note.match(/,/g) || []).length;
        midi -= octaveDown * 12;
    }
    
    // Clamp to valid MIDI range (0-127)
    midi = Math.max(0, Math.min(127, midi));
    
    return midi;
}

/**
 * Get default notes if parsing fails
 */
function getDefaultNotes() {
    return [
        { pitch: 64, duration: 1, rest: false },  // E
        { pitch: 67, duration: 1, rest: false },  // G
        { pitch: 69, duration: 1, rest: false },  // A
        { pitch: 71, duration: 1, rest: false },  // B
        { pitch: 76, duration: 1, rest: false },  // e
        { pitch: 79, duration: 1, rest: false },  // g
        { pitch: 81, duration: 1, rest: false },  // a
        { pitch: 83, duration: 1, rest: false }   // b
    ];
}

/**
 * Play audio from ABC notation
 */
async function playAudio() {
    console.log('Play button clicked');

    try {
        const notation = document.getElementById('musicCode').textContent;

        if (!notation || notation === '🎼 No music generated yet. Click "Generate Music" to start.') {
            showError('No music to play');
            return;
        }

        if (Tone.context.state === 'suspended') {
            await Tone.start();
        }

        isPlaying = true;
        updatePlaybackStatus('🎵 Playing...');
        document.getElementById('playBtn').disabled = true;
        document.getElementById('pauseBtn').disabled = false;
        document.getElementById('stopBtn').disabled = false;

        // Parse notation
        currentNotes = parseABCNotation(notation);
        console.log('Parsed notes:', currentNotes.length);

        if (currentNotes.length === 0) {
            showError('No valid notes found in notation');
            isPlaying = false;
            document.getElementById('playBtn').disabled = false;
            document.getElementById('pauseBtn').disabled = true;
            document.getElementById('stopBtn').disabled = true;
            return;
        }

        currentNoteIndex = 0;
        await playNotes();

    } catch (error) {
        console.error('Playback error:', error);
        showError('Playback failed: ' + error.message);
        isPlaying = false;
        document.getElementById('playBtn').disabled = false;
        document.getElementById('pauseBtn').disabled = true;
        document.getElementById('stopBtn').disabled = true;
    }
}

/**
 * Play a sequence of notes
 */
async function playNotes() {
    const baseDuration = 0.4; // Base note duration in seconds
    const totalNotes = currentNotes.length;

    console.log('Starting playback of', totalNotes, 'notes');

    while (currentNoteIndex < totalNotes && isPlaying) {
        const note = currentNotes[currentNoteIndex];
        const noteDuration = baseDuration * note.duration;

        if (!note.rest && note.pitch > 0) {
            // Convert MIDI note to frequency
            // Formula: frequency = 440 * 2^((MIDI - 69) / 12)
            const frequency = 440 * Math.pow(2, (note.pitch - 69) / 12);
            
            console.log(`Playing note: MIDI ${note.pitch}, Freq ${frequency.toFixed(2)}Hz, Duration ${noteDuration.toFixed(2)}s`);
            
            synth.triggerAttackRelease(frequency, noteDuration);
        } else if (note.rest) {
            console.log(`Rest: ${noteDuration.toFixed(2)}s`);
        }

        // Update progress
        const progress = Math.round(((currentNoteIndex + 1) / totalNotes) * 100);
        updatePlaybackStatus(`🎵 Playing... ${progress}%`);

        // Wait for note duration
        await new Promise(resolve => setTimeout(resolve, (noteDuration + 0.05) * 1000));

        currentNoteIndex++;
    }

    if (isPlaying) {
        isPlaying = false;
        updatePlaybackStatus('✅ Finished');
        document.getElementById('playBtn').disabled = false;
        document.getElementById('pauseBtn').disabled = true;
        document.getElementById('stopBtn').disabled = true;
    }
}

/**
 * Pause audio playback
 */
function pauseAudio() {
    console.log('Pause clicked');
    isPlaying = false;
    synth.triggerRelease();
    updatePlaybackStatus('⏸️ Paused');
    document.getElementById('playBtn').disabled = false;
    document.getElementById('pauseBtn').disabled = true;
    document.getElementById('stopBtn').disabled = false;
}

/**
 * Stop audio playback
 */
function stopAudio() {
    console.log('Stop clicked');
    isPlaying = false;
    synth.triggerRelease();
    currentNoteIndex = 0;
    updatePlaybackStatus('⏹️ Stopped');
    document.getElementById('playBtn').disabled = false;
    document.getElementById('pauseBtn').disabled = true;
    document.getElementById('stopBtn').disabled = true;
}

/**
 * Update playback status display
 */
function updatePlaybackStatus(status) {
    const statusEl = document.getElementById('playbackStatus');
    if (statusEl) {
        statusEl.innerHTML = '<i class="fas fa-info-circle"></i> ' + status;
    }
}

/**
 * Download ABC notation as file
 */
function downloadABC() {
    console.log('Download clicked');

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

        showSuccess('✅ Music downloaded successfully!');
        console.log('Download completed');

    } catch (error) {
        console.error('Download error:', error);
        showError('Download failed: ' + error.message);
    }
}

/**
 * Update playback status display
 */
function updatePlaybackStatus(status) {
    document.getElementById('playbackStatus').textContent = status;
}

/**
 * Download ABC notation as file
 */
function downloadABC() {
    try {
        const notation = document.getElementById('musicCode').textContent;

        if (!notation || notation === 'No music generated yet. Click "Generate Music" to start.') {
            showError('No music to download');
            return;
        }

        // Create blob
        const blob = new Blob([notation], { type: 'text/plain' });

        // Create download link
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;

        // Generate timestamped filename
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
        link.download = `music_${timestamp}.abc`;

        // Trigger download
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        // Clean up
        URL.revokeObjectURL(url);

        showSuccess('Music downloaded successfully!');

    } catch (error) {
        showError('Download failed: ' + error.message);
    }
}


/**
 * Update playback status display
 */
function updatePlaybackStatus(status) {
    document.getElementById('playbackStatus').textContent = status;
}

/**
 * Download ABC notation as file
 */
function downloadABC() {
    try {
        const notation = document.getElementById('musicCode').textContent;

        if (!notation || notation === 'No music generated yet. Click "Generate Music" to start.') {
            showError('No music to download');
            return;
        }

        // Create blob
        const blob = new Blob([notation], { type: 'text/plain' });

        // Create download link
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;

        // Generate timestamped filename
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
        link.download = `music_${timestamp}.abc`;

        // Trigger download
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        // Clean up
        URL.revokeObjectURL(url);

        showSuccess('Music downloaded successfully!');

    } catch (error) {
        showError('Download failed: ' + error.message);
    }
}
