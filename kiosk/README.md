# Kiosk Frontend

A modern kiosk frontend application built with React, TypeScript, Vite, and Tailwind CSS.

**🖥️ Dual Deployment:** Runs as a web app OR as an Electron desktop app with true OS-level security.

> **For Electron Desktop App:** See [ELECTRON_README.md](./ELECTRON_README.md) for desktop deployment with Alt+Tab blocking.  
> **For Linux Deployment:** See [LINUX_SETUP.md](./LINUX_SETUP.md) for Ubuntu/Openbox kiosk setup.

## 🚀 Tech Stack

- **React 18** - Modern React with hooks
- **TypeScript** - Type-safe development
- **Vite** - Lightning-fast build tool
- **Tailwind CSS** - Utility-first CSS framework
- **PostCSS & Autoprefixer** - CSS processing
- **Electron** (Optional) - Desktop app with OS-level security

## 📁 Project Structure

```
kiosk/
├── src/
│   ├── components/       # Reusable UI components
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   └── index.ts
│   ├── utils/           # Utility functions
│   │   ├── api.ts       # API client
│   │   └── helpers.ts   # Helper functions
│   ├── types/           # TypeScript type definitions
│   │   └── index.ts
│   ├── App.tsx          # Main application component
│   ├── main.tsx         # Application entry point
│   └── index.css        # Global styles with Tailwind
├── public/              # Static assets
├── tailwind.config.js   # Tailwind configuration
├── postcss.config.js    # PostCSS configuration
├── tsconfig.json        # TypeScript configuration
├── vite.config.ts       # Vite configuration
└── package.json         # Dependencies
```

## 🛠️ Setup & Installation

The project has been initialized with all dependencies. To set up:

1. **Copy environment variables:**

   ```bash
   cp .env.example .env
   ```

2. **Install dependencies (if needed):**
   ```bash
   npm install
   ```

## 🏃 Development

Start the development server:

```bash
npm run dev
```

The application will be available at `http://localhost:5173/`

## 🔧 Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## 🎨 Tailwind CSS

Tailwind CSS is configured and ready to use. The configuration includes:

- Content paths for all source files
- PostCSS with Autoprefixer
- Custom theme extensions (in `tailwind.config.js`)

### Usage Example:

```tsx
<div className="bg-blue-500 text-white p-4 rounded-lg">Hello Tailwind!</div>
```

## 📦 Components

### Button

```tsx
import { Button } from "./components";

<Button variant="primary" size="lg" onClick={handleClick}>
  Click Me
</Button>;
```

### Card

```tsx
import { Card } from "./components";

<Card title="My Card">
  <p>Card content goes here</p>
</Card>;
```

## 🔌 API Integration

The `api.ts` utility provides methods for backend communication:

```tsx
import { api } from "./utils/api";

// GET request
const data = await api.get("/users");

// POST request
const result = await api.post("/transactions", { amount: 100 });
```

## 🎯 Type Safety

Type definitions are located in `src/types/index.ts`:

```typescript
interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
}
```

## 🚀 Building for Production

```bash
npm run build
```

The production-ready files will be in the `dist/` directory.

## 📝 Environment Variables

Create a `.env` file based on `.env.example`:

- `VITE_API_BASE_URL` - Backend API URL (default: http://localhost:8000)

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## 📄 License

MIT

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) (or [oxc](https://oxc.rs) when used in [rolldown-vite](https://vite.dev/guide/rolldown)) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default defineConfig([
  globalIgnores(["dist"]),
  {
    files: ["**/*.{ts,tsx}"],
    extends: [
      // Other configs...

      // Remove tseslint.configs.recommended and replace with this
      tseslint.configs.recommendedTypeChecked,
      // Alternatively, use this for stricter rules
      tseslint.configs.strictTypeChecked,
      // Optionally, add this for stylistic rules
      tseslint.configs.stylisticTypeChecked,

      // Other configs...
    ],
    languageOptions: {
      parserOptions: {
        project: ["./tsconfig.node.json", "./tsconfig.app.json"],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
]);
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from "eslint-plugin-react-x";
import reactDom from "eslint-plugin-react-dom";

export default defineConfig([
  globalIgnores(["dist"]),
  {
    files: ["**/*.{ts,tsx}"],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs["recommended-typescript"],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ["./tsconfig.node.json", "./tsconfig.app.json"],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
]);
```
