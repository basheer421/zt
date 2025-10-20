import { useState } from "react";
import { Button, Card } from "./components";
import { formatCurrency } from "./utils/helpers";

function App() {
  const [count, setCount] = useState(0);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-4xl mx-auto">
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            Kiosk Frontend
          </h1>
          <p className="text-gray-600">
            React + TypeScript + Vite + Tailwind CSS
          </p>
        </header>

        <div className="grid gap-6 md:grid-cols-2">
          <Card title="Counter Demo">
            <div className="text-center">
              <p className="text-5xl font-bold text-blue-600 mb-4">{count}</p>
              <div className="flex gap-2 justify-center">
                <Button
                  variant="primary"
                  size="lg"
                  onClick={() => setCount((count) => count + 1)}
                >
                  Increment
                </Button>
                <Button
                  variant="secondary"
                  size="lg"
                  onClick={() => setCount(0)}
                >
                  Reset
                </Button>
              </div>
            </div>
          </Card>

          <Card title="Features">
            <ul className="space-y-2 text-gray-700">
              <li className="flex items-center">
                <span className="text-green-500 mr-2">✓</span>
                React 18 with TypeScript
              </li>
              <li className="flex items-center">
                <span className="text-green-500 mr-2">✓</span>
                Vite for fast development
              </li>
              <li className="flex items-center">
                <span className="text-green-500 mr-2">✓</span>
                Tailwind CSS for styling
              </li>
              <li className="flex items-center">
                <span className="text-green-500 mr-2">✓</span>
                Component library structure
              </li>
              <li className="flex items-center">
                <span className="text-green-500 mr-2">✓</span>
                Utility functions & types
              </li>
            </ul>
          </Card>

          <Card title="Currency Formatter">
            <div className="space-y-3">
              <p className="text-gray-700">
                Amount:{" "}
                <span className="font-mono text-blue-600">
                  {formatCurrency(1234.56)}
                </span>
              </p>
              <p className="text-gray-700">
                Balance:{" "}
                <span className="font-mono text-green-600">
                  {formatCurrency(50000)}
                </span>
              </p>
            </div>
          </Card>

          <Card title="Quick Actions">
            <div className="space-y-2">
              <Button variant="primary" className="w-full">
                Start Transaction
              </Button>
              <Button variant="secondary" className="w-full">
                View History
              </Button>
              <Button variant="danger" className="w-full">
                Emergency Stop
              </Button>
            </div>
          </Card>
        </div>

        <footer className="mt-8 text-center text-gray-600 text-sm">
          <p>Ready to build your kiosk application!</p>
        </footer>
      </div>
    </div>
  );
}

export default App;
