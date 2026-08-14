export const IRAQI_GOVERNORATES = [
  { slug: "baghdad", nameEn: "Baghdad", nameAr: "بغداد" },
  { slug: "basra", nameEn: "Basra", nameAr: "البصرة" },
  { slug: "nineveh", nameEn: "Nineveh", nameAr: "نينوى" },
  { slug: "erbil", nameEn: "Erbil", nameAr: "أربيل" },
  { slug: "sulaymaniyah", nameEn: "Sulaymaniyah", nameAr: "السليمانية" },
  { slug: "dohuk", nameEn: "Dohuk", nameAr: "دهوك" },
  { slug: "kirkuk", nameEn: "Kirkuk", nameAr: "كركوك" },
  { slug: "anbar", nameEn: "Anbar", nameAr: "الأنبار" },
  { slug: "diyala", nameEn: "Diyala", nameAr: "ديالى" },
  { slug: "saladin", nameEn: "Saladin", nameAr: "صلاح الدين" },
  { slug: "babil", nameEn: "Babil", nameAr: "بابل" },
  { slug: "karbala", nameEn: "Karbala", nameAr: "كربلاء" },
  { slug: "najaf", nameEn: "Najaf", nameAr: "النجف" },
  { slug: "wasit", nameEn: "Wasit", nameAr: "واسط" },
  { slug: "maysan", nameEn: "Maysan", nameAr: "ميسان" },
  { slug: "dhi_qar", nameEn: "Dhi Qar", nameAr: "ذي قار" },
  { slug: "muthanna", nameEn: "Muthanna", nameAr: "المثنى" },
  { slug: "qadisiyyah", nameEn: "Qadisiyyah", nameAr: "القادسية" },
];

export const CATEGORIES = [
  {
    id: "job",
    labelKey: "opportunities.categories.job",
    subs: [
      { id: "online", labelKey: "opportunities.subs.online" },
      { id: "onsite", labelKey: "opportunities.subs.onsite" },
    ],
  },
  {
    id: "course",
    labelKey: "opportunities.categories.course",
    subs: [
      { id: "paid", labelKey: "opportunities.subs.paid" },
      { id: "free", labelKey: "opportunities.subs.free" },
    ],
  },
  {
    id: "volunteer",
    labelKey: "opportunities.categories.volunteer",
    subs: null,
  },
];

export const ROLE_LABELS = {
  lawyer: { en: "Lawyer", ar: "محامي" },
  doctor: { en: "Doctor", ar: "طبيب" },
  engineer: { en: "Engineer", ar: "مهندس" },
  teacher: { en: "Teacher", ar: "معلم" },
  developer: { en: "Developer", ar: "مطور" },
  designer: { en: "Designer", ar: "مصمم" },
  accountant: { en: "Accountant", ar: "محاسب" },
  marketing: { en: "Marketing", ar: "تسويق" },
  translator: { en: "Translator", ar: "مترجم" },
  nurse: { en: "Nurse", ar: "ممرض" },
  sales: { en: "Sales", ar: "مبيعات" },
  photographer: { en: "Photographer", ar: "مصور" },
  writer: { en: "Writer", ar: "كاتب" },
  driver: { en: "Driver", ar: "سائق" },
  hr: { en: "HR", ar: "موارد بشرية" },
  data: { en: "Data Analyst", ar: "محلل بيانات" },
  customer_support: { en: "Customer Support", ar: "دعم العملاء" },
};

export function roleLabel(slug, isArabic) {
  if (!slug) return "";
  const entry = ROLE_LABELS[slug];
  if (!entry) return slug;
  return isArabic ? entry.ar : entry.en;
}
