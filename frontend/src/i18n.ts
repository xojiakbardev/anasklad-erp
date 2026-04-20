import i18next from "i18next";
import { initReactI18next } from "react-i18next";

const uz = {
  common: {
    login: "Kirish",
    logout: "Chiqish",
    register: "Ro'yxatdan o'tish",
    email: "Email",
    password: "Parol",
    full_name: "To'liq ism",
    company: "Kompaniya nomi",
    save: "Saqlash",
    cancel: "Bekor qilish",
    delete: "O'chirish",
    loading: "Yuklanmoqda...",
    error: "Xatolik yuz berdi",
    refresh: "Yangilash",
    test: "Tekshirish",
  },
  nav: {
    dashboard: "Bosh sahifa",
    products: "Mahsulotlar",
    orders: "Buyurtmalar",
    stocks: "Qoldiqlar",
    finance: "Moliya",
    integrations: "Integratsiyalar",
    settings: "Sozlamalar",
    reports: "Hisobotlar",
  },
  integrations: {
    title: "Integratsiyalar",
    subtitle: "Marketplace do'konlaringizni ulang va real-time boshqaring",
    add_uzum: "Uzum integratsiyasini qo'shish",
    connected_shops: "Ulangan do'konlar",
    no_integrations: "Hali birorta integratsiya yo'q",
    no_integrations_hint: "Uzum seller kabinetingizdan API token oling va shu yerga ulang",
    token: "API token",
    token_hint: "Uzum seller kabinet → Sozlamalar → API kalitlari",
    label: "Belgi",
    label_hint: "Masalan: 'Asosiy do'kon' yoki 'Egasi: Aziz'",
    connect: "Ulash",
    status_active: "Faol",
    status_error: "Xato",
    status_disabled: "O'chirilgan",
    last_checked: "Oxirgi tekshirish",
    shops_count: "{{count}} ta do'kon",
    delete_confirm: "Haqiqatan ham bu integratsiyani o'chirmoqchimisiz? Barcha sinxronlangan ma'lumotlar yo'qoladi.",
  },
  login: {
    title: "Anasklad-ERP",
    subtitle: "Ipak yo'li terminali",
    welcome: "Xush kelibsiz",
    no_account: "Hali ro'yxatdan o'tmaganmisiz?",
    create_account: "Hisob yarating",
    signin_cta: "Kirish",
  },
  register: {
    title: "Hisob yarating",
    subtitle: "Anasklad-ERP bilan boshlang",
    have_account: "Hisobingiz bormi?",
    signin: "Kirish",
    register_cta: "Ro'yxatdan o'tish",
  },
  errors: {
    network: "Tarmoq xatosi — internetni tekshiring",
    invalid_credentials: "Email yoki parol noto'g'ri",
    email_taken: "Bu email allaqachon ro'yxatdan o'tgan",
    token_expired: "Sessiya tugadi, qayta kiring",
  },
};

i18next.use(initReactI18next).init({
  resources: { uz: { translation: uz } },
  lng: "uz",
  fallbackLng: "uz",
  interpolation: { escapeValue: false },
});

export default i18next;
