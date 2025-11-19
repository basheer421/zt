# ZT-Verify Admin Panel

A modern React admin panel for managing the ZT-Verify zero-trust authentication system.

## Features

- 📊 **Dashboard** - Overview with statistics, charts, and recent activity
- 👥 **User Management** - View, edit, suspend, delete, and **create new users**
- 🔐 **Login Attempts** - Monitor all authentication attempts with filtering
- 📈 **Risk Analytics** - Visualize risk scores and identify high-risk users
- 👨‍💼 **Admin Management** - Create and manage administrator accounts
- 🎨 **Modern UI** - Built with React, TypeScript, and Tailwind CSS
- 🔑 **User Creation** - Create users and get shareable credentials with copy-to-clipboard

## Tech Stack

- **React 18** - Modern React with hooks
- **TypeScript** - Type-safe development
- **Vite** - Fast build tool and dev server
- **React Router** - Client-side routing
- **Tailwind CSS** - Utility-first styling
- **Recharts** - Beautiful charts and visualizations
- **Lucide React** - Modern icon library
- **Axios** - HTTP client with interceptors
- **date-fns** - Date formatting utilities

## Prerequisites

- Node.js 18+ and npm
- ZT-Verify backend running (see `../backend/README.md`)

## Getting Started

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` and set your backend URL:

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

### 3. Run Development Server

```bash
npm run dev
```

The admin panel will be available at `http://localhost:5174`

### 4. Create Initial Admin User

The backend automatically creates a default admin user during deployment:

**Default Admin Credentials:**

- Username: `admin`
- Password: `Admin123!`

⚠️ **IMPORTANT**: Change this password after first login!

If you need to create additional admin users manually from the backend:

```bash
# Using Python
python create_admin.py
```

Follow the prompts to create a new admin user.

### 5. Login

Navigate to `http://localhost:5174/login` and use your admin credentials.

## Project Structure

```
admin-panel/
├── src/
│   ├── components/       # Reusable components
│   │   ├── Layout.tsx    # Main layout with sidebar
│   │   └── PrivateRoute.tsx  # Protected route wrapper
│   ├── contexts/         # React contexts
│   │   └── AuthContext.tsx   # Authentication state
│   ├── pages/            # Page components
│   │   ├── Login.tsx     # Login page
│   │   ├── Dashboard.tsx # Dashboard with stats
│   │   ├── Users.tsx     # User management
│   │   ├── LoginAttempts.tsx  # Login monitoring
│   │   ├── RiskAnalytics.tsx  # Risk visualization
│   │   └── AdminUsers.tsx     # Admin management
│   ├── types/            # TypeScript types
│   │   └── index.ts
│   ├── utils/            # Utility functions
│   │   └── api.ts        # API client
│   ├── App.tsx           # Root component
│   ├── main.tsx          # Entry point
│   └── index.css         # Global styles
├── index.html
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── tsconfig.json
```

## Available Scripts

- `npm run dev` - Start development server (port 5174)
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Building for Production

```bash
npm run build
```

The build output will be in the `dist/` directory, ready to deploy to Vercel, Netlify, or any static host.

## Deploying to Vercel

1. Install Vercel CLI:

   ```bash
   npm install -g vercel
   ```

2. Login to Vercel:

   ```bash
   vercel login
   ```

3. Deploy:

   ```bash
   vercel
   ```

4. Set environment variables in Vercel dashboard:
   - `VITE_API_BASE_URL` - Your production backend URL

## Backend API Endpoints

The admin panel expects these endpoints from the backend:

### Authentication

- `POST /api/admin/login` - Admin login

### Dashboard

- `GET /api/admin/stats?days=7` - Get dashboard statistics
- `GET /api/admin/recent-activity?limit=10` - Get recent login attempts

### Users

- `GET /api/admin/users` - Get all users
- `GET /api/admin/users/:id` - Get user by ID
- `POST /api/admin/users` - Create user
- `PUT /api/admin/users/:id` - Update user
- `DELETE /api/admin/users/:id` - Delete user
- `PATCH /api/admin/users/:id/status` - Update user status

### Login Attempts

- `GET /api/admin/login-attempts` - Get all login attempts
- `GET /api/admin/login-attempts/:username` - Get user's login attempts

### Risk Analytics

- `GET /api/admin/risky-users?limit=10` - Get top risky users
- `GET /api/admin/risk-distribution?days=7` - Get risk distribution

### Admin Users

- `GET /api/admin/admin-users` - Get all admin users
- `POST /api/admin/admin-users` - Create admin user
- `DELETE /api/admin/admin-users/:username` - Delete admin user

## Security Notes

- Admin credentials are stored in a separate `admin_users` table
- JWT tokens are stored in localStorage (consider httpOnly cookies for production)
- All API requests include authentication headers
- CORS is configured in the backend for the admin panel origin

## Troubleshooting

### Cannot connect to backend

- Ensure backend is running on `http://localhost:8000`
- Check CORS settings in backend
- Verify `VITE_API_BASE_URL` in `.env`

### Login fails

- Verify admin user exists in database
- Check backend logs for errors
- Ensure password is hashed with bcrypt

### Build fails

- Run `npm install` to ensure all dependencies are installed
- Check Node.js version (18+ required)
- Clear `node_modules` and reinstall if needed

## License

Part of the ZT-Verify project.
