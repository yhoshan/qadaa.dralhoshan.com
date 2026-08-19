/* =============================================
   WhatsAppShare — أيقونة مشاركة عائمة خضراء، مستلهمة من مكنز أصول الفقه.
   ============================================= */
import { MessageCircle, Phone } from "lucide-react";

export default function WhatsAppShare() {
  const shareText = "مكنز القضاء والأنظمة والمحاماة — فهرس للروابط والمواد القانونية والقضائية للباحثين";
  const href = `https://wa.me/?text=${encodeURIComponent(`${shareText}\nhttps://qadaa.dralhoshan.com/`)}`;

  return (
    <a
      className="whatsapp-share"
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      aria-label="مشاركة المكنز عبر واتساب"
      title="مشاركة عبر واتساب"
    >
      <MessageCircle aria-hidden="true" className="whatsapp-share__bubble" />
      <Phone aria-hidden="true" className="whatsapp-share__phone" />
    </a>
  );
}
