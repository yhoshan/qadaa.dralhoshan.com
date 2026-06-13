/* =============================================
   Navbar — مكنز القضاء والأنظمة والمحاماة
   Dark Judicial Majesty Design
   ============================================= */
import { useTheme } from "@/contexts/ThemeContext";
import { Sun, Moon, Scale } from "lucide-react";
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
          {/* Right: Signature */}
          <a
            href="https://nsooos.com/"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 opacity-90 hover:opacity-100 transition-opacity"
            title="د. يوسف بن حمود الحوشان"
          >
            <span
              className="text-[oklch(0.82_0.10_75)] text-sm font-bold"
              style={{ fontFamily: "Amiri, serif" }}
            >
              د. يوسف بن حمود الحوشان
            </span>
          </a>

          {/* Center: Logo + Title */}
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-[oklch(0.72_0.12_75/0.15)] border border-[oklch(0.72_0.12_75/0.4)] flex items-center justify-center">
                <Scale className="w-4 h-4 text-[oklch(0.82_0.10_75)]" />
              </div>
              <div className="hidden sm:block">
                <h1 className="text-sm font-bold text-[oklch(0.92_0.01_80)] leading-tight" style={{ fontFamily: "Amiri, serif" }}>
                  مكنز القضاء والأنظمة
                </h1>
                <p className="text-[10px] text-[oklch(0.60_0.01_240)] leading-tight">والمحاماة</p>
              </div>
            </div>
          </div>

          {/* Left: Actions */}
          <div className="flex items-center gap-2">
            {/* Dark Mode Toggle */}
            <button
              onClick={toggleTheme}
              className="w-9 h-9 rounded-lg bg-[oklch(0.20_0.03_240)] border border-[oklch(0.25_0.03_240)] flex items-center justify-center text-[oklch(0.72_0.12_75)] hover:bg-[oklch(0.25_0.04_240)] transition-colors"
              title={theme === "dark" ? "الوضع النهاري" : "الوضع الليلي"}
            >
              {theme === "dark" ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
            </button>

            {/* Makanez Platform Link */}
            <a
              href="https://dralhoshan.com/"
              target="_blank"
              rel="noopener noreferrer"
              title="منصة المكانز العلمية"
              className="w-9 h-9 flex items-center justify-center opacity-80 hover:opacity-100 transition-opacity"
            >
              <img
                src="https://zadwarod.dralhoshan.com/manus-storage/makanez-icon_85f25650.png"
                alt="منصة المكانز"
                className="h-7 w-auto object-contain"
              />
            </a>
          </div>
        </div>
      </div>
    </header>
  );
}
