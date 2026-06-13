/* =============================================
   Navbar — مكنز القضاء والأنظمة والمحاماة
   ألوان مطابقة لـ osool.dralhoshan.com
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

  const isDark = theme === "dark";

  return (
    <header
      className="fixed top-0 right-0 left-0 z-50 transition-all duration-300"
      style={{
        background: scrolled
          ? isDark
            ? "oklch(0.18 0.04 52 / 0.97)"
            : "oklch(0.98 0.01 85 / 0.97)"
          : "transparent",
        backdropFilter: scrolled ? "blur(12px)" : "none",
        borderBottom: scrolled
          ? isDark
            ? "1px solid oklch(1 0 0 / 12%)"
            : "1px solid oklch(0.88 0.04 78)"
          : "none",
      }}
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
              className="h-8 w-auto object-contain"
              style={{
                filter: "invert(1) brightness(2) drop-shadow(0 1px 3px rgba(0,0,0,0.6))",
              }}
            />
          </a>

          {/* Center: Title */}
          <div className="hidden sm:block text-center">
            <h1
              className="text-sm font-bold leading-tight"
              style={{
                fontFamily: "Amiri, serif",
                color: isDark ? "oklch(0.92 0.01 80)" : "oklch(0.18 0.04 50)",
              }}
            >
              مكنز القضاء والأنظمة والمحاماة
            </h1>
          </div>

          {/* Left: Dark Mode Toggle */}
          <div className="flex items-center gap-2">
            <button
              onClick={toggleTheme}
              className="w-9 h-9 rounded-lg flex items-center justify-center transition-colors"
              style={{
                background: isDark ? "oklch(0.28 0.05 52)" : "oklch(0.93 0.03 80)",
                border: isDark ? "1px solid oklch(1 0 0 / 12%)" : "1px solid oklch(0.88 0.04 78)",
                color: "oklch(0.48 0.12 68)",
              }}
              title={isDark ? "الوضع النهاري" : "الوضع الليلي"}
            >
              {isDark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
            </button>
          </div>

        </div>
      </div>
    </header>
  );
}
