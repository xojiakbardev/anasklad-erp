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
    back: "Orqaga",
    next: "Keyingi",
    skip: "O'tkazib yuborish",
    close: "Yopish",
    help: "Yordam",
  },
  nav: {
    dashboard: "Bosh sahifa",
    products: "Mahsulotlar",
    orders: "Buyurtmalar",
    stocks: "Qoldiqlar",
    finance: "Moliya",
    reports: "Hisobotlar",
    integrations: "Integratsiyalar",
    settings: "Sozlamalar",
    help: "Yordam",
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
    delete_confirm:
      "Haqiqatan ham bu integratsiyani o'chirmoqchimisiz? Barcha sinxronlangan ma'lumotlar yo'qoladi.",
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
    uzum_auth: "Uzum tokeni noto'g'ri yoki muddati tugagan",
    uzum_no_shops: "Ushbu token bog'langan do'kon topilmadi",
    unknown: "Kutilmagan xatolik. Qaytadan urinib ko'ring",
  },
  onboarding: {
    step1_title: "Xush kelibsiz!",
    step1_body:
      "Anasklad-ERP Uzum seller'lar uchun zamonaviy boshqaruv tizimi. 3 qadamdan o'tib, birinchi ma'lumotlaringizni ko'ring.",
    step2_title: "Uzum tokenini oling",
    step2_body:
      "Uzum Seller kabinet → Sozlamalar → API kalitlari bo'limida yangi token yarating. Token 'SKU_READ' va 'SKU_UPDATE' ruxsatlarini o'z ichiga olishi kerak.",
    step3_title: "Do'konni ulang",
    step3_body:
      "Integratsiyalar sahifasida tokenni kiriting — do'konlar avtomatik yuklanadi.",
    step4_title: "Sync qiling",
    step4_body:
      "Integratsiya kartasida 'Sync' tugmasini bosing. Mahsulotlar, buyurtmalar va moliya birdaniga sinxronlanadi.",
    start: "Boshlash",
    to_integrations: "Integratsiyalarga o'tish",
  },
  help: {
    title: "Yordam markazi",
    search: "Qidirish...",
    faq: "Ko'p beriladigan savollar",
  },
};

const ru: typeof uz = {
  common: {
    login: "Войти",
    logout: "Выйти",
    register: "Регистрация",
    email: "Email",
    password: "Пароль",
    full_name: "Полное имя",
    company: "Название компании",
    save: "Сохранить",
    cancel: "Отмена",
    delete: "Удалить",
    loading: "Загрузка...",
    error: "Произошла ошибка",
    refresh: "Обновить",
    test: "Проверить",
    back: "Назад",
    next: "Далее",
    skip: "Пропустить",
    close: "Закрыть",
    help: "Помощь",
  },
  nav: {
    dashboard: "Главная",
    products: "Товары",
    orders: "Заказы",
    stocks: "Остатки",
    finance: "Финансы",
    reports: "Отчёты",
    integrations: "Интеграции",
    settings: "Настройки",
    help: "Помощь",
  },
  integrations: {
    title: "Интеграции",
    subtitle: "Подключайте магазины и управляйте ими в реальном времени",
    add_uzum: "Подключить Uzum",
    connected_shops: "Подключённые магазины",
    no_integrations: "Интеграций пока нет",
    no_integrations_hint: "Получите API-токен в кабинете Uzum и подключите его здесь",
    token: "API-токен",
    token_hint: "Кабинет Uzum → Настройки → API-ключи",
    label: "Название",
    label_hint: "Например: 'Главный магазин' или 'Владелец: Азиз'",
    connect: "Подключить",
    status_active: "Активна",
    status_error: "Ошибка",
    status_disabled: "Отключена",
    last_checked: "Последняя проверка",
    delete_confirm:
      "Действительно удалить эту интеграцию? Все синхронизированные данные будут потеряны.",
  },
  login: {
    title: "Anasklad-ERP",
    subtitle: "Терминал Шёлкового пути",
    welcome: "Добро пожаловать",
    no_account: "Ещё нет аккаунта?",
    create_account: "Создать аккаунт",
    signin_cta: "Войти",
  },
  register: {
    title: "Создайте аккаунт",
    subtitle: "Начните работу с Anasklad-ERP",
    have_account: "Уже есть аккаунт?",
    signin: "Войти",
    register_cta: "Зарегистрироваться",
  },
  errors: {
    network: "Ошибка сети — проверьте интернет",
    invalid_credentials: "Неверный email или пароль",
    email_taken: "Этот email уже зарегистрирован",
    token_expired: "Сессия истекла, войдите заново",
    uzum_auth: "Токен Uzum недействителен или истёк",
    uzum_no_shops: "К токену не привязан ни один магазин",
    unknown: "Неожиданная ошибка. Попробуйте снова",
  },
  onboarding: {
    step1_title: "Добро пожаловать!",
    step1_body:
      "Anasklad-ERP — современная система управления для Uzum-селлеров. Пройдите 3 шага и увидите первые данные.",
    step2_title: "Получите токен Uzum",
    step2_body:
      "Кабинет Uzum Seller → Настройки → API-ключи. Создайте токен с правами 'SKU_READ' и 'SKU_UPDATE'.",
    step3_title: "Подключите магазин",
    step3_body:
      "На странице Интеграции введите токен — магазины подтянутся автоматически.",
    step4_title: "Синхронизируйте",
    step4_body:
      "Нажмите 'Sync' на карточке интеграции — товары, заказы и финансы синхронизируются за раз.",
    start: "Начать",
    to_integrations: "К интеграциям",
  },
  help: {
    title: "Центр помощи",
    search: "Поиск...",
    faq: "Часто задаваемые вопросы",
  },
};

const STORAGE_KEY = "anasklad.lang";

export type Language = "uz" | "ru";

export function getSavedLanguage(): Language {
  const saved = localStorage.getItem(STORAGE_KEY);
  return saved === "ru" ? "ru" : "uz";
}

export function setLanguage(lang: Language): void {
  localStorage.setItem(STORAGE_KEY, lang);
  void i18next.changeLanguage(lang);
  document.documentElement.lang = lang;
}

i18next.use(initReactI18next).init({
  resources: {
    uz: { translation: uz },
    ru: { translation: ru },
  },
  lng: getSavedLanguage(),
  fallbackLng: "uz",
  interpolation: { escapeValue: false },
});

export default i18next;
