# FastAPI Backend with ML Engine

A complete Python FastAPI backend with SQLite database and ML model integration.

## Features

- ✅ FastAPI REST API
- ✅ SQLite database with connection pooling
- ✅ ML model loading and prediction engine
- ✅ Docker and Docker Compose support
- ✅ Alpine-based Python image for small container size
- ✅ Health check endpoints
- ✅ CORS middleware
- ✅ JWT authentication ready
- ✅ Email integration (Resend)
- ✅ Makefile for common tasks

## Project Structure

```
backend/
├── main.py              # FastAPI application
├── database.py          # Database connection and queries
├── ml_engine.py         # ML model functions
├── models/              # Directory for .pkl model files
│   └── .gitkeep
├── requirements.txt     # Python dependencies
├── .env.example        # Environment variables template
├── .gitignore          # Git ignore rules
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Docker Compose configuration
├── Makefile            # Build automation
└── README.md           # This file
```

## Quick Start

### Option 1: Local Development

1. **Create virtual environment and install dependencies:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   make install
   ```

2. **Set up environment:**

   ```bash
   make env
   # Edit .env file with your configuration
   ```

3. **Initialize database:**

   ```bash
   make init-db
   ```

4. **Run the application:**

   ```bash
   make dev
   ```

5. **Access the API:**
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs
   - Health: http://localhost:8000/health

### Option 2: Docker

1. **Build and run with Docker Compose:**

   ```bash
   make docker-build
   make docker-up
   ```

2. **View logs:**

   ```bash
   make docker-logs
   ```

3. **Stop containers:**
   ```bash
   make docker-down
   ```

## Available Make Commands

```bash
make help              # Show all available commands
make install           # Install dependencies
make run               # Run the application
make dev               # Run with auto-reload
make clean             # Clean cache files
make docker-build      # Build Docker image
make docker-up         # Start containers
make docker-down       # Stop containers
make docker-logs       # View container logs
make docker-shell      # Open shell in container
make init-db           # Initialize database
make create-dummy-model # Create test ML model
make env               # Create .env from template
make setup             # Complete setup
```

## Adding ML Models

1. Place your `.pkl` model files in the `models/` directory
2. The models will be automatically loaded on application startup
3. Use the `predict()` function in `ml_engine.py` to make predictions

Example:

```python
from ml_engine import predict

result = predict("model_name", {"feature1": 1.0, "feature2": 2.0})
```

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /api/protected` - Example protected endpoint
- `GET /docs` - Interactive API documentation

## Environment Variables

See `.env.example` for all available configuration options.

## Development

- Python 3.11+
- FastAPI
- SQLite
- Scikit-learn for ML models

## License

MIT
