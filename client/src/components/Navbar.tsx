/* =============================================
   Navbar — مكنز القضاء والأنظمة والمحاماة
   زر حول المكنز ذهبي صغير مقابل الوضع الليلي، ونافذة تعريفية بهوية بيجية
   ============================================= */
import { useTheme } from "@/contexts/ThemeContext";
import { Sun, Moon, ShieldCheck } from "lucide-react";
import { useState, useEffect } from "react";
import { Dialog, DialogClose, DialogContent, DialogDescription, DialogTitle } from "@/components/ui/dialog";

export default function Navbar() {
  const { theme, toggleTheme } = useTheme();
  const [scrolled, setScrolled] = useState(false);
  const [aboutOpen, setAboutOpen] = useState(false);

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

          {/* Right: About the thesaurus — identity-colored compact control */}
          <Dialog open={aboutOpen} onOpenChange={setAboutOpen}>
            <button
              onClick={() => setAboutOpen(true)}
              className="inline-flex h-9 items-center gap-1.5 rounded-lg px-3 transition-all hover:opacity-85 active:scale-[0.97]"
              style={{
                background: isDark ? "oklch(0.28 0.05 52)" : "oklch(0.93 0.03 80)",
                border: isDark ? "1px solid oklch(1 0 0 / 12%)" : "1px solid oklch(0.88 0.04 78)",
                color: "oklch(0.48 0.12 68)",
                fontFamily: "Cairo, sans-serif",
              }}
              title="حول المكنز"
            >
              <ShieldCheck className="h-3.5 w-3.5" />
              <span className="text-[10px] font-semibold">حول المكنز</span>
            </button>

            <DialogContent
              dir="rtl"
              showCloseButton={false}
              className="max-w-md text-right"
              style={{
                background: "#006C35",
                borderColor: "#F7FBFF",
                color: "#F7FBFF",
                fontFamily: "Cairo, sans-serif",
              }}
            >
              <div className="flex items-center justify-between gap-4 border-b pb-3" style={{ borderColor: "#F7FBFF" }}>
                <div className="flex items-center gap-2">
                  <ShieldCheck className="h-5 w-5" style={{ color: "#F7FBFF" }} />
                  <DialogTitle className="text-base" style={{ fontFamily: "Amiri, serif", color: "#F7FBFF" }}>
                    حول المكنز
                  </DialogTitle>
                </div>
                <DialogClose className="text-xl leading-none opacity-65 transition-opacity hover:opacity-100" aria-label="إغلاق">×</DialogClose>
              </div>

              <DialogDescription className="pt-1 text-right text-sm leading-8" style={{ color: "#F7FBFF", fontFamily: "Cairo, sans-serif" }}>
                مكنز القضاء والأنظمة والمحاماة فهرسٌ تجميعيٌّ للروابط والإحالات إلى مواد قانونية وقضائية منشورة في مصادر خارجية، أُعدّ لتيسير الوصول وخدمة الباحثين والقضاة والمحامين. لا يدّعي ملكية المواد ولا يضمن محتواها أو دقتها أو بقاء روابطها. تبقى الحقوق لأصحابها، ويتحمل المستخدم مسؤولية التحقق من المادة وحقوق استخدامها، ومن له حق أو ملاحظة فليتواصل عبر البريد الإلكتروني.
              </DialogDescription>

              <div className="flex justify-center pt-2">
                <DialogClose asChild>
                  <button
                    className="rounded-lg px-6 py-2 text-xs font-semibold transition-opacity hover:opacity-85 active:scale-[0.97]"
                    style={{ background: "#006C35", color: "#F7FBFF", border: "1px solid #F7FBFF", fontFamily: "Cairo, sans-serif" }}
                  >
                    فهمت
                  </button>
                </DialogClose>
              </div>
            </DialogContent>
          </Dialog>

          {/* Center: empty spacer */}
          <div className="flex-1" />

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
