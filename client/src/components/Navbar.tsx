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
              title="شروط الاستخدام وإخلاء المسؤولية"
            >
              <ShieldCheck className="h-3.5 w-3.5" />
              <span className="text-[10px] font-semibold">شروط الاستخدام وإخلاء المسؤولية</span>
            </button>

            <DialogContent
              dir="rtl"
              showCloseButton={false}
              className="max-h-[calc(100dvh-2rem)] max-w-md overflow-y-auto text-right"
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
                    شروط الاستخدام وإخلاء المسؤولية
                  </DialogTitle>
                </div>
                <DialogClose className="text-xl leading-none opacity-65 transition-opacity hover:opacity-100" aria-label="إغلاق">×</DialogClose>
              </div>

              <DialogDescription className="pt-1 text-right text-sm leading-8" style={{ color: "#F7FBFF", fontFamily: "Cairo, sans-serif" }}>
                <span>مكنز القضاء والأنظمة والمحاماة منصة بحثية غير ربحية تُعنى بفهرسة الروابط والإحالات إلى الأبحاث والمواد النظامية والقضائية المنشورة والمتاحة عبر مصادر ومواقع خارجية، وقد أُعدّت مبادرةً لتيسير البحث وخدمة الدارسين والممارسين في الحقل العدلي.</span>
                <br />
                <br />
                <span><strong>إخلاء المسؤولية القانونية:</strong> لا يقدّم المكنز استشارات قانونية أو إفتاءً نظامياً، ولا يُغني عن الرجوع إلى الوثائق الصادرة عن الجهات القضائية والرسمية المختصة أو الجرائد الرسمية. وتتضمن المواد مصادر من ولايات وأنظمة قضائية متعددة؛ لذا تقع مسؤولية التحقق من سريان المواد وصحتها وحداثتها ومدى انطباقها على الاختصاص النوعي والمكاني على عاتق المستخدم وحده.</span>
                <br />
                <br />
                <span><strong>حقوق الملكية الفكرية:</strong> لا تدّعي المنصة ملكية أيٍّ من المواد المُحال إليها، وتظل جميع الحقوق الفكرية والأدبية محفوظةً لأصحاب الحقوق ومصادرها الأصلية، كما لا تضمن المنصة استمرار الروابط أو سلامة المحتوى الخارجي.</span>
                <br />
                <br />
                <span><strong>الملاحظات وطلبات التعديل:</strong> لمن كان له حق أو استفسار أو طلب حذف أو تصحيح رابط، يُرجى التواصل عبر البريد الإلكتروني: <a href="mailto:yhoshan@gmail.com" className="underline underline-offset-2 hover:opacity-85">yhoshan@gmail.com</a>.</span>
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
