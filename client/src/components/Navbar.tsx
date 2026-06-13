/* =============================================
   Navbar — مكنز القضاء والأنظمة والمحاماة
   Dark Judicial Majesty Design
   ============================================= */
import { useTheme } from "@/contexts/ThemeContext";
import { Sun, Moon } from "lucide-react";
import { useState, useEffect } from "react";

export default function Navbar() {
  const { theme, toggleTheme } = useTheme();
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 60);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header
      className={`fixed top-0 right-0 left-0 z-50 transition-all duration-300 ${
        scrolled
          ? "bg-[oklch(0.12_0.02_240/0.97)] backdrop-blur-xl border-b border-[oklch(0.25_0.03_240)]"
          : "bg-transparent"
      }`}
    >
      <div className="container">
        <div className="flex items-center justify-between h-16">

          {/* Right: Signature image */}
          <a
            href="https://dralhoshan.com/"
            target="_blank"
            rel="noopener noreferrer"
            className="opacity-90 hover:opacity-100 transition-opacity"
            title="د. يوسف بن حمود الحوشان"
          >
            <img
              src="/manus-storage/signature-hoshan_0c8875c4.webp"
              alt="د. يوسف بن حمود الحوشان"
              className="h-10 w-auto object-contain"
              style={{ filter: "invert(1) brightness(2)" }}
            />
          </a>

          {/* Center: Title only (no logo) */}
          <div className="hidden sm:block text-center">
            <h1
              className="text-sm font-bold text-[oklch(0.92_0.01_80)] leading-tight"
              style={{ fontFamily: "Amiri, serif" }}
            >
              مكنز القضاء والأنظمة والمحاماة
            </h1>
          </div>

          {/* Left: Dark Mode Toggle only */}
          <div className="flex items-center gap-2">
            <button
              onClick={toggleTheme}
              className="w-9 h-9 rounded-lg bg-[oklch(0.20_0.03_240)] border border-[oklch(0.25_0.03_240)] flex items-center justify-center text-[oklch(0.72_0.12_75)] hover:bg-[oklch(0.25_0.04_240)] transition-colors"
              title={theme === "dark" ? "الوضع النهاري" : "الوضع الليلي"}
            >
              {theme === "dark" ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
            </button>
          </div>

        </div>
      </div>
    </header>
  );
}
