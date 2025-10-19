import { Link, useLocation } from "react-router-dom";
import { Bell, Sprout } from "lucide-react";

export default function Header() {
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  return (
    <header className="w-full border-b-2 border-emerald-500 bg-white shadow-lg sticky top-0 z-50">
      <div className="max-w-[1280px] mx-auto px-6 py-4">
        <div className="flex items-center justify-between gap-8">
          <Link to="/" className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-500 to-lime-500 flex items-center justify-center">
              <Sprout className="w-5 h-5 text-white" />
            </div>
            <div className="flex flex-col">
              <h1 className="text-2xl font-bold text-gray-800 leading-none">
                RiceGuard AI
              </h1>
              <p className="text-sm text-gray-500">Smart Disease Detection</p>
            </div>
          </Link>

          <nav className="hidden md:flex items-center gap-8">
            <Link
              to="/"
              className={`text-base font-semibold transition-colors ${
                isActive("/")
                  ? "text-emerald-500 border-b-2 border-emerald-500 pb-1"
                  : "text-gray-600 hover:text-emerald-500"
              }`}
            >
              Home
            </Link>
            <Link
              to="/history"
              className={`text-base transition-colors ${
                isActive("/history")
                  ? "text-emerald-500 border-b-2 border-emerald-500 pb-1"
                  : "text-gray-600 hover:text-emerald-500"
              }`}
            >
              History
            </Link>
            <Link
              to="/disease-library"
              className={`text-base transition-colors ${
                isActive("/disease-library")
                  ? "text-emerald-500 border-b-2 border-emerald-500 pb-1"
                  : "text-gray-600 hover:text-emerald-500"
              }`}
            >
              Disease Library
            </Link>
            <Link
              to="/about"
              className={`text-base transition-colors ${
                isActive("/about")
                  ? "text-emerald-500 border-b-2 border-emerald-500 pb-1"
                  : "text-gray-600 hover:text-emerald-500"
              }`}
            >
              About
            </Link>
          </nav>

          <div className="flex items-center gap-4">
            <button className="w-10 h-10 rounded-full bg-emerald-50 flex items-center justify-center hover:bg-emerald-100 transition-colors">
              <Bell className="w-3.5 h-3.5 text-black" />
            </button>
            <img
              src="https://api.builder.io/api/v1/image/assets/TEMP/da40fe1b098b82c8bb229ad2da29306c81399209?width=80"
              alt="User profile"
              className="w-10 h-10 rounded-full border-2 border-emerald-500"
            />
          </div>
        </div>
      </div>
    </header>
  );
}
