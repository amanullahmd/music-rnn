# Music Generation with RNNs

**Assignment 3** - Einführung in Deep Learning (WiSe 25/26)  
**Student:** Md Amanullah  
**Matrikelnummer:** 5466324

---

## Overview

This project implements a music generation system using Recurrent Neural Networks (RNNs). The model is trained on the IrishMAN dataset containing 214,122 Irish folk tunes in ABC notation format. It learns to generate new music by predicting the next character in a sequence, similar to how language models work but applied to music.

The system successfully generates syntactically valid ABC notation tunes that follow musical conventions learned from the training data.

---

## Quick Results

| Metric | Value |
|--------|-------|
| Top-1 Accuracy | 74.91% |
| Top-5 Accuracy | 95.40% |
| Validation Loss | 0.7729 |
| Training Loss | 0.7918 |
| Total Epochs | 10 |
| Model Parameters | 959,715 |

---

## Project Structure

```
.
├── app.py                              # Flask web application
├── requirements.txt                    # Python dependencies
├── best_model.pt                       # Trained RNN model weights
├── .env.example                        # Environment configuration template
├── .gitignore                          # Git ignore rules
├── api/
│   ├── __init__.py
│   └── routes.py                       # API endpoints
├── services/
│   ├── __init__.py
│   ├── generator.py                    # Music generation logic
│   ├── model_loader.py                 # Model loading utilities
│   ├── audio_converter.py              # ABC to audio conversion
│   ├── validator.py                    # Input validation
│   └── request_handler.py              # Request processing
├── config/
│   ├── __init__.py
│   └── logging_config.py               # Logging configuration
├── templates/
│   ├── base.html                       # Base template
│   └── index.html                      # Main UI
├── static/
│   ├── css/
│   │   └── style.css                   # Styling with gradients
│   └── js/
│       ├── app.js                      # Main app logic
│       ├── generation.js               # Generation handler
│       ├── playback.js                 # Playback utilities
│       ├── playback-abcjs.js           # ABC.js integration
│       ├── storage.js                  # Local storage
│       └── history.js                  # Generation history
├── tests/
│   ├── __init__.py
│   ├── test_generation.py              # Generation tests
│   ├── test_validator.py               # Validator tests
│   ├── test_frontend.py                # Frontend tests
│   └── test_concurrent.py              # Concurrency tests
├── .kiro/specs/
│   └── music-generation-gui/
│       ├── requirements.md             # Feature requirements
│       ├── design.md                   # Design document
│       └── tasks.md                    # Implementation tasks
└── README.md                           # This file
```

---

## Features

### Music Generation
- Generate Irish folk music in ABC notation format
- Temperature control for creativity vs. determinism
- Configurable sequence length
- Uses trained RNN model with 959,715 parameters

### Web Interface
- Professional gradient-based UI design
- Real-time generation with status updates
- ABC notation display and download
- Generation history tracking
- Responsive design

### Model
- 2-Layer LSTM with 256 hidden units
- 128-dimensional embeddings
- Trained on 214,122 Irish folk tunes
- 95.4% top-5 accuracy

---

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

1. Clone the repository:
```bash
git clone https://github.com/amanullahmd/music-rnn.git
cd music-rnn
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env if needed (default settings work fine)
```

---

## Running the Application

### Development Server
```bash
python app.py
```

The application will be available at `http://localhost:5000`

### Running Tests
```bash
pytest tests/
```

All 63 tests should pass.

---

## Usage

1. Open the web interface at `http://localhost:5000`
2. Adjust temperature slider (0.5 = deterministic, 1.0 = creative)
3. Set desired sequence length
4. Click "Generate Music"
5. View generated ABC notation
6. Download ABC notation or play online at [abc.rectanglered.com](https://abc.rectanglered.com/)

---

## Model Architecture

```
Input (ABC notation)
    ↓
Embedding Layer (128D)
    ↓
2-Layer LSTM (256 hidden units each)
    ↓
Dropout (0.3)
    ↓
Output Layer (99 vocabulary)
    ↓
Generated Music (ABC notation)
```

### Architecture Details

| Component | Configuration |
|-----------|----------------|
| Type | 2-Layer LSTM |
| Embedding Dimension | 128 |
| Hidden Units | 256 per layer |
| Dropout Rate | 0.3 |
| Vocabulary Size | 99 tokens |
| Total Parameters | 959,715 |

---

## Training Configuration

| Parameter | Value |
|-----------|-------|
| Optimizer | Adam |
| Learning Rate | 0.001 |
| Batch Size | 32 |
| Gradient Clipping | max norm 1.0 |
| Loss Function | CrossEntropyLoss |
| LR Scheduler | ReduceLROnPlateau |
| Training Device | CUDA (GPU) |
| Training Time | ~90 minutes |
| Total Epochs | 10 |

---

## Dataset

| Aspect | Value |
|--------|-------|
| Training Samples | 214,122 tunes |
| Validation Samples | 2,162 tunes |
| Format | ABC notation |
| Vocabulary Size | 99 unique characters |
| Sequence Length | 100-1000+ characters |

---

## Generated Music Example

```
X:1
T:Generated Tune
M:4/4
L:1/8
K:G
B2 | c3 A F2 D2 | G3 A B2 AG | FGAB cAFA |
G2 D2 D2 GA | B3 A G2 A2 | FAce d3 e |
fgfe d2 c2 | B4 B2 d2 | cBAB ABAG |
FG A2 A2 d2 | cBAG F2 G2 | A2 F2 G4 |]
```

The generated tune demonstrates valid ABC notation syntax with proper headers (X:, T:, M:, L:, K:), logical note sequences, and realistic musical patterns.

---

## API Endpoints

### Generate Music
```
POST /api/generate
Content-Type: application/json

{
  "length": 200,
  "temperature": 0.8
}

Response:
{
  "abc_notation": "X:1\nT:Generated...",
  "status": "success"
}
```

### Generate MP4/WAV
```
POST /api/generate-mp4
Content-Type: application/json

{
  "abc_notation": "X:1\nT:Generated...",
  "format": "wav"
}

Response: Binary audio file
```

---

## Key Insights

- RNNs effectively learn sequential patterns in music
- LSTM cells handle long sequences better than vanilla RNNs
- Character-level modeling works well for structured formats like ABC notation
- GPU acceleration is essential for large-scale training
- Proper regularization prevents overfitting while maintaining generalization
- Temperature control provides intuitive creativity adjustment

---

## Challenges & Solutions

### 1. GPU Training Power Constraints
**Challenge:** Training 214K samples for 10 epochs required significant GPU memory and ~90 minutes of computation.  
**Solution:** Optimized batch processing with dynamic padding, efficient data loading, and gradient accumulation strategies.

### 2. Gradient Instability
**Challenge:** RNNs suffer from vanishing/exploding gradients with long sequences.  
**Solution:** Applied gradient clipping (max norm 1.0) and used LSTM cells for better stability.

### 3. Variable-Length Sequences
**Challenge:** ABC notation files range from 100-1000+ characters.  
**Solution:** Implemented dynamic padding in batches to handle variable lengths efficiently.

### 4. Overfitting Risk
**Challenge:** Large model on sequential data prone to overfitting.  
**Solution:** Applied dropout (0.3), learning rate scheduling (ReduceLROnPlateau), and validation monitoring.

### 5. ABC Notation Validation
**Challenge:** Generated sequences must be valid ABC notation.  
**Solution:** Implemented strict validation with proper headers, bar lines, and chord annotations.

---

## Dependencies

- **Flask** - Web framework
- **PyTorch** - Deep learning framework
- **NumPy** - Numerical computing
- **SciPy** - Audio processing
- **python-dotenv** - Environment configuration
- **pytest** - Testing framework
- **hypothesis** - Property-based testing

---

## Testing

The project includes comprehensive test coverage:

- **Unit Tests** - Individual component testing
- **Integration Tests** - End-to-end workflow testing
- **Property-Based Tests** - Hypothesis-based correctness verification
- **Frontend Tests** - UI interaction testing
- **Concurrency Tests** - Multi-threaded request handling

Run all tests:
```bash
pytest tests/ -v
```

---

## Deployment

### Environment Variables
Create `.env` file with:
```
MODEL_PATH=best_model.pt
PORT=5000
DEBUG=False
LOG_LEVEL=INFO
```

### Production Server
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## References

- **Dataset:** IrishMAN (Irish Music Annotation Network) - [Hugging Face](https://huggingface.co/datasets/sander-wood/irishman)
- **Framework:** PyTorch - [pytorch.org](https://pytorch.org/)
- **Music Format:** ABC Notation - [abc.rectanglered.com](https://abc.rectanglered.com/)
- **Assignment:** Einführung in Deep Learning (WiSe 25/26)

---

## License

This project is part of the Deep Learning course assignment at THM.

---

**Last Updated:** January 22, 2026
