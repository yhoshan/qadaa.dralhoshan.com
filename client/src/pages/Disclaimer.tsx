/* =============================================
   Disclaimer — إخلاء المسؤولية
   مكنز القضاء والأنظمة والمحاماة
   ============================================= */
import { Link } from "wouter";
import { ArrowRight, Scale } from "lucide-react";

export default function Disclaimer() {
  return (
    <div
      className="min-h-screen"
      style={{ background: "oklch(0.98 0.01 85)", fontFamily: "Cairo, sans-serif", direction: "rtl" }}
    >
      {/* Header */}
      <div
        className="border-b px-6 py-4 flex items-center gap-3"
        style={{ borderColor: "oklch(0.88 0.04 78)", background: "oklch(0.96 0.02 82)" }}
      >
        <Link href="/">
          <button
            className="flex items-center gap-2 text-sm transition-opacity hover:opacity-70"
            style={{ color: "oklch(0.48 0.12 68)", fontFamily: "Cairo, sans-serif" }}
          >
            <ArrowRight className="w-4 h-4" />
            العودة للرئيسية
          </button>
        </Link>
      </div>

      {/* Content */}
      <div className="max-w-3xl mx-auto px-6 py-12">
        {/* Title */}
        <div className="flex items-center gap-3 mb-8">
          <div
            className="w-12 h-12 rounded-xl flex items-center justify-center"
            style={{ background: "oklch(0.93 0.03 80)", border: "1px solid oklch(0.85 0.05 78)" }}
          >
            <Scale className="w-6 h-6" style={{ color: "oklch(0.48 0.12 68)" }} />
          </div>
          <div>
            <h1
              className="text-2xl font-bold"
              style={{ fontFamily: "Amiri, serif", color: "oklch(0.18 0.04 50)" }}
            >
              إخلاء المسؤولية
            </h1>
            <p className="text-xs mt-0.5" style={{ color: "oklch(0.52 0.06 60)" }}>
              يُرجى قراءة هذا البيان بعناية قبل استخدام الموقع
            </p>
          </div>
        </div>

        {/* Disclaimer box */}
        <div
          className="rounded-2xl p-8 space-y-6 text-sm leading-loose"
          style={{
            background: "oklch(1 0 0)",
            border: "1px solid oklch(0.88 0.04 78)",
            color: "oklch(0.25 0.04 50)",
            boxShadow: "0 2px 16px oklch(0.48 0.12 68 / 0.06)",
          }}
        >
          <p>
            هذا الموقع <strong>مكنز بحثي توثيقي</strong> يهدف إلى تسهيل الوصول إلى المواد القضائية والنظامية والبحثية،
            ولا يُعد ما فيه استشارة قانونية أو رأيًا مهنيًا أو تمثيلًا نظاميًا أو وعدًا بنتيجة قضائية.
          </p>

          <hr style={{ borderColor: "oklch(0.92 0.03 80)" }} />

          <p>
            يتحمل المستخدم وحده مسؤولية التحقق من حداثة النصوص والأنظمة والأحكام والقرارات، ومن ملاءمتها لواقعته الخاصة،
            ولا يجوز الاعتماد على نتائج البحث أو المواد المعروضة في اتخاذ إجراء قضائي أو نظامي أو مالي إلا بعد مراجعة
            <strong> محامٍ أو مختص مرخص</strong>.
          </p>

          <hr style={{ borderColor: "oklch(0.92 0.03 80)" }} />

          <p>
            لا يضمن القائمون على الموقع اكتمال المواد أو خلوها من الخطأ أو السهو أو تغيرها بعد النشر،
            ولا يتحملون أي مسؤولية عن أي خسارة أو ضرر مباشر أو غير مباشر ينشأ عن استخدام الموقع أو
            عدم القدرة على استخدامه أو الاعتماد على محتواه.
          </p>

          <hr style={{ borderColor: "oklch(0.92 0.03 80)" }} />

          <p>
            الروابط أو الملفات أو الإحالات الخارجية — إن وجدت — وُضعت للتيسير، ولا تعني المصادقة على محتواها
            أو تحمل المسؤولية عنها.
          </p>

          <hr style={{ borderColor: "oklch(0.92 0.03 80)" }} />

          <p>
            جميع الحقوق محفوظة لأصحابها، ويُمنع إعادة نشر محتوى الموقع أو استغلاله تجاريًا أو آليًا
            إلا بإذن مكتوب، مع الالتزام بالأنظمة ذات العلاقة.
          </p>
        </div>

        {/* Back button */}
        <div className="mt-8 text-center">
          <Link href="/">
            <button
              className="px-6 py-3 rounded-xl text-sm font-bold transition-opacity hover:opacity-80"
              style={{
                background: "rgb(139, 105, 20)",
                color: "white",
                fontFamily: "Cairo, sans-serif",
              }}
            >
              العودة إلى المكنز
            </button>
          </Link>
        </div>
      </div>
    </div>
  );
}
