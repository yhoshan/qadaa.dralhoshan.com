/* بيانات روابط المجلات الرسمية؛ تصميم المكنز الأخضر مع فلتر بلد الإصدار. */
export type OfficialJournal = { name: string; country: string; description: string; countLabel: string; color: string; officialLink: string }

export const OFFICIAL_JOURNALS: OfficialJournal[] = [
  {
    "name": "المجلة الأردنية في القانون والعلوم السياسية",
    "country": "الأردن",
    "description": "الأردن · جامعة مؤتة، عمادة البحث العلمي",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.55 0.12 75)",
    "officialLink": "https://dsr.mutah.edu.jo/index.php/jjlps"
  },
  {
    "name": "سلسلة البحوث القانونية - مجلة جامعة عمان العربية للبحوث",
    "country": "الأردن",
    "description": "الأردن · جامعة عمان العربية",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.55 0.12 75)",
    "officialLink": "https://www.aau.edu.jo/ar/administrative/deanship-scientific-research-and-graduate-studies/slslt-albhwth-alqanwnyt"
  },
  {
    "name": "سلسلة العلوم السياسية والقانون (مجلة المنارة للبحوث والدراسات)",
    "country": "الأردن",
    "description": "الأردن · جامعة آل البيت، عمادة البحث العلمي",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.55 0.12 75)",
    "officialLink": "https://journals.aabu.edu.jo/index.php/law"
  },
  {
    "name": "مجلة العدالة والقانون",
    "country": "الأردن",
    "description": "الأردن · مركز البحث وتطوير الموارد البشرية رماح - الأردن",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.55 0.12 75)",
    "officialLink": "https://justlawjo.com/"
  },
  {
    "name": "مجلة المعهد القضائي الأردني للدراسات القضائية والقانونية",
    "country": "الأردن",
    "description": "الأردن · المعهد القضائي الأردني",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.55 0.12 75)",
    "officialLink": "https://jij.gov.jo/"
  },
  {
    "name": "مجلة جامعة الزيتونة للدراسات القانونية (Al-Zaytoonah University of Jordan Journal for Legal Studies)",
    "country": "الأردن",
    "description": "الأردن · جامعة الزيتونة الأردنية، عمادة البحث العلمي والابتكار",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.55 0.12 75)",
    "officialLink": "https://journals.zuj.edu.jo/zujjls/"
  },
  {
    "name": "مجلة أبوظبي الجامعية للقانون (ADUJL)",
    "country": "الإمارات",
    "description": "الإمارات · كلية القانون، جامعة أبوظبي",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.52 0.13 165)",
    "officialLink": "https://journal.adu.ac.ae"
  },
  {
    "name": "مجلة الإمارات لحقوق الإنسان",
    "country": "الإمارات",
    "description": "الإمارات · جمعية الاتحاد لحقوق الإنسان (منظمة غير حكومية)",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.52 0.13 165)",
    "officialLink": "https://theuahr.org/ar/emirates-magazines"
  },
  {
    "name": "مجلة جامعة الإمارات للبحوث القانونية (UAEU Law Journal)",
    "country": "الإمارات",
    "description": "الإمارات · كلية القانون، جامعة الإمارات العربية المتحدة",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.52 0.13 165)",
    "officialLink": "https://www.uaeu.ac.ae/ar/cl/sljournal/index.shtml"
  },
  {
    "name": "مجلة جامعة الشارقة للعلوم القانونية (JLS)",
    "country": "الإمارات",
    "description": "الإمارات · جامعة الشارقة",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.52 0.13 165)",
    "officialLink": "https://spu.sharjah.ac.ae/index.php/JLS"
  },
  {
    "name": "مجلة جامعة عجمان للدراسات القانونية",
    "country": "الإمارات",
    "description": "الإمارات · جامعة عجمان",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.52 0.13 165)",
    "officialLink": "https://www.ajman.ac.ae/ar/law/magazine"
  },
  {
    "name": "المجلة القانونية (هيئة التشريع والرأي القانوني)",
    "country": "البحرين",
    "description": "البحرين · هيئة التشريع والرأي القانوني، مملكة البحرين",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.57 0.15 15)",
    "officialLink": "https://www.lloc.gov.bh"
  },
  {
    "name": "مجلة الحقوق (Journal of Law)",
    "country": "البحرين",
    "description": "البحرين · كلية الحقوق، جامعة البحرين",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.57 0.15 15)",
    "officialLink": "https://law.uob.edu.bh/college-of-science/journal-of-law"
  },
  {
    "name": "مجلة دراسات قانونية",
    "country": "البحرين",
    "description": "البحرين · مجلس النواب، مملكة البحرين",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.57 0.15 15)",
    "officialLink": "https://www.nuwab.bh/%D9%85%D8%AC%D9%84%D8%A9-%D8%AF%D8%B1%D8%A7%D8%B3%D8%A7%D8%AA-%D9%82%D8%A7%D9%86%D9%88%D9%86%D9%8A%D8%A9"
  },
  {
    "name": "المجلة الجزائرية للقانون والعدالة",
    "country": "الجزائر",
    "description": "الجزائر · مركز البحوث القانونية والقضائية",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.54 0.13 140)",
    "officialLink": "https://crjj.mjustice.gov.dz"
  },
  {
    "name": "مجلة الدراسات القانونية",
    "country": "الجزائر",
    "description": "الجزائر · مخبر البحث (غير محدد)",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.54 0.13 140)",
    "officialLink": "https://asjp.cerist.dz"
  },
  {
    "name": "مجلة الدراسات القانونية المقارنة",
    "country": "الجزائر",
    "description": "الجزائر · جامعة الشلف",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.54 0.13 140)",
    "officialLink": "https://journals.univ-chlef.dz"
  },
  {
    "name": "مجلة الدراسات القانونية والسياسية",
    "country": "الجزائر",
    "description": "الجزائر · جامعة عمر تليجي - الأغواط",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.54 0.13 140)",
    "officialLink": "https://www.asjp.cerist.dz/en/PresentationRevue/318"
  },
  {
    "name": "مجلة الدراسات و البحوث القانونية",
    "country": "الجزائر",
    "description": "الجزائر · جامعة محمد بوضياف - المسيلة",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.54 0.13 140)",
    "officialLink": "https://www.univ-msila.dz"
  },
  {
    "name": "مجلة القانون والمجتمع",
    "country": "الجزائر",
    "description": "الجزائر · جامعة أحمد دراية - أدرار",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.54 0.13 140)",
    "officialLink": "https://www.asjp.cerist.dz/en/PresentationRevue/137"
  },
  {
    "name": "مجلة المحكمة العليا الجزائرية",
    "country": "الجزائر",
    "description": "الجزائر · المحكمة العليا الجزائرية",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.54 0.13 140)",
    "officialLink": "https://coursupreme.dz"
  },
  {
    "name": "مجلة جامعة الملك سعود - القانون والعلوم السياسية",
    "country": "السعودية",
    "description": "السعودية · كلية الحقوق والعلوم السياسية، جامعة الملك سعود",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.48 0.12 68)",
    "officialLink": "https://sjournals.sdl.edu.sa/ar/Journals/detail-journal-scope/34084003"
  },
  {
    "name": "مجلة جامعة طيبة للحقوق (Taibah University Journal of Law)",
    "country": "السعودية",
    "description": "السعودية · كلية الحقوق، جامعة طيبة",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.48 0.12 68)",
    "officialLink": "https://www.taibahu.edu.sa/taibah-university-journal-law"
  },
  {
    "name": "مجلة الأحكام (Sudan Law Journal)",
    "country": "السودان",
    "description": "السودان · السلطة القضائية السودانية",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.50 0.12 42)",
    "officialLink": "https://sj.gov.sd"
  },
  {
    "name": "مجلة العدل",
    "country": "السودان",
    "description": "السودان · وزارة العدل السودانية",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.50 0.12 42)",
    "officialLink": "https://moj.gov.sd"
  },
  {
    "name": "مجلة القانون والدراسات الإنسانية",
    "country": "السودان",
    "description": "السودان · غير محدد",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.50 0.12 42)",
    "officialLink": "https://jlse.journals.ekb.eg"
  },
  {
    "name": "مجلة جامعة شندي للبحوث والدراسات الشرعية والقانونية",
    "country": "السودان",
    "description": "السودان · عمادة البحث العلمي، جامعة شندي",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.50 0.12 42)",
    "officialLink": "https://journals.ush.edu.sd/law"
  },
  {
    "name": "مجلة قسطاس",
    "country": "السودان",
    "description": "السودان · رابطة طلبة كلية القانون، جامعة الخرطوم",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.50 0.12 42)",
    "officialLink": "https://www.qistasmagazine.com"
  },
  {
    "name": "مجلة آشور للعلوم القانونية والسياسية",
    "country": "العراق",
    "description": "العراق · الجمعية العراقية للعلوم القانونية",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.55 0.12 155)",
    "officialLink": "https://ashurjournal.com/"
  },
  {
    "name": "مجلة الحقوق",
    "country": "العراق",
    "description": "العراق · كلية القانون، الجامعة المستنصرية",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.55 0.12 155)",
    "officialLink": "https://mhj.uomustansiriyah.edu.iq"
  },
  {
    "name": "مجلة الرافدين للحقوق (Al-rafidain of Law)",
    "country": "العراق",
    "description": "العراق · كلية الحقوق، جامعة الموصل",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.55 0.12 155)",
    "officialLink": "https://alaw.mosuljournals.com/"
  },
  {
    "name": "مجلة العلوم القانونية",
    "country": "العراق",
    "description": "العراق · كلية القانون، جامعة بغداد",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.55 0.12 155)",
    "officialLink": "https://jols.uobaghdad.edu.iq/index.php/jols"
  },
  {
    "name": "مجلة الكوفة للعلوم القانونية والسياسية",
    "country": "العراق",
    "description": "العراق · كلية القانون، جامعة الكوفة",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.55 0.12 155)",
    "officialLink": "https://journal.uokufa.edu.iq/index.php/kjlps"
  },
  {
    "name": "مجلة المحقق الحلي للعلوم القانونية والسياسية",
    "country": "العراق",
    "description": "العراق · كلية القانون، جامعة بابل",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.55 0.12 155)",
    "officialLink": "http://law.uobabylon.edu.iq/"
  },
  {
    "name": "مجلة النهرين للعلوم القانونية",
    "country": "العراق",
    "description": "العراق · كلية الحقوق، جامعة النهرين",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.55 0.12 155)",
    "officialLink": "https://journal.nahrainlaw.org/"
  },
  {
    "name": "مجلة النور للدراسات القانونية",
    "country": "العراق",
    "description": "العراق · كلية القانون والعلوم السياسية، جامعة النور",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.55 0.12 155)",
    "officialLink": "https://jnls.alnoor.edu.iq/"
  },
  {
    "name": "مجلة تدوين للعلوم القانونية والسياسية",
    "country": "العراق",
    "description": "العراق · غير محدد",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.55 0.12 155)",
    "officialLink": "https://tadween.iku.edu.iq/"
  },
  {
    "name": "مجلة كلية القانون والعلوم السياسية",
    "country": "العراق",
    "description": "العراق · كلية القانون والعلوم السياسية، الجامعة العراقية",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.55 0.12 155)",
    "officialLink": "http://jlps.edu.iq/"
  },
  {
    "name": "مجلة الحقوق (Journal of Law)",
    "country": "الكويت",
    "description": "الكويت · مجلس النشر العلمي، جامعة الكويت",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.60 0.14 215)",
    "officialLink": "https://journals.ku.edu.kw/jol/index.php/jol"
  },
  {
    "name": "مجلة كلية القانون الكويتية العالمية (Kilaw Journal)",
    "country": "الكويت",
    "description": "الكويت · كلية القانون الكويتية العالمية",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.60 0.14 215)",
    "officialLink": "https://journal.kilaw.edu.kw"
  },
  {
    "name": "المجلة الإلكترونية للأبحاث القانونية",
    "country": "المغرب",
    "description": "المغرب · المعهد المغربي للإعلام العلمي والتقني (IMIST)",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.53 0.14 25)",
    "officialLink": "https://revues.imist.ma/index.php/RERJ"
  },
  {
    "name": "المجلة المغربية للدراسات القانونية والاقتصادية (REMEJE)",
    "country": "المغرب",
    "description": "المغرب · غير محدد",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.53 0.14 25)",
    "officialLink": "https://www.remeje.ma"
  },
  {
    "name": "مجلة إضاءات في الدراسات القانونية",
    "country": "المغرب",
    "description": "المغرب · غير محدد",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.53 0.14 25)",
    "officialLink": "https://idaat.net"
  },
  {
    "name": "مجلة الفقه والقانون (Majalah Droit)",
    "country": "المغرب",
    "description": "المغرب · غير محدد",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.53 0.14 25)",
    "officialLink": "https://www.majalah-droit.ma"
  },
  {
    "name": "مجلة القانون المغربي",
    "country": "المغرب",
    "description": "المغرب · دار السلام",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.53 0.14 25)",
    "officialLink": "https://www.darassalam.ma"
  },
  {
    "name": "مجلة قانونك الإلكترونية (9anonak)",
    "country": "المغرب",
    "description": "المغرب · غير محدد",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.53 0.14 25)",
    "officialLink": "https://www.9anonak.com"
  },
  {
    "name": "مجلة معالم قانونية",
    "country": "المغرب",
    "description": "المغرب · غير محدد",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.53 0.14 25)",
    "officialLink": "https://66b3fb1863f34.site123.me"
  },
  {
    "name": "مغرب القانون",
    "country": "المغرب",
    "description": "المغرب · غير محدد",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.53 0.14 25)",
    "officialLink": "https://maroclaw.com"
  },
  {
    "name": "مجلة ابن خلدون للدراسات والأبحاث (فرع القانون)",
    "country": "اليمن",
    "description": "اليمن · غير محدد",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.48 0.11 32)",
    "officialLink": "https://www.benkjournal.com"
  },
  {
    "name": "مجلة البحوث والدراسات القانونية",
    "country": "اليمن",
    "description": "اليمن · وزارة العدل اليمنية",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.48 0.11 32)",
    "officialLink": "https://almjalh.moj.gov.ye"
  },
  {
    "name": "مجلة القانون",
    "country": "اليمن",
    "description": "اليمن · جامعة عدن",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.48 0.11 32)",
    "officialLink": "https://www.aden-univ.net/mag10.aspx"
  },
  {
    "name": "مجلة جامعة الجزيرة العلمية (فرع القانون)",
    "country": "اليمن",
    "description": "اليمن · جامعة الجزيرة - إب",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.48 0.11 32)",
    "officialLink": "https://j.aljazeeraibb.edu.ye"
  },
  {
    "name": "مجلة جامعة الملكة أروى",
    "country": "اليمن",
    "description": "اليمن · جامعة الملكة أروى",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.48 0.11 32)",
    "officialLink": "https://journal.qau.edu.ye"
  },
  {
    "name": "مجلة جامعة صنعاء للعلوم الإنسانية (فرع القانون)",
    "country": "اليمن",
    "description": "اليمن · جامعة صنعاء",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.48 0.11 32)",
    "officialLink": "https://journals.su.edu.ye"
  },
  {
    "name": "المجلة القانونية التونسية",
    "country": "تونس",
    "description": "تونس · مركز الدراسات والبحوث والنشر",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.57 0.14 20)",
    "officialLink": "https://bibliotheque.arp.tn"
  },
  {
    "name": "مجلة الحقوق والإجراءات الجبائية",
    "country": "تونس",
    "description": "تونس · Juridoc تونس",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.57 0.14 20)",
    "officialLink": "https://juridoc.tn"
  },
  {
    "name": "مجلة المرافعات المدنية والتجارية",
    "country": "تونس",
    "description": "تونس · الدولة التونسية (تشريعية)",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.57 0.14 20)",
    "officialLink": "https://www.justice.gov.tn"
  },
  {
    "name": "المجلة الدولية للبحوث والدراسات القانونية (IJLRS)",
    "country": "دولية",
    "description": "دولية · غير محدد",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.53 0.12 260)",
    "officialLink": "https://vsrp.co.uk"
  },
  {
    "name": "مجلة القانون الدولي للدراسات البحثية",
    "country": "دولية",
    "description": "دولية · غير محدد",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.53 0.12 260)",
    "officialLink": "https://www.democraticac.de"
  },
  {
    "name": "مجلة القانون والأعمال الدولية (Revue Droit Des Affaires)",
    "country": "دولية",
    "description": "دولية · غير محدد",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.53 0.12 260)",
    "officialLink": "https://www.droitetentreprise.com"
  },
  {
    "name": "American Journal of International Law (AJIL)",
    "country": "دولية",
    "description": "دولية · American Society of International Law (ASIL)",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.53 0.12 260)",
    "officialLink": "https://www.cambridge.org/core/journals/american-journal-of-international-law"
  },
  {
    "name": "Arbitration International",
    "country": "دولية",
    "description": "دولية · Oxford University Press",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.53 0.12 260)",
    "officialLink": "https://academic.oup.com/arbitration"
  },
  {
    "name": "British Yearbook of International Law",
    "country": "دولية",
    "description": "دولية · Oxford University Press",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.53 0.12 260)",
    "officialLink": "https://academic.oup.com/bybil"
  },
  {
    "name": "CIFILE Journal of International Law (CJIL)",
    "country": "دولية",
    "description": "دولية · CIFILE",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.53 0.12 260)",
    "officialLink": "https://www.cifilejournal.com"
  },
  {
    "name": "Columbia Journal of Transnational Law",
    "country": "دولية",
    "description": "دولية · Columbia Law School",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.53 0.12 260)",
    "officialLink": "https://www.columbialawreview.org/jtl"
  },
  {
    "name": "European Journal of International Law (EJIL)",
    "country": "دولية",
    "description": "دولية · Oxford University Press",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.53 0.12 260)",
    "officialLink": "https://academic.oup.com/ejil"
  },
  {
    "name": "Hague Journal on the Rule of Law",
    "country": "دولية",
    "description": "دولية · Springer",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.53 0.12 260)",
    "officialLink": "https://www.springer.com/journal/40803"
  },
  {
    "name": "Harvard International Law Journal",
    "country": "دولية",
    "description": "دولية · Harvard Law School",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.53 0.12 260)",
    "officialLink": "https://journals.law.harvard.edu/ilj"
  },
  {
    "name": "Harvard Law Review",
    "country": "دولية",
    "description": "دولية · Harvard Law School",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.53 0.12 260)",
    "officialLink": "https://harvardlawreview.org"
  },
  {
    "name": "Human Rights Law Review",
    "country": "دولية",
    "description": "دولية · Oxford University Press",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.53 0.12 260)",
    "officialLink": "https://academic.oup.com/hrlr"
  },
  {
    "name": "Human Rights Quarterly",
    "country": "دولية",
    "description": "دولية · Johns Hopkins University Press",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.53 0.12 260)",
    "officialLink": "https://www.press.jhu.edu/journals/human-rights-quarterly"
  },
  {
    "name": "ICSID Review - Foreign Investment Law Journal",
    "country": "دولية",
    "description": "دولية · Oxford University Press",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.53 0.12 260)",
    "officialLink": "https://academic.oup.com/icsidreview"
  },
  {
    "name": "International & Comparative Law Quarterly (ICLQ)",
    "country": "دولية",
    "description": "دولية · British Institute of International and Comparative Law",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.53 0.12 260)",
    "officialLink": "https://www.cambridge.org/core/journals/international-and-comparative-law-quarterly"
  },
  {
    "name": "Journal of Conflict and Security Law",
    "country": "دولية",
    "description": "دولية · Oxford University Press",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.53 0.12 260)",
    "officialLink": "https://academic.oup.com/jcsl"
  },
  {
    "name": "Journal of International Criminal Justice",
    "country": "دولية",
    "description": "دولية · Oxford University Press",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.53 0.12 260)",
    "officialLink": "https://academic.oup.com/jicj"
  },
  {
    "name": "Journal of International Economic Law",
    "country": "دولية",
    "description": "دولية · Oxford University Press",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.53 0.12 260)",
    "officialLink": "https://academic.oup.com/jiel"
  },
  {
    "name": "Leiden Journal of International Law",
    "country": "دولية",
    "description": "دولية · Cambridge University Press",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.53 0.12 260)",
    "officialLink": "https://www.cambridge.org/core/journals/leiden-journal-of-international-law"
  },
  {
    "name": "Michigan Journal of International Law",
    "country": "دولية",
    "description": "دولية · University of Michigan Law School",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.53 0.12 260)",
    "officialLink": "https://repository.law.umich.edu/mjil"
  },
  {
    "name": "Modern Law Review",
    "country": "دولية",
    "description": "دولية · Wiley-Blackwell",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.53 0.12 260)",
    "officialLink": "https://onlinelibrary.wiley.com/journal/14682230"
  },
  {
    "name": "Netherlands International Law Review",
    "country": "دولية",
    "description": "دولية · Springer",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.53 0.12 260)",
    "officialLink": "https://www.springer.com/journal/40802"
  },
  {
    "name": "Oxford Journal of Legal Studies",
    "country": "دولية",
    "description": "دولية · Oxford University Press",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.53 0.12 260)",
    "officialLink": "https://academic.oup.com/ojls"
  },
  {
    "name": "Stanford Journal of International Law",
    "country": "دولية",
    "description": "دولية · Stanford Law School",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.53 0.12 260)",
    "officialLink": "https://law.stanford.edu/stanford-journal-of-international-law-sjil"
  },
  {
    "name": "Yale Law Journal",
    "country": "دولية",
    "description": "دولية · Yale Law School",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.53 0.12 260)",
    "officialLink": "https://www.yalelawjournal.org"
  },
  {
    "name": "مجلة الدراسات الفقهية والقانونية",
    "country": "سلطنة عمان",
    "description": "سلطنة عمان · المعهد العالي للقضاء، سلطنة عُمان",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.61 0.13 50)",
    "officialLink": "https://jjls.hji.edu.om"
  },
  {
    "name": "مجلة جامعة السلطان قابوس للدراسات القانونية (SQULSJ)",
    "country": "سلطنة عمان",
    "description": "سلطنة عمان · كلية الحقوق، جامعة السلطان قابوس",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.61 0.13 50)",
    "officialLink": "https://squlsj.squ.edu.om"
  },
  {
    "name": "مجلة التحكيم السورية",
    "country": "سوريا",
    "description": "سوريا · مكتب منصور للمحاماة (بالتعاون مع شركة آمالي)",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.58 0.12 250)",
    "officialLink": "https://syrian-arbitration.com/"
  },
  {
    "name": "مجلة القانون",
    "country": "سوريا",
    "description": "سوريا · غير محدد",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.58 0.12 250)",
    "officialLink": "https://www.syrianlaw.com"
  },
  {
    "name": "مجلة بحوث جامعة حلب - سلسلة العلوم القانونية والشرعية",
    "country": "سوريا",
    "description": "سوريا · جامعة حلب",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.58 0.12 250)",
    "officialLink": "http://researchjournal.alepuniv.edu.sy/"
  },
  {
    "name": "مجلة جامعة البعث - سلسلة العلوم القانونية",
    "country": "سوريا",
    "description": "سوريا · جامعة البعث",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.58 0.12 250)",
    "officialLink": "https://journal.albaath-univ.edu.sy/"
  },
  {
    "name": "مجلة جامعة اللاذقية (تشرين سابقاً) للبحوث والدراسات العلمية - سلسلة العلوم الاقتصادية والقانونية",
    "country": "سوريا",
    "description": "سوريا · جامعة اللاذقية",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.58 0.12 250)",
    "officialLink": "https://journal.latakia-univ.edu.sy/"
  },
  {
    "name": "مجلة جامعة دمشق للعلوم القانونية",
    "country": "سوريا",
    "description": "سوريا · جامعة دمشق",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.58 0.12 250)",
    "officialLink": "http://journal.damascusuniversity.edu.sy/index.php/legj"
  },
  {
    "name": "المجلة العصرية للدراسات القانونية (Modern Journal of Legal Studies)",
    "country": "فلسطين",
    "description": "فلسطين · الكلية العصرية الجامعية - رام الله",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.46 0.12 150)",
    "officialLink": "https://mucjournals.muc.edu.ps"
  },
  {
    "name": "مجلة الأبحاث القانونية",
    "country": "فلسطين",
    "description": "فلسطين · جامعة النجاح الوطنية (كلية الحقوق)",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.46 0.12 150)",
    "officialLink": "https://journals.najah.edu"
  },
  {
    "name": "مجلة الحقوق والعلوم السياسية",
    "country": "فلسطين",
    "description": "فلسطين · جامعة فلسطين التقنية - خضوري (كلية الحقوق)",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.46 0.12 150)",
    "officialLink": "https://www.ptuk.edu.ps"
  },
  {
    "name": "مجلة بيت المقدس للقانون",
    "country": "فلسطين",
    "description": "فلسطين · جامعة القدس (كلية الحقوق)",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.46 0.12 150)",
    "officialLink": "https://www.alquds.edu"
  },
  {
    "name": "مجلة ديوان الجريدة الرسمية للأبحاث القانونية",
    "country": "فلسطين",
    "description": "فلسطين · ديوان الجريدة الرسمية - فلسطين",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.46 0.12 150)",
    "officialLink": "https://journal.ogb.gov.ps"
  },
  {
    "name": "المجلة الدولية للقانون (International Review of Law - IRL)",
    "country": "قطر",
    "description": "قطر · كلية القانون، جامعة قطر",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.54 0.16 355)",
    "officialLink": "https://journals.qu.edu.qa/index.php/IRL"
  },
  {
    "name": "المجلة القضائية - Al-Majallah al-Qada'iyah",
    "country": "لبنان",
    "description": "لبنان · دار صادر للنشر (أسسها يوسف صادر)",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.67 0.13 35)",
    "officialLink": "https://www.saderlegal.com/"
  },
  {
    "name": "مجلة جيل الأبحاث القانونية المعمقة",
    "country": "لبنان",
    "description": "لبنان · مركز جيل للبحث العلمي",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.67 0.13 35)",
    "officialLink": "http://journals.jilrc.com/legal-depth-research"
  },
  {
    "name": "مجلة لبنان",
    "country": "لبنان",
    "description": "لبنان · Legal Agenda (المفكرة القانونية)",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.67 0.13 35)",
    "officialLink": "https://legal-agenda.com/"
  },
  {
    "name": "مجلة محكمة (Mahkama)",
    "country": "لبنان",
    "description": "لبنان · غير محدد",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.67 0.13 35)",
    "officialLink": "https://mahkama.net"
  },
  {
    "name": "BAU Journal of Legal Studies - مجلة الدراسات القانونية",
    "country": "لبنان",
    "description": "لبنان · كلية الحقوق والعلوم السياسية، جامعة بيروت العربية (BAU)",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.67 0.13 35)",
    "officialLink": "https://digitalcommons.bau.edu.lb/lsjournal/"
  },
  {
    "name": "Proche-Orient, Études juridiques",
    "country": "لبنان",
    "description": "لبنان · كلية الحقوق والعلوم السياسية، جامعة القديس يوسف (USJ)",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.67 0.13 35)",
    "officialLink": "https://e-journals.usj.edu.lb/poej"
  },
  {
    "name": "USEK Law Journal - Revue juridique de l'USEK",
    "country": "لبنان",
    "description": "لبنان · كلية الحقوق والعلوم السياسية، جامعة الروح القدس - الكسليك (USEK)",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.67 0.13 35)",
    "officialLink": "https://www.usek.edu.lb/"
  },
  {
    "name": "مجلة أبحاث قانونية",
    "country": "ليبيا",
    "description": "ليبيا · كلية القانون، جامعة سرت",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.60 0.12 210)",
    "officialLink": "https://journal.su.edu.ly"
  },
  {
    "name": "مجلة البحوث القانونية",
    "country": "ليبيا",
    "description": "ليبيا · كلية القانون، جامعة مصراتة",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.60 0.12 210)",
    "officialLink": "https://jlr.misuratau.edu.ly"
  },
  {
    "name": "مجلة الحقوق للعلوم الشرعية والقانونية (Al-haq Journal)",
    "country": "ليبيا",
    "description": "ليبيا · غير محدد",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.60 0.12 210)",
    "officialLink": "https://www.al-haqjournal.ly"
  },
  {
    "name": "مجلة العلوم القانونية",
    "country": "ليبيا",
    "description": "ليبيا · كلية القانون، جامعة المرقب",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.60 0.12 210)",
    "officialLink": "https://jls.elmergib.edu.ly"
  },
  {
    "name": "مجلة القانون",
    "country": "ليبيا",
    "description": "ليبيا · كلية القانون، جامعة طرابلس",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.60 0.12 210)",
    "officialLink": "https://journals.uot.edu.ly"
  },
  {
    "name": "مجلة دراسات قانونية",
    "country": "ليبيا",
    "description": "ليبيا · كلية القانون، جامعة بنغازي",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.60 0.12 210)",
    "officialLink": "https://journals.uob.edu.ly"
  },
  {
    "name": "مجلة كلية الشريعة والقانون - الجامعة الأسمرية",
    "country": "ليبيا",
    "description": "ليبيا · الجامعة الأسمرية الإسلامية - زليتن",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.60 0.12 210)",
    "officialLink": "https://journals.asmarya.edu.ly"
  },
  {
    "name": "المجلة الدولية للفقه والقضاء والتشريع (IJDJL)",
    "country": "مصر",
    "description": "مصر · نادي قضاة مصر",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.60 0.13 28)",
    "officialLink": "https://ijdjl.journals.ekb.eg"
  },
  {
    "name": "مجلة البحوث القانونية والاقتصادية",
    "country": "مصر",
    "description": "مصر · كلية الحقوق، جامعة المنصورة",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.60 0.13 28)",
    "officialLink": "https://mjle.journals.ekb.eg"
  },
  {
    "name": "مجلة الحقوق للبحوث القانونية والاقتصادية",
    "country": "مصر",
    "description": "مصر · كلية الحقوق، جامعة الإسكندرية",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.60 0.13 28)",
    "officialLink": "https://lalexu.journals.ekb.eg"
  },
  {
    "name": "مجلة الدراسات القانونية",
    "country": "مصر",
    "description": "مصر · غير محدد",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.60 0.13 28)",
    "officialLink": "https://maal.journals.ekb.eg"
  },
  {
    "name": "مجلة العلوم القانونية والاقتصادية",
    "country": "مصر",
    "description": "مصر · كلية الحقوق، جامعة عين شمس",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.60 0.13 28)",
    "officialLink": "https://jelc.journals.ekb.eg"
  },
  {
    "name": "مجلة القانون والاقتصاد",
    "country": "مصر",
    "description": "مصر · كلية الحقوق، جامعة القاهرة",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.60 0.13 28)",
    "officialLink": "https://mle.journals.ekb.eg"
  },
  {
    "name": "مجلة المحاماة الإلكترونية",
    "country": "مصر",
    "description": "مصر · المركز الإعلامي لنقابة المحامين المصرية",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.60 0.13 28)",
    "officialLink": "https://egyls.com"
  },
  {
    "name": "مجلة محكمة النقض (المجلة القضائية)",
    "country": "مصر",
    "description": "مصر · محكمة النقض المصرية",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.60 0.13 28)",
    "officialLink": "https://ccj.journals.ekb.eg"
  },
  {
    "name": "المجلة الموريتانية للدراسات والبحوث",
    "country": "موريتانيا",
    "description": "موريتانيا · المركز الموريتاني للدراسات والبحوث القانونية والاقتصادية والاجتماعية (CMERJES)",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.52 0.11 70)",
    "officialLink": "https://cmerjes.org"
  },
  {
    "name": "مجلة المرافعات المدنية الموريتانية",
    "country": "موريتانيا",
    "description": "موريتانيا · الدولة الموريتانية (تشريعية)",
    "countLabel": "رابط رسمي",
    "color": "oklch(0.52 0.11 70)",
    "officialLink": "https://www.onamauritanie.mr"
  }
]
