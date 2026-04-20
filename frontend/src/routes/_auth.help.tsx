import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { useTranslation } from "react-i18next";

import { IkatStripe } from "@/components/IkatStripe";

export const Route = createFileRoute("/_auth/help")({
  component: HelpPage,
});

interface FaqEntry {
  q: { uz: string; ru: string };
  a: { uz: string; ru: string };
}

const FAQ: FaqEntry[] = [
  {
    q: {
      uz: "Uzum API tokenini qayerdan olaman?",
      ru: "Где получить API-токен Uzum?",
    },
    a: {
      uz: "seller.uzum.uz → Sozlamalar → API kalitlari → 'Yangi token yaratish'. Token'ga 'SKU_READ' va 'SKU_UPDATE' ruxsatlarini bering. Token bir marta ko'rsatiladi — ehtiyot bo'lib nusxa oling.",
      ru: "seller.uzum.uz → Настройки → API-ключи → 'Создать новый токен'. Выдайте права 'SKU_READ' и 'SKU_UPDATE'. Токен показывается один раз — сразу скопируйте.",
    },
  },
  {
    q: {
      uz: "Sinxronizatsiya qancha tez-tez ishlaydi?",
      ru: "Как часто выполняется синхронизация?",
    },
    a: {
      uz: "FBS buyurtmalar: har 2 daqiqa. Moliya (sotuv/xarajat): har 10 daqiqa. Katalog: har 30 daqiqa. Har qanday vaqt integratsiya kartasida 'Sync' tugmasini bosib qo'lda ishga tushirsa bo'ladi.",
      ru: "FBS-заказы: каждые 2 минуты. Финансы (продажи/расходы): каждые 10 минут. Каталог: каждые 30 минут. В любое время можно нажать 'Sync' на карточке интеграции.",
    },
  },
  {
    q: {
      uz: "Sof foyda qanday hisoblanadi?",
      ru: "Как считается чистая прибыль?",
    },
    a: {
      uz: "Sof foyda = sotuv narxi − Uzum komissiyasi − logistika xizmati − tannarx. Ushbu qiymatlarni Uzum o'zi /finance/orders endpointida qaytaradi — biz ularni saqlab, jamlab ko'rsatamiz.",
      ru: "Чистая прибыль = цена продажи − комиссия Uzum − логистика − себестоимость. Эти значения Uzum возвращает в /finance/orders — мы их сохраняем и агрегируем.",
    },
  },
  {
    q: {
      uz: "Tannarxni qanday kiritaman?",
      ru: "Как вводить себестоимость?",
    },
    a: {
      uz: "Uzum Seller kabinetida har SKU uchun 'purchasePrice' maydoni bor — shu qiymat avtomatik olinadi. Keyingi versiyalarda Anasklad ichida qo'lda tahrir qilish imkoniyati qo'shiladi.",
      ru: "В кабинете Uzum у каждого SKU есть поле 'purchasePrice' — оно подтягивается автоматически. В следующих версиях появится редактирование внутри Anasklad.",
    },
  },
  {
    q: {
      uz: "ABC-analiz nimani ko'rsatadi?",
      ru: "Что показывает ABC-анализ?",
    },
    a: {
      uz: "Mahsulotlar daromad ulushi bo'yicha 4 guruhga ajratiladi: A — eng yaxshi 80% daromad keltiradigan SKU'lar (odatda ~20%), B — keyingi 15%, C — qolgan 5%, N — umuman sotilmagan. A guruhga ko'proq e'tibor bering.",
      ru: "Товары делятся на 4 группы по доле выручки: A — SKU, дающие 80% выручки (обычно ~20% товаров), B — следующие 15%, C — остальные 5%, N — не продавалось. Фокус — на группе A.",
    },
  },
  {
    q: {
      uz: "FBO va FBS farqi?",
      ru: "Разница между FBO и FBS?",
    },
    a: {
      uz: "FBO (Fulfillment by Uzum) — tovar Uzum omborida yotadi, ular o'zi jo'natadi. FBS (Fulfillment by Seller) — tovar sizning omboringizda, buyurtma kelganda siz pickup-pointga eltib berasiz.",
      ru: "FBO (Fulfillment by Uzum) — товар на складе Uzum, они сами доставляют. FBS (Fulfillment by Seller) — товар у вас, при заказе вы везёте в пункт приёма.",
    },
  },
  {
    q: {
      uz: "Buyurtmani qanday tasdiqlayman?",
      ru: "Как подтвердить заказ?",
    },
    a: {
      uz: "Buyurtmalar sahifasida (kanban) CREATED ustunidan buyurtmani oching → 'Tasdiqlash' tugmasi. Buyurtma PACKING holatiga o'tadi va etiketka chop etishga tayyor bo'ladi.",
      ru: "На странице Заказов (канбан) откройте заказ из колонки CREATED → кнопка 'Подтвердить'. Заказ перейдёт в PACKING и будет готов к печати этикетки.",
    },
  },
  {
    q: {
      uz: "Etiketka qayerdan chop etiladi?",
      ru: "Где печатается этикетка?",
    },
    a: {
      uz: "Tasdiqlangan (PACKING) buyurtma drawer'ida '🖨 Etiketka' tugmasi — PDF yangi tabda ochiladi. Standart o'lcham: 58x40 mm (LARGE).",
      ru: "В панели подтверждённого (PACKING) заказа — кнопка '🖨 Этикетка' открывает PDF в новой вкладке. Стандартный размер: 58x40 мм (LARGE).",
    },
  },
  {
    q: {
      uz: "Ma'lumot keshlanadimi yoki har safar Uzum'dan olinadi?",
      ru: "Данные кешируются или запрашиваются у Uzum каждый раз?",
    },
    a: {
      uz: "Barcha ma'lumot bizning PostgreSQL bazamizda saqlanadi. Uzum'ga faqat sync vaqtida murojaat qilamiz — bu tezlik va rate-limit'ni tejash uchun.",
      ru: "Все данные хранятся в нашей PostgreSQL. К Uzum обращаемся только во время sync — ради скорости и экономии rate-limit.",
    },
  },
  {
    q: {
      uz: "Ma'lumotlarim xavfsizmi?",
      ru: "Мои данные в безопасности?",
    },
    a: {
      uz: "Uzum tokeni Fernet (AES-128 CBC + HMAC) bilan shifrlangan holda saqlanadi. Har so'rov HTTPS orqali. Parollar Argon2 bilan hash qilingan. Kelajakda 2FA qo'shamiz.",
      ru: "Токен Uzum хранится зашифрованным (Fernet / AES-128 CBC + HMAC). Все запросы по HTTPS. Пароли — Argon2. В будущем добавим 2FA.",
    },
  },
];

function HelpPage() {
  const { t, i18n } = useTranslation();
  const [query, setQuery] = useState("");
  const lang = (i18n.language === "ru" ? "ru" : "uz") as "uz" | "ru";

  const filtered = query
    ? FAQ.filter(
        (f) =>
          f.q[lang].toLowerCase().includes(query.toLowerCase()) ||
          f.a[lang].toLowerCase().includes(query.toLowerCase()),
      )
    : FAQ;

  return (
    <div className="h-full overflow-auto">
      <header className="px-8 pt-8 pb-4 border-b border-[var(--color-border-hair)]">
        <div className="label-micro mb-2">HELP</div>
        <h1 className="display-title text-4xl">{t("help.title")}</h1>
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={t("help.search")}
          className="ak-input w-full max-w-md mt-4"
        />
      </header>

      <div className="max-w-3xl px-8 py-8 space-y-4">
        <div className="label-micro mb-2">{t("help.faq")} · {filtered.length}</div>
        {filtered.map((entry, idx) => (
          <FaqItem
            key={idx}
            question={entry.q[lang]}
            answer={entry.a[lang]}
            index={idx + 1}
          />
        ))}
        {filtered.length === 0 && (
          <div className="p-12 text-center text-[var(--color-fg-muted)]">
            Hech narsa topilmadi / Ничего не найдено
          </div>
        )}
      </div>
    </div>
  );
}

function FaqItem({
  question,
  answer,
  index,
}: {
  question: string;
  answer: string;
  index: number;
}) {
  const [open, setOpen] = useState(false);
  return (
    <div className="relative border border-[var(--color-border-hair)] rounded-sm">
      {open && <IkatStripe className="absolute left-0 top-0 bottom-0" />}
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className={"w-full text-left py-4 pr-5 flex items-start gap-4 cursor-pointer " + (open ? "pl-9" : "pl-5")}
      >
        <span className="ledger-number text-xs text-[var(--color-fg-dim)] w-6 shrink-0 mt-0.5">
          {index.toString().padStart(2, "0")}
        </span>
        <span className="flex-1 font-medium">{question}</span>
        <span className="text-[var(--color-fg-muted)]">{open ? "−" : "+"}</span>
      </button>
      {open && (
        <div className="pl-[60px] pr-5 pb-5 text-sm text-[var(--color-fg-muted)] leading-relaxed">
          {answer}
        </div>
      )}
    </div>
  );
}
