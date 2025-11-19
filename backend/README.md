# FastAPI Backend with ML Engine

A complete Python FastAPI backend with SQLite database and ML model integration.

## 🎯 Quick Demo - Hardcoded Risk Users

For immediate testing, three demo users are available with **hardcoded risk levels**:

| Username      | Password   | Risk Level  | Color |
| ------------- | ---------- | ----------- | ----- |
| `green_user`  | `Test123!` | Low (15)    | 🟢    |
| `yellow_user` | `Test123!` | Medium (50) | 🟡    |
| `red_user`    | `Test123!` | High (85)   | 🔴    |

Create them with: `python create_demo_users.py`

Test at: http://localhost:8000/docs

## 👨‍💼 Default Admin Account

A default admin account is automatically created during deployment:

| Username | Password    | Purpose            |
| -------- | ----------- | ------------------ |
| `admin`  | `Admin123!` | Admin panel access |

⚠️ **Change this password after first login!**

Access admin panel at: `/admin` or use the separate admin-panel app

---

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

4. **Create demo users (optional but recommended):**

   ```bash
   python create_demo_users.py
   ```

   This creates three demo users with hardcoded risk levels:

   - `green_user` (Low Risk - 🟢)
   - `yellow_user` (Medium Risk - 🟡)
   - `red_user` (High Risk - 🔴)

   All use password: `Test123!`

5. **Run the application:**

   ```bash
   make dev
   ```

6. **Access the API:**
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

## Demo Users with Hardcoded Risk Levels

For demonstration purposes, the following users have **hardcoded risk scores** that override the ML model predictions:

| Username      | Risk Score | Risk Level | Color     | Behavior                              |
| ------------- | ---------- | ---------- | --------- | ------------------------------------- |
| `green_user`  | 15         | Low        | 🟢 GREEN  | Direct login allowed, no 2FA required |
| `yellow_user` | 50         | Medium     | 🟡 YELLOW | 2FA required for unknown devices      |
| `red_user`    | 85         | High       | 🔴 RED    | Always requires 2FA verification      |

### Risk Level Thresholds

- **🟢 LOW (0-29)**: Direct login allowed
- **🟡 MEDIUM (30-69)**: 2FA required for unknown devices
- **🔴 HIGH (70-100)**: Always requires 2FA

### Testing Demo Users

These users can be created with the default password `Test123!` using:

```bash
# Create demo users
python create_admin.py green_user user@example.com
python create_admin.py yellow_user user@example.com
python create_admin.py red_user user@example.com
```

Or use the quick script:

```bash
# Create all demo users at once
python create_demo_users.py

# Test the hardcoded users (requires backend running)
python test_demo_users.py
```

Or use the `/api/authenticate` endpoint with any of these usernames to see the hardcoded risk behavior. All other users will use the ML model for risk assessment.

**Note**: The hardcoded logic is in `main.py` in the `/api/authenticate` endpoint and does not modify the ML model itself.

## Environment Variables

See `.env.example` for all available configuration options.

## Development

- Python 3.11+
- FastAPI
- SQLite
- Scikit-learn for ML models

## GUI Setup for Presentation (Ubuntu Server)

### Install Minimal GUI Environment

If you want to run the Electron kiosk app on Ubuntu Server:

```bash
# Install minimal X server and Openbox window manager
sudo apt-get update
sudo apt-get install -y xorg openbox xinit

# Install Node
wget -qO- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
source ~/.bashrc
nvm install --lts


# Install Electron dependencies
sudo apt-get install -y \
  libgtk-3-0 \
  libnotify4 \
  libnss3 \
  libxss1 \
  libxtst6 \
  xdg-utils \
  libatspi2.0-0 \
  libdrm2 \
  libgbm1 \
  libxcb-dri3-0
```

### Start the Kiosk App

```bash
# Start X server with Openbox
startx

# In the X terminal that opens:
cd ~/code/ZT/kiosk
npm install
npm start
```

### Presentation Demo (No GUI Needed)

**Recommended:** Use the automated demo script instead of the GUI:

```bash
# Start backend
cd backend
./start_demo.sh

# Run automated demo (shows 3 risk levels with colors)
python presentation_demo.py

# Or use Swagger UI for interactive demo
# Open browser: http://localhost:8000/docs
```

**Demo Files:**

- `DEMO_QUICK_START.md` - Quick reference guide
- `PRESENTATION_TESTING_GUIDE.md` - Complete presentation guide
- `test_scenarios.json` - All 9 test cases with JSON
- `presentation_demo.py` - Automated color-coded demo
- `UAE_TEST_CASES.md` - 20 detailed UAE-specific test cases

## License

MIT
