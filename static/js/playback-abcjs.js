/**
 * Professional ABC notation playback using abcjs
 * Renders sheet music and provides audio playback
 */

let synth = null;
let isPlaying = false;
let currentNotes = [];
let currentNoteIndex = 0;
let abcPlayer = null;

document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing abcjs playback...');
    
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
 * Render ABC notation as sheet music using abcjs
 */
function renderSheetMusic(notation) {
    try {
        const sheetMusicDiv = document.getElementById('sheetMusic');
        
        if (!sheetMusicDiv) {
            console.error('Sheet music container not found');
            return;
        }
        
        // Clear previous rendering
        sheetMusicDiv.innerHTML = '';
        
        // Validate notation
        if (!notation || notation.trim() === '' || notation.includes('No music generated')) {
            sheetMusicDiv.innerHTML = '<p class="text-muted text-center py-5"><i class="fas fa-music"></i> Sheet music will appear here</p>';
            return;
        }
        
        console.log('Rendering ABC notation:', notation.substring(0, 100));
        
        // Render using abcjs
        const options = {
            responsive: 'resize',
            staffwidth: 800,
            scale: 1.5,
            paddingtop: 15,
            paddingbottom: 15,
            paddingleft: 15,
            paddingright: 15
        };
        
        try {
            // Use abcjs to render the notation
            const visualObj = ABCJS.renderAbc('sheetMusic', notation, options);
            
            if (!visualObj || visualObj.length === 0) {
                console.warn('abcjs returned empty visualization');
                sheetMusicDiv.innerHTML = '<p class="text-warning text-center py-5"><i class="fas fa-exclamation-triangle"></i> Could not render sheet music</p>';
                return;
            }
            
            console.log('Sheet music rendered successfully with', visualObj.length, 'tune(s)');
            
            // Store for playback
            abcPlayer = visualObj;
            return visualObj;
        } catch (e) {
            console.error('abcjs rendering error:', e);
            console.error('Notation that failed:', notation);
            sheetMusicDiv.innerHTML = '<p class="text-danger text-center py-5"><i class="fas fa-exclamation-circle"></i> Error rendering sheet music: ' + e.message + '</p>';
            return null;
        }
        
    } catch (error) {
        console.error('Error rendering sheet music:', error);
        const sheetMusicDiv = document.getElementById('sheetMusic');
        if (sheetMusicDiv) {
            sheetMusicDiv.innerHTML = '<p class="text-danger text-center py-5"><i class="fas fa-exclamation-circle"></i> Error: ' + error.message + '</p>';
        }
        return null;
    }
}

/**
 * Parse ABC notation to extract notes for playback
 */
function parseABCNotation(notation) {
    try {
        const notes = [];
        const lines = notation.split('\n');
        
        console.log('Parsing ABC notation...');
        
        // Skip header lines and extract note lines
        for (const line of lines) {
            // Skip header lines
            if (line.match(/^[A-Z]:/)) continue;
            if (line.trim() === '') continue;
            
            // Parse each note in the line
            let i = 0;
            while (i < line.length) {
                const char = line[i];
                
                // Skip chord annotations
                if (char === '"') {
                    i++;
                    while (i < line.length && line[i] !== '"') {
                        i++;
                    }
                    i++;
                    continue;
                }
                
                // Skip bar lines and repeats
                if (/[|:\[\]]/.test(char)) {
                    i++;
                    continue;
                }
                
                // Skip spaces
                if (char === ' ') {
                    i++;
                    continue;
                }
                
                // Skip decorations
                if (/[{}~!+.]/.test(char)) {
                    i++;
                    continue;
                }
                
                // Parse note
                if (/[A-Ga-g]/.test(char)) {
                    let note = char;
                    i++;
                    
                    // Skip accidentals
                    while (i < line.length && /[\^_=]/.test(line[i])) {
                        i++;
                    }
                    
                    // Handle octave changes
                    while (i < line.length && /[',]/.test(line[i])) {
                        note += line[i];
                        i++;
                    }
                    
                    // Parse duration
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
                } else {
                    i++;
                }
            }
        }
        
        console.log('Total notes parsed:', notes.length);
        return notes.length > 0 ? notes : getDefaultNotes();
        
    } catch (error) {
        console.error('Error parsing ABC:', error);
        return getDefaultNotes();
    }
}

/**
 * Convert ABC note to MIDI pitch
 */
function noteToMIDI(note) {
    const noteMap = {
        'D': 62, 'E': 64, 'F': 65, 'G': 67, 'A': 69, 'B': 71,
        'c': 72, 'd': 74, 'e': 76, 'f': 77, 'g': 79, 'a': 81, 'b': 83
    };
    
    let baseNote = note.replace(/[',]/g, '');
    let midi = noteMap[baseNote] || 64;
    
    if (note.includes("'")) {
        const octaveUp = (note.match(/'/g) || []).length;
        midi += octaveUp * 12;
    }
    if (note.includes(',')) {
        const octaveDown = (note.match(/,/g) || []).length;
        midi -= octaveDown * 12;
    }
    
    midi = Math.max(0, Math.min(127, midi));
    return midi;
}

/**
 * Get default notes if parsing fails
 */
function getDefaultNotes() {
    return [
        { pitch: 64, duration: 1, rest: false },
        { pitch: 67, duration: 1, rest: false },
        { pitch: 69, duration: 1, rest: false },
        { pitch: 71, duration: 1, rest: false },
        { pitch: 76, duration: 1, rest: false },
        { pitch: 79, duration: 1, rest: false },
        { pitch: 81, duration: 1, rest: false },
        { pitch: 83, duration: 1, rest: false }
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
    const baseDuration = 0.4;
    const totalNotes = currentNotes.length;

    console.log('Starting playback of', totalNotes, 'notes');

    while (currentNoteIndex < totalNotes && isPlaying) {
        const note = currentNotes[currentNoteIndex];
        const noteDuration = baseDuration * note.duration;

        if (!note.rest && note.pitch > 0) {
            const frequency = 440 * Math.pow(2, (note.pitch - 69) / 12);
            console.log(`Playing: MIDI ${note.pitch}, Freq ${frequency.toFixed(2)}Hz`);
            synth.triggerAttackRelease(frequency, noteDuration);
        }

        const progress = Math.round(((currentNoteIndex + 1) / totalNotes) * 100);
        updatePlaybackStatus(`🎵 Playing... ${progress}%`);

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
