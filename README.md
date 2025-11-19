# Zero Trust Authentication System

A comprehensive Zero Trust security solution with ML-powered risk assessment, adaptive authentication, and multi-platform support. Built for enterprise environments requiring high-security authentication with user-friendly deployment.

## 🏗️ System Architecture

This project consists of three main components:

### 1. **Backend** (Python/FastAPI)
REST API server with machine learning-based risk assessment engine for intelligent authentication decisions.

### 2. **Admin Panel** (React/TypeScript)
Web-based administrative dashboard for user management, security analytics, and system monitoring.

### 3. **Kiosk Application** (React/Electron)
Secure kiosk interface for physical deployment locations with full lockdown capabilities.

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** (for backend)
- **Node.js 18+** and npm (for frontend applications)
- **Docker** (optional, for containerized deployment)
- **Git** (for version control)

### 1️⃣ Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your RESEND_API_KEY for OTP emails

# Initialize database and create admin user
python create_default_admin.py

# Start the server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Backend will be running at:** `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/api/health`

**Default Admin Credentials:**
- Username: `admin`
- Password: `Admin123!`

---

### 2️⃣ Admin Panel Setup

```bash
cd admin-panel

# Install dependencies
npm install

# Create .env file (optional)
cp .env.example .env

# Start development server
npm run dev
```

**Admin Panel will be running at:** `http://localhost:5174`

---

### 3️⃣ Kiosk Application Setup

#### Web Version (Development)
```bash
cd kiosk

# Install dependencies
npm install

# Create .env file
cp .env.example .env
# Set VITE_API_BASE_URL=http://localhost:8000

# Start development server
npm run dev
```

**Kiosk will be running at:** `http://localhost:5173`

#### Electron Desktop Version
```bash
cd kiosk/electron

# Install Electron dependencies
npm install

# Start Electron app (loads http://localhost:5173)
npm start
```

---

## 🐳 Docker Deployment

For production deployment using Docker:

```bash
cd backend

# Build and start with docker-compose
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop services
docker-compose down
```

The backend will be available at `http://localhost:8000` with persistent database storage.

---

## 📋 Features

### 🔒 Zero Trust Security Model
- **No Implicit Trust**: Every login attempt is evaluated
- **Continuous Verification**: Device fingerprinting and behavior analysis
- **Adaptive Authentication**: Risk-based access control

### 🤖 ML-Powered Risk Assessment
- **Hybrid Engine**: Combines machine learning with rule-based intelligence
- **UAE-Focused**: Optimized for UAE region with local threat intelligence
- **Risk Scoring**: 0-100 scale with three threat levels:
  - **Low (0-29)**: Direct access granted
  - **Medium (30-69)**: 2FA required for unknown devices
  - **High (70-100)**: Always requires 2FA

### 📊 Risk Factors Analyzed
- IP geolocation and ASN reputation
- Device fingerprinting (browser, OS, screen resolution)
- Login time patterns (business hours vs off-hours)
- Historical behavior
- Failed login attempts

### 🔐 Two-Factor Authentication (2FA)
- Email-based OTP delivery via Resend API
- Time-limited codes (5 minutes expiry)
- Device trust management

### 👥 User Management
- Role-based access control (Admin/User)
- Bulk user operations
- Login attempt audit logs
- Real-time security analytics

### 🖥️ Kiosk Security Features
- Full-screen lockdown mode
- Disabled system shortcuts (Alt+Tab, F11, Ctrl+Alt+Del)
- Navigation restrictions
- Auto-recovery on crash
- Configurable allowed domains

---

## 🗂️ Project Structure

```
zt-main/
├── backend/                    # Python FastAPI Backend
│   ├── main.py                # FastAPI app entry point
│   ├── database.py            # SQLite database operations
│   ├── ml_engine_uae.py       # ML risk assessment engine
│   ├── otp.py                 # OTP generation and verification
│   ├── admin_routes.py        # Admin API endpoints
│   ├── inventory_routes.py    # Inventory management APIs
│   ├── models/                # ML model files
│   │   └── global_model.pkl   # Trained risk assessment model
│   ├── requirements.txt       # Python dependencies
│   ├── Dockerfile             # Container configuration
│   └── docker-compose.yml     # Multi-container setup
│
├── admin-panel/               # React Admin Dashboard
│   ├── src/
│   │   ├── pages/             # Dashboard, Users, Analytics
│   │   ├── components/        # Reusable UI components
│   │   ├── contexts/          # React context (Auth)
│   │   └── utils/             # API client, helpers
│   ├── vite.config.ts         # Vite build configuration
│   └── package.json           # Node dependencies
│
└── kiosk/                     # Kiosk Application
    ├── src/
    │   ├── components/        # Login, 2FA, UI components
    │   ├── pages/             # Inventory page
    │   ├── contexts/          # User context
    │   └── utils/             # API client, kiosk mode
    ├── electron/              # Electron wrapper
    │   ├── main.js            # Electron main process
    │   └── preload.js         # Secure IPC bridge
    ├── linux-config/          # Linux kiosk setup scripts
    └── package.json           # Node dependencies
```

---

## 🔌 API Endpoints

### Public Endpoints
- `POST /api/authenticate` - Authenticate user and get risk score
- `POST /api/otp/request` - Request OTP for 2FA
- `POST /api/otp/verify` - Verify OTP code
- `GET /api/health` - Health check

### Admin Endpoints (Requires JWT Token)
- `GET /api/admin/dashboard/stats` - System statistics
- `GET /api/admin/users` - List all users
- `POST /api/admin/users` - Create new user
- `DELETE /api/admin/users/{id}` - Delete user
- `GET /api/admin/login-attempts` - Audit logs
- `GET /api/admin/risk-analytics` - Risk distribution data
- `GET /api/admin/admin-users` - List admin accounts
- `POST /api/admin/admin-users` - Create admin account

### Inventory Endpoints
- `GET /api/inventory/items` - List inventory items
- `POST /api/inventory/items` - Add inventory item
- `PUT /api/inventory/items/{id}` - Update item
- `DELETE /api/inventory/items/{id}` - Delete item

---

## 🔧 Configuration

### Backend Environment Variables (.env)

```env
# Database
DB_PATH=./zt_verify.db

# Email Service (Resend API)
RESEND_API_KEY=your_resend_api_key_here

# JWT Secret
JWT_SECRET=your-secret-key-here

# Admin Account
ADMIN_USERNAME=admin
ADMIN_PASSWORD=Admin123!
```

### Frontend Environment Variables

**Admin Panel:**
```env
VITE_API_BASE_URL=http://localhost:8000
```

**Kiosk:**
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_PRODUCTION_URL=https://zt-two.vercel.app
```

---

## 🧪 Testing

### Backend Tests
```bash
cd backend

# Test database operations
python test_database.py

# Test ML engine
python test_uae_model.py

# Test API endpoints
python test_api.py

# Test OTP functionality
python test_otp_endpoints.py
```

### Demo Users
Create demo users for testing:
```bash
python create_demo_users.py
```

**Demo Accounts:**
- **green_user** / password123 (Low risk - 15)
- **yellow_user** / password123 (Medium risk - 50)
- **red_user** / password123 (High risk - 85)

---

## 📦 Database Schema

### Users Table
- `id`, `username`, `email`, `hashed_password`, `full_name`, `role`, `created_at`

### Login Attempts Table
- `id`, `user_id`, `username`, `timestamp`, `ip_address`, `device_info`, `risk_score`, `decision`, `success`

### Devices Table
- `id`, `user_id`, `device_fingerprint`, `trusted`, `last_seen`

### OTP Challenges Table
- `id`, `user_id`, `code_hash`, `expires_at`, `verified`, `created_at`

### Admin Users Table
- `id`, `username`, `email`, `hashed_password`, `created_at`

### Inventory Table
- `id`, `name`, `quantity`, `location`, `last_updated`

---

## 🌐 Deployment

### Backend Deployment (Render.com)
1. Push code to GitHub
2. Connect repository to Render
3. Configure environment variables
4. Deploy as Web Service

### Frontend Deployment (Vercel)

**Admin Panel:**
```bash
cd admin-panel
vercel deploy --prod
```

**Kiosk:**
```bash
cd kiosk
vercel deploy --prod
```

### Electron Kiosk Packaging

**For Linux:**
```bash
cd kiosk
npm install
npm run build
# Use electron-builder to package
```

**For Windows:**
```bash
cd kiosk
npm run build
# Use electron-builder with Windows target
```

---

## 🔐 Security Considerations

### Production Checklist
- [ ] Change default admin password
- [ ] Generate strong JWT secret
- [ ] Configure CORS for specific origins only
- [ ] Enable HTTPS for all endpoints
- [ ] Set up rate limiting
- [ ] Configure firewall rules
- [ ] Enable database backups
- [ ] Review and harden kiosk lockdown settings
- [ ] Implement log rotation
- [ ] Set up monitoring and alerts

### Kiosk Security
- Disable all system shortcuts
- Use OpenBox or minimal window manager on Linux
- Configure autostart and watchdog
- Whitelist allowed navigation domains
- Enable automatic crash recovery
- Disable developer tools in production

---

## 🛠️ Development Tools

### Useful Commands

**Backend:**
```bash
make dev          # Start development server
make test         # Run all tests
make seed         # Seed database with demo data
make migrate      # Run database migrations
```

**Frontend:**
```bash
npm run dev       # Start dev server
npm run build     # Production build
npm run preview   # Preview production build
npm run lint      # Run linter
```

---

## 📝 License

This project is proprietary software. All rights reserved.

---

## 👥 Support

For questions or issues:
- Review documentation in individual component README files
- Check API documentation at `/docs` endpoint
- Review test files for usage examples

---

## 🗺️ Roadmap

### Future Enhancements
- [ ] Biometric authentication support
- [ ] Multi-language support
- [ ] Advanced threat intelligence integration
- [ ] Real-time dashboard updates via WebSockets
- [ ] Mobile admin app
- [ ] Automated security reports
- [ ] Integration with SIEM systems

---

**Built with ❤️ for Zero Trust Security**
