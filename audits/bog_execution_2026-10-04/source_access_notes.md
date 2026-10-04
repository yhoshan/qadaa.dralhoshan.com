# ملاحظات الوصول إلى مصادر ديوان المظالم الرسمية

> تاريخ الفحص: 2026-10-04. هذه الملاحظات توثق الوصول ولا تمثل إدخالًا للبيانات.

## المصدر والحزمة

- المصدر المعتمد: [ديوان المظالم](https://www.bog.gov.sa/) — نطاق حكومي رسمي `bog.gov.sa`، المملكة العربية السعودية.
- الحزمة المقدمة: `audits/bog_execution_2026-10-04/bog_makanz_execution_pack_v2.json`.
- حُظر توسيع النطاق خارج الحزمة، وحُظر إدخال الأخبار والترجمات والمحتوى الإعلامي والتعريفي.

## ما ثبت مباشرة من الموقع الرسمي

### المبادئ التي قررتها المحكمة الإدارية العليا

تُظهر [صفحة المبادئ](https://www.bog.gov.sa/knowledge-center/PrinciplesBlogs/Pages/default.aspx) أربع مجموعات رسمية:

1. [الأعوام 1439–1440–1441 هـ](https://www.bog.gov.sa/knowledge-center/PrinciplesBlogs/1439-1440-1441)
2. [عام 1442 هـ](https://www.bog.gov.sa/knowledge-center/PrinciplesBlogs/1442)
3. [عام 1443 هـ](https://www.bog.gov.sa/knowledge-center/PrinciplesBlogs/1443)
4. [عام 1444 هـ](https://www.bog.gov.sa/knowledge-center/PrinciplesBlogs/1444)

### قرارات هيئة التدقيق مجتمعة

تقرر [الصفحة الرسمية](https://www.bog.gov.sa/knowledge-center/decisions/Pages/default.aspx) أنها تضم الكشاف والقرارات الموضوعية والمبادئ المستخلصة، وتربط إلى الملف الرسمي:

- [قرارات هيئة التدقيق مجتمعة — print_1436.pdf](https://www.bog.gov.sa/knowledge-center/decisions/Documents/print_1436.pdf)

### السوابق القضائية الإدارية

أثبتت نتيجة بحث الويب الرسمية أن الملف الرسمي القديم يحوّل إلى المسار الحالي، والملف قابل للقراءة عبر أداة الجلب:

- [السوابق القضائية كاملة](https://www.bog.gov.sa/knowledge-center/JudicialBlogs/A1402-1436/Documents/%D8%A7%D9%84%D8%B3%D9%88%D8%A7%D8%A8%D9%82%20%D8%A7%D9%84%D9%82%D8%B6%D8%A7%D8%A6%D9%8A%D8%A9%20%D9%83%D8%A7%D9%85%D9%84%D8%A9%20(PDF)/%D8%A7%D9%84%D8%B3%D9%88%D8%A7%D8%A8%D9%82%20%D8%A7%D9%84%D9%82%D8%B6%D8%A7%D8%A6%D9%8A%D8%A9%20%D9%83%D8%A7%D9%85%D9%84%D8%A9.pdf)

والنص الرسمي المستخرج يذكر أن المدونة تشمل **1,336 سابقة قضائية** مستخلصة من **4,594 حكمًا إداريًا** للأعوام **1402–1436 هـ**.

## حالة الوصول التقني

- صفحات الفهارس الرسمية متاحة عبر أداة `fetch` وتثبت العناوين والبنية، لكن محتوى القوائم والمرفقات الديناميكية لا يظهر في HTML المستخرج.
- اتصال HTTP المباشر من بيئتي التنفيذية ومن البيئة البديلة إلى `www.bog.gov.sa:443` يفشل حاليًا بـ `SSL_ERROR_SYSCALL` أو مهلة اتصال.
- محاولة المتصفح السحابي أعطت `ERR_CONNECTION_CLOSED`.
- لهذا السبب لا يجوز اختلاق روابط ملفات أو إدخال أحكام فردية من دون إمكانية التحقق من الملف الرسمي أو رابط المجلد الرسمي.

## روابط المجموعات المحددة في الحزمة

- [المدونات القضائية](https://www.bog.gov.sa/knowledge-center/JudicialBlogs/Pages/default.aspx)
- [الأحكام 1402–1426](https://www.bog.gov.sa/knowledge-center/JudicialBlogs/AA1402-1426/Pages/default.aspx)
- [الأحكام 1439](https://www.bog.gov.sa/knowledge-center/JudicialBlogs/1439/Pages/default.aspx)
- [الأحكام الإدارية في الملكية الفكرية](https://www.bog.gov.sa/knowledge-center/JudicialBlogs/intellectual-property/Pages/default.aspx)
- [مبادئ المحكمة الإدارية العليا 1444](https://www.bog.gov.sa/knowledge-center/PrinciplesBlogs/1444/Pages/default.aspx)
- [الأنظمة القضائية](https://www.bog.gov.sa/knowledge-center/JudicialSystems/Pages/JudicalSystems.aspx)
- [قواعد ولوائح مجلس القضاء الإداري](https://www.bog.gov.sa/AdministrativeJusticeCouncil/RulesAndRegulations/Pages/default.aspx)

## قاعدة التنفيذ

لا تدخل قاعدة البيانات إلا وحدة فردية لها رابط رسمي مباشر أو رابط مجموعة رسمية موثقة، وبعد التحقق من عدم تكرارها بالرابط أو أرقام الحكم/القضية أو العنوان المطبع والسنة/المجموعة.
