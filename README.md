# NetOps AI Pipeline

A comprehensive network operations AI pipeline for KPI anomaly detection and incident log summarization. Built with Python, FastAPI, and machine learning for telecom network monitoring.

## Features

- **KPI Anomaly Detection**: Uses Isolation Forest to detect anomalies in network KPIs (PRB Utilization, RRC Connections, Throughput, BLER)
- **Automated Visualization**: Generates PNG charts showing anomaly patterns across KPIs
- **Log Summarization**: GenAI-powered incident summarization from syslog data (optional with API keys)
- **RESTful API**: FastAPI service with endpoints for upload, analysis, and reporting
- **Batch Processing**: Standalone jobs for training and scoring
- **Production Ready**: Docker containerization, CI/CD, comprehensive testing

## Tech Stack

- **Backend**: Python 3.11, FastAPI, SQLModel + SQLite
- **ML**: scikit-learn (Isolation Forest), Pandas
- **Visualization**: Matplotlib
- **Testing**: pytest, Ruff, Black
- **Deployment**: Docker, GitHub Actions CI

## Quick Start

### Local Development

```bash
# Clone and setup
git clone <repo-url>
cd netops-ai-pipeline

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from storage import init_db; init_db()"

# Start the API server
uvicorn app:app --reload
```

### Test the API

```bash
# Upload sample KPI data for anomaly detection
curl -F "file=@data/sample_kpi.csv" -F "train_if_missing=true" \
  http://127.0.0.1:8000/upload

# Get anomaly report
curl http://127.0.0.1:8000/report/1

# Check health
curl http://127.0.0.1:8000/health
```

### Batch Processing

```bash
# Train anomaly detection model
python jobs/batch_train.py data/sample_kpi.csv

# Score new data
python jobs/batch_score.py data/sample_kpi.csv
```

## API Endpoints

- `POST /upload` - Upload KPI CSV for anomaly detection
- `GET /report/{upload_id}` - Get anomaly analysis report
- `POST /logs/summarize` - Summarize incident logs (GenAI optional)
- `GET /uploads` - List all uploads
- `GET /health` - Service health check

## Data Format

### KPI CSV Input
```csv
cell_id,timestamp,PRB_Util,RRC_Conn,Throughput_Mbps,BLER
CELL001,2024-01-01 10:00:00,45.2,150,25.5,0.02
```

### Expected Output
- Anomaly flags (-1 = anomaly, 1 = normal)
- Anomaly scores (lower = more anomalous)
- PNG visualization charts
- JSON reports with statistics

## Configuration

Copy `.env.example` to `.env` and configure:

```bash
# Optional: Enable GenAI log summarization
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Database (default: SQLite)
DATABASE_URL=sqlite:///netops.db
```

## Testing

```bash
# Run all tests
pytest -v

# Run linting
ruff check .
black --check .

# Test specific module
pytest tests/test_features.py -v
```

## Docker Deployment

```bash
# Build image
docker build -t netops-ai-pipeline .

# Run container
docker run -p 8000:8000 netops-ai-pipeline

# Access API at http://localhost:8000
```

## Architecture

```
netops-ai-pipeline/
├── app.py              # FastAPI application
├── storage.py          # Database models (SQLModel)
├── features.py         # KPI data processing
├── model.py            # ML model (Isolation Forest)
├── charts.py           # Visualization generation
├── summarize.py        # Log analysis & GenAI
├── ingest.py           # Data ingestion utilities
├── jobs/               # Batch processing scripts
│   ├── batch_train.py  # Model training job
│   └── batch_score.py  # Scoring job
├── tests/              # Unit tests
├── data/               # Sample data
└── .github/workflows/  # CI/CD pipeline
```

## ML Approach

**Anomaly Detection**: Uses Isolation Forest, an unsupervised algorithm that:
- Isolates anomalies by randomly selecting features and split values
- Anomalies require fewer splits to isolate (shorter paths in trees)
- No labeled data required - perfect for network KPI monitoring
- Robust to high-dimensional data and different scales

**Features**: PRB Utilization, RRC Connections, Throughput (Mbps), Block Error Rate (BLER)

## Production Considerations

- **Scalability**: Stateless API design, can be horizontally scaled
- **Monitoring**: Health checks, structured logging
- **Security**: CORS enabled, input validation, no secrets in code
- **CI/CD**: Automated testing, linting, Docker builds
- **Data Pipeline**: Batch jobs for offline processing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run `ruff check . && black . && pytest`
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

---

**Built for telecom network operations teams who need automated anomaly detection and intelligent incident analysis.**
