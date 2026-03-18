# Example: AI/ML Project Adaptation

## Scenario

**Input:** A machine learning project with training and inference

**Project Structure:**
```
ml-project/
├── data/
│   ├── raw/                 # Raw datasets
│   ├── processed/           # Preprocessed data
│   └── external/            # External data
├── models/
│   ├── checkpoints/        # Model checkpoints
│   └── exports/            # Exported models
├── notebooks/
│   ├── exploration.ipynb
│   └── training.ipynb
├── src/
│   ├── data/               # Data processing
│   │   └── dataset.py
│   ├── models/             # Model definitions
│   │   └── transformer.py
│   ├── training/           # Training scripts
│   │   └── train.py
│   ├── inference/          # Inference
│   │   └── predict.py
│   └── evaluation/         # Evaluation
│       └── metrics.py
├── tests/
├── configs/
│   ├── default.yaml
│   └── experiment_01.yaml
├── requirements.txt
├── pyproject.toml
├── Dockerfile
└── README.md
```

---

## Running the Adapter

```bash
claude "Using prompts/universal-adapter.md, analyze this ML project"
```

---

## Generated Output

### ANALYSIS-MLProject.md

```markdown
# Project Analysis: ML Project

## Overview

Machine learning project using Transformers for text classification.
Includes data processing, model training, and inference pipeline.

## Technology Stack

| Component | Technology | Version | Notes |
|-----------|-----------|---------|-------|
| Language | Python | 3.10 | From pyproject.toml |
| ML Framework | PyTorch | 2.1 | Deep learning |
| Transformers | Hugging Face | 4.35 | Pre-trained models |
| Data | Pandas | 2.1 | Data processing |
| Notebooks | Jupyter | - | Exploration |
| Experiment Tracking | MLflow | 2.8 | Metrics logging |
| Training | Custom | - | Training scripts |
| Container | Docker | - | Reproducible env |

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Data Pipeline                       │
│  raw/ → dataset.py → processed/ → train.py       │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│              Training Pipeline                       │
│  train.py → checkpoints/ → model export            │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│             Inference Pipeline                       │
│  predict.py → trained model → predictions           │
└─────────────────────────────────────────────────────┘
```

## Key Components

| Component | Path | Purpose |
|-----------|------|---------|
| Data Loading | `src/data/dataset.py` | PyTorch Dataset |
| Model | `src/models/transformer.py` | Model architecture |
| Training | `src/training/train.py` | Training loop |
| Inference | `src/inference/predict.py` | Prediction API |
| Evaluation | `src/evaluation/metrics.py` | Metrics computation |
| Config | `configs/default.yaml` | Default hyperparameters |

## ML Pipeline

### 1. Data Preparation
```bash
# Process raw data
python -m src.data.dataset --input data/raw/ --output data/processed/
```

### 2. Training
```bash
# Train with default config
python -m src.training.train --config configs/default.yaml

# Train with experiment config
python -m src.training.train --config configs/experiment_01.yaml
```

### 3. Evaluation
```bash
# Evaluate on test set
python -m src.evaluation.metrics --model models/exports/best_model/
```

### 4. Inference
```bash
# Run predictions
python -m src.inference.predict --input data/test.json --model models/exports/best_model/
```

## Development Setup

### Prerequisites
- Python 3.10+
- CUDA 12.1 (for GPU)
- 16GB+ RAM

### Installation
```bash
# Create environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download model (if needed)
python -c "from transformers import AutoModel; AutoModel.from_pretrained('model-name')"
```

### Running Notebooks
```bash
# Start Jupyter
jupyter notebook notebooks/

# Or VS Code
code notebooks/exploration.ipynb
```

## Key Files

1. **`src/training/train.py`** — Main training script
2. **`src/models/transformer.py`** — Model architecture
3. **`src/data/dataset.py`** — Data loading
4. **`configs/default.yaml`** — Default configuration
5. **`notebooks/training.ipynb`** — Training experiments

## Common Gotchas

- **GPU:** Requires CUDA; will fallback to CPU (slow)
- **Memory:** Large models need 16GB+ RAM
- **Data:** Raw data must be preprocessed before training
- **Checkpoints:** Save frequently to avoid losing progress

## Experiment Tracking

| Tool | Purpose | Location |
|------|---------|----------|
| MLflow | Metrics tracking | `mlruns/` |
| Weights & Biases | (Optional) | Cloud |
| TensorBoard | (Optional) | `tensorboard/` |

## GPU Setup

```bash
# Check CUDA
python -c "import torch; print(torch.cuda.is_available())"

# Expected output: True
```

## Risks & Gaps

| Issue | Severity | Recommendation |
|-------|----------|----------------|
| No automated testing | High | Add unit tests for data transforms |
| No data versioning | Medium | Add DVC |
| Limited documentation | Medium | Document model architecture |
| No model registry | Medium | Add MLflow registry |

## Next Steps

1. **Setup:** Create venv and install requirements
2. **Data:** Run preprocessing: `python -m src.data.dataset`
3. **Train:** Start training: `python -m src.training.train`
4. **Experiment:** Open `notebooks/training.ipynb`
5. **Inference:** Test: `python -m src.inference.predict --input sample.json`
```

---

## Follow-up Questions

> "How do I train on my own data?"

> "What's the model architecture?"

> "How do I deploy for inference?"

---

## Model Architecture (if known)

From `src/models/transformer.py`:

- **Base Model:** [BERT / RoBERTa / etc.]
- **Task:** Text Classification
- **Classes:** [N classes]
- **Input:** [Max sequence length]

---

**See also:**
- [Python Example](python.md)
- [Clean Project Example](clean-project.md)
- [Microservices Example](microservices.md)
