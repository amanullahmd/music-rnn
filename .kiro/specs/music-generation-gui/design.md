# Design Document: Music Generation GUI

## Overview

A full-stack web application consisting of a React-based frontend and a Flask backend that provides a professional interface for generating Irish folk music using a trained RNN model. The system enables users to generate music with customizable parameters, visualize and play the output, and manage their generation history with local storage persistence.

**Technology Stack**:
- Frontend: React 18, TypeScript, Tailwind CSS, Vite
- Backend: Flask, PyTorch
- Audio Processing: Tone.js (ABC to audio conversion)
- Storage: Browser LocalStorage, JSON export
- Deployment: Docker, environment-based configuration

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Web Browser                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              React Frontend (SPA)                    │   │
│  │  ┌─────────────┐  ┌──────────────┐  ┌────────────┐  │   │
│  │  │ Generation  │  │ Music Display│  │  History   │  │   │
│  │  │ Interface   │  │  & Playback  │  │  Manager   │  │   │
│  │  └─────────────┘  └──────────────┘  └────────────┘  │   │
│  │         │                │                │           │   │
│  │         └────────────────┼────────────────┘           │   │
│  │                          │                            │   │
│  │              ┌───────────▼──────────┐                │   │
│  │              │  API Client Service  │                │   │
│  │              └───────────┬──────────┘                │   │
│  └──────────────────────────┼──────────────────────────┘   │
│                             │ HTTP/JSON                     │
└─────────────────────────────┼──────────────────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │  Flask Backend     │
                    │  ┌──────────────┐  │
                    │  │ API Routes   │  │
                    │  ├──────────────┤  │
                    │  │ Model Loader │  │
                    │  ├──────────────┤  │
                    │  │ Generator    │  │
                    │  ├──────────────┤  │
                    │  │ Validator    │  │
                    │  └──────────────┘  │
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │  RNN Model         │
                    │  (best_model.pt)   │
                    └────────────────────┘
```

## Components and Interfaces

### Frontend Components

**GenerationInterface**
- Manages seed text input, temperature slider, sequence length slider
- Handles form submission and validation
- Displays loading state during generation
- Props: `onGenerate(params)`, `isLoading`, `error`

**MusicDisplay**
- Renders ABC notation with syntax highlighting
- Shows formatted, read-only text area
- Props: `notation`, `isLoading`

**MusicPlayback**
- Manages audio playback controls (play, pause, stop)
- Handles ABC to audio conversion
- Provides download functionality
- Props: `notation`, `onError`

**HistoryPanel**
- Lists recent 10 generations with timestamps
- Allows loading previous generations
- Manages favorites (save/remove)
- Props: `generations`, `onLoadGeneration`, `onSaveFavorite`

**ThemeToggle**
- Switches between dark and light themes
- Persists preference to localStorage
- Props: `onThemeChange`

### Backend API Endpoints

**POST /api/generate**
- Request body: `{ seed: string, temperature: number, length: number }`
- Response: `{ notation: string, timestamp: string, parameters: object }`
- Validates input parameters
- Returns 400 for invalid input, 500 for generation errors

**GET /api/health**
- Response: `{ status: "ok", model_loaded: boolean }`
- Used for health checks and model status

### Services

**APIClient**
- Handles all HTTP communication with backend
- Manages request/response serialization
- Implements error handling and retry logic

**StorageManager**
- Manages localStorage operations
- Persists theme preference, favorites, history
- Handles storage quota management

**AudioConverter**
- Converts ABC notation to audio using Tone.js
- Manages playback state
- Handles audio context initialization

## Data Models

### Generation Object
```typescript
interface Generation {
  id: string;                    // UUID
  notation: string;              // ABC notation text
  seed: string;                  // Input seed text
  temperature: number;           // 0.1 to 2.0
  length: number;                // 50 to 500
  timestamp: string;             // ISO 8601 datetime
  isFavorite: boolean;           // User-marked favorite
}
```

### API Request/Response
```typescript
interface GenerationRequest {
  seed: string;                  // Optional, uses default if empty
  temperature: number;           // 0.1 to 2.0
  length: number;                // 50 to 500
}

interface GenerationResponse {
  notation: string;              // Generated ABC notation
  timestamp: string;             // Server timestamp
  parameters: GenerationRequest; // Echo of input parameters
}
```

### Storage Schema
```typescript
interface StorageData {
  theme: 'light' | 'dark';
  favorites: Generation[];
  history: Generation[];
}
```

## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.


### Property 1: Default Seed Handling
*For any* generation request with an empty seed, the backend SHALL use a default seed value and produce valid ABC notation output.
**Validates: Requirements 1.2**

### Property 2: Temperature Display Accuracy
*For any* temperature value between 0.1 and 2.0, the UI SHALL display the exact value adjusted on the slider.
**Validates: Requirements 1.3**

### Property 3: Sequence Length Display Accuracy
*For any* sequence length value between 50 and 500, the UI SHALL display the exact value adjusted on the slider.
**Validates: Requirements 1.4**

### Property 4: Generation Request Parameters
*For any* generation request, the frontend SHALL send all parameters (seed, temperature, length) to the backend in the correct format.
**Validates: Requirements 1.5**

### Property 5: Loading State During Generation
*For any* in-flight generation request, the UI SHALL display a loading indicator and the Generate button SHALL be disabled.
**Validates: Requirements 1.6**

### Property 6: Successful Generation Response Handling
*For any* successful generation response, the UI SHALL display the generated ABC notation and re-enable the Generate button.
**Validates: Requirements 1.7**

### Property 7: Error Handling and Recovery
*For any* failed generation request, the UI SHALL display an error message and re-enable the Generate button.
**Validates: Requirements 1.8**

### Property 8: ABC Notation Display Completeness
*For any* generated ABC notation, the Music_Display SHALL render the complete text without truncation or modification.
**Validates: Requirements 2.2**

### Property 9: Audio Playback Initiation
*For any* valid ABC notation, clicking the Play button SHALL initiate audio playback.
**Validates: Requirements 2.3**

### Property 10: Playback UI State
*For any* active audio playback, the UI SHALL display a pause button and current playback position.
**Validates: Requirements 2.4**

### Property 11: File Download Functionality
*For any* generated ABC notation, clicking Download SHALL create a file with the notation content and a timestamped filename.
**Validates: Requirements 2.5**

### Property 12: Audio Conversion Error Handling
*For any* invalid ABC notation, the audio converter SHALL display an error message and disable the Play button.
**Validates: Requirements 2.6**

### Property 13: Generation History Addition
*For any* successful generation, the History_Manager SHALL add it to the recent generations list.
**Validates: Requirements 3.1**

### Property 14: History Display Limit
*For any* history view, the History_Manager SHALL display at most 10 generations with timestamps and parameters.
**Validates: Requirements 3.2**

### Property 15: History Item Loading
*For any* history item, clicking it SHALL load that generation into the Music_Display.
**Validates: Requirements 3.3**

### Property 16: Favorite Persistence
*For any* generation marked as favorite, the History_Manager SHALL persist it to localStorage and mark it as favorite.
**Validates: Requirements 3.4**

### Property 17: Selective History Clearing
*For any* Clear History action, the History_Manager SHALL remove all non-favorite generations while preserving favorites.
**Validates: Requirements 3.5**

### Property 18: Favorites Export Format
*For any* Export Favorites action, the system SHALL create a downloadable JSON file containing all saved favorite generations with metadata.
**Validates: Requirements 3.6**

### Property 19: Theme Toggle Persistence
*For any* theme change, the UI_Framework SHALL switch themes and persist the preference to localStorage.
**Validates: Requirements 4.2**

### Property 20: Responsive Layout Adaptation
*For any* viewport size change, the UI_Framework SHALL adapt the layout to fit the screen dimensions.
**Validates: Requirements 4.3**

### Property 21: Tooltip Display
*For any* parameter hover action, the UI_Framework SHALL display a tooltip with the parameter's purpose and range.
**Validates: Requirements 4.4**

### Property 22: Visual Feedback on Actions
*For any* user action, the UI_Framework SHALL provide visual feedback through button states, animations, or status messages.
**Validates: Requirements 4.5**

### Property 23: Error Message Display
*For any* application error, the UI_Framework SHALL display a user-friendly error message with recovery options.
**Validates: Requirements 4.6**

### Property 24: Backend Generation Functionality
*For any* valid generation request with parameters within range, the backend SHALL generate and return valid ABC notation.
**Validates: Requirements 5.1**

### Property 25: Input Parameter Validation
*For any* generation request, the backend SHALL validate that seed length, temperature (0.1-2.0), and sequence length (50-500) are within acceptable ranges.
**Validates: Requirements 5.2**

### Property 26: Invalid Parameter Error Response
*For any* request with invalid parameters, the backend SHALL return a 400 error with a descriptive error message.
**Validates: Requirements 5.3**

### Property 27: JSON Response Format
*For any* successful generation, the backend SHALL return a valid JSON response containing the notation field.
**Validates: Requirements 5.4**

### Property 28: Concurrent Request Safety
*For any* concurrent generation requests, the backend SHALL process them independently without data corruption or interference.
**Validates: Requirements 5.5**

### Property 29: Generation Error Response
*For any* error during generation, the backend SHALL return a 500 error with error details and context.
**Validates: Requirements 5.6**

### Property 30: Theme Preference Persistence
*For any* theme preference change, the Storage_Manager SHALL persist it to localStorage.
**Validates: Requirements 6.1**

### Property 31: Favorite Metadata Persistence
*For any* favorite generation, the Storage_Manager SHALL persist it to localStorage with complete metadata (timestamp, parameters).
**Validates: Requirements 6.2**

### Property 32: Data Restoration on Reload
*For any* application reload, the Storage_Manager SHALL restore the theme preference and load all saved favorites.
**Validates: Requirements 6.3**

### Property 33: Storage Quota Management
*For any* localStorage capacity limit, the Storage_Manager SHALL remove oldest non-favorite generations to make space for new data.
**Validates: Requirements 6.4**

### Property 34: Export File Format
*For any* Export Favorites action, the exported JSON file SHALL contain all saved generations with complete metadata.
**Validates: Requirements 6.5**

### Property 35: Environment Variable Configuration
*For any* application startup, the Deployment_System SHALL read and apply configuration from environment variables (model path, port, debug mode).
**Validates: Requirements 7.2**

### Property 36: Request and Error Logging
*For any* request or error, the Deployment_System SHALL log it to a file or logging service.
**Validates: Requirements 7.3**

### Property 37: Error Context Capture
*For any* application error, the Deployment_System SHALL capture stack traces and error context for debugging.
**Validates: Requirements 7.4**

### Property 38: Static and API Server Integration
*For any* deployment, the Deployment_System SHALL serve both static frontend files and API endpoints from the same server.
**Validates: Requirements 7.5**

## Error Handling

**Frontend Error Handling**:
- Network errors: Display "Connection failed. Please check your internet connection."
- Generation errors: Display backend error message with retry option
- Audio conversion errors: Display "Could not convert music to audio. Try a different generation."
- Storage errors: Gracefully degrade, warn user that favorites may not persist

**Backend Error Handling**:
- Invalid parameters: Return 400 with specific validation error messages
- Model loading errors: Return 500 with "Model failed to load"
- Generation timeout: Return 500 with "Generation took too long"
- Concurrent request limits: Queue requests or return 429 "Too many requests"

**Logging Strategy**:
- Log all generation requests with parameters and timestamp
- Log all errors with stack traces and context
- Log performance metrics (generation time, model load time)
- Separate logs for development and production

## Testing Strategy

### Unit Testing Approach
- Test individual components in isolation (GenerationInterface, MusicDisplay, etc.)
- Test API client request/response handling
- Test storage manager operations
- Test input validation logic
- Test error handling paths
- Focus on specific examples and edge cases

### Property-Based Testing Approach
- Use Hypothesis (Python) for backend property tests
- Use fast-check (TypeScript) for frontend property tests
- Minimum 100 iterations per property test
- Each property test validates one correctness property from the design
- Tag each test with: **Feature: music-generation-gui, Property {number}: {property_text}**

### Test Coverage
- Backend: Validation, generation, error handling, concurrency
- Frontend: State management, API communication, storage, UI rendering
- Integration: End-to-end generation flow, history management, favorites

### Example Property Test (Backend)
```python
# Feature: music-generation-gui, Property 24: Backend Generation Functionality
@given(
    seed=st.text(min_size=0, max_size=50),
    temperature=st.floats(min_value=0.1, max_value=2.0),
    length=st.integers(min_value=50, max_value=500)
)
def test_generation_produces_valid_abc(seed, temperature, length):
    """For any valid generation request, backend SHALL generate valid ABC notation"""
    response = client.post('/api/generate', json={
        'seed': seed,
        'temperature': temperature,
        'length': length
    })
    assert response.status_code == 200
    data = response.json()
    assert 'notation' in data
    assert isinstance(data['notation'], str)
    assert len(data['notation']) > 0
```

### Example Property Test (Frontend)
```typescript
// Feature: music-generation-gui, Property 2: Temperature Display Accuracy
fc.assert(
  fc.property(
    fc.floats({ min: 0.1, max: 2.0, noNaN: true }),
    (temperature) => {
      const { getByDisplayValue } = render(<TemperatureSlider value={temperature} />);
      expect(getByDisplayValue(temperature.toFixed(1))).toBeInTheDocument();
    }
  ),
  { numRuns: 100 }
);
```

