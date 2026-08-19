/* PWA design: صفحة مستقلة بخلفية #006C35 وصورة عنوان المكنز فقط، بلا أرقام أو وصف أو عناصر تحكم. */
const PWA_TITLE_REFERENCE = "/manus-storage/qadaa-pwa-title-reference_aedb1a98.jpeg";

export default function PwaInstall() {
  return (
    <main className="pwa-install-screen" aria-label="مكنز القضاء والأنظمة والمحاماة">
      <div className="pwa-title-reference">
        <img
          src={PWA_TITLE_REFERENCE}
          alt="مكنز القضاء والأنظمة والمحاماة"
        />
      </div>
    </main>
  );
}
