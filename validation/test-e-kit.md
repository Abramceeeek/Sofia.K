# Test E kit: call guide and message version (D70)

> **Postponed until v0 exists (D86).** Test E runs with a working demo after Test B, and before any B2B-specific build work. Don't send these yet. Before it runs, Claude adds a short demo section at the close of the call guide.

**What this is:** the Test E questions from `discovery-interviews.md` in two shareable forms:
- **A. Call guide** (30 min), for all 5 contacts;
- **B. By message**, for agencies that prefer to answer in writing or by voice note, in English, Russian and Uzbek.

Both keep the same rules: **past behaviour only, no pitching until the close**, and no money is discussed or taken (CLAUDE.md gates).

It also has **C. The intro line** for hotel staff contacts, asking them to introduce you to a manager or budget holder.

- **Published copy with copy buttons:** https://claude.ai/artifact/LZQEYVFmjWUXXpVMLx7qu8 (private to you; you copy the texts from it, so nobody else needs access).
- **Translations:** the Russian and Uzbek texts are Claude's translations. **Check them before sending** (0.25 h, already in the Test E hours).

**Rules that still apply**
- Work on personal time and a personal device, and **never use employer contacts or information**.
- Before approaching a public body (a borough, BID or tourism board), check that your secondary-employment rules allow it.
- If someone answers by **voice note**, transcribe it, then delete the audio (CLAUDE.md guardrail).
- Store answers only in `validation/raw/` (git-ignored) and in the results sheet's `Discovery` tab.

---

## A. Call guide (30 min)

**Before (15 min)**
- Read their website: what do they already offer guests or clients (concierge, guides, partners, tours)?
- Fill the organisation row in `results-sheet.xlsx` → `Discovery` (type, role, date).

**Opening (1 min)**
> Thanks for making the time. I'm researching how [hotels / visitor services / travel agencies] help people find things to do in London. It's a small independent project, and I'm not selling anything today. It takes about 25 minutes. Is it OK if I take notes? I won't record, and I won't quote you by name without asking.

**Context (3 min)**
1. What's your role, and roughly how many guests or visitors do you deal with in a week?

**Last time (10 min)**

2. Tell me about the last time a guest asked you what to do or where to go. What did they ask? What did you give them?
3. What happened afterwards? Did you hear how it went?
4. When did a recommendation last go wrong, or a guest come back disappointed? What happened?

**What they use and spend today (8 min)**

5. What do you use now: your own knowledge, printed guides, an app, partners, a concierge service? Who keeps it up to date?
6. Have you paid for anything like that in the last year: guides, concierge software, local partnerships, content? What did it cost, and who signed it off?
7. Do local venues or tour companies pay you, or give your guests discounts? How does that work?

**How they judge it (5 min)**

8. How do you know whether a recommendation was good? Do reviews, repeat stays or complaints show it?
9. *Tourism bodies only:* What do you measure for visitors (spend, dwell time, spreading people beyond the hotspots)? What did you last commission for visitor experience, and how did the budget decision work?

**Uzbek agencies:** replace questions 2–9 with questions 2–7 of the message version (B). In Russian or Uzbek, read them from the translated text.

**Follow-ups that keep it factual**
- "Can you give me an example?" · "What happened then?" · "What did that cost?" · "Who signed it off?"
- Avoid "Would you use…?" and "Do you like the idea…?". Answers about the future don't count.

**Close (3 min, only now)**

10. In two sentences: "a planner that learns what makes each person feel good on a day out and plans around it (moments, not landmarks), with a personal plan for each guest."
11. Who else should I talk to about this?
12. Would you be open to trying it with a few guests later, unpaid, when it exists? **Write down the exact answer.**
13. *Hotel and serviced-apartment staff:* read the intro line (C).

**After (15 min):** record in `Discovery`:
- current solution;
- **current spend** (£ a month; 0 if none);
- **budget owner named?** (Y/N);
- the strongest pain quote, word for word;
- **commitment**: none / introduction to the budget owner / agreed to an unpaid pilot.

**Read-out (D57):** worth building toward if **≥ 2 of 5** already spend money or staff time on this, **and ≥ 2 of 5** give an introduction or agree to an unpaid pilot. Polite interest doesn't count.

---

## B. By message (agencies)

Send **message 1** first. Send **message 2** only after they have answered; it holds the description, so nothing is pitched before the questions.

### English

```text id=m1-en
Hello [name], I'm Abram, based in London. I'm researching how travel agencies help clients plan their free days in London. It's a small independent project and I'm not selling anything. If you have 10 minutes, could you answer these by message? A voice note is fine too, and short answers are perfect.

1. What's your role, and roughly how many clients did you send to London in the last 12 months?
2. Think of the last client you sent to London. What did they do on their free days, and how did they choose?
3. What did they complain about afterwards, or wish they had known?
4. Do you sell tours, guides or day plans for London? What do you pay for them, and what do you charge?
5. What do you pay each month for tools or services (booking systems, guides, marketing)? Who approves that spending?
6. The last time you paid a supplier abroad, was it by card or bank transfer? A company card or a personal one? In which currency?
7. What did your bank or accountant need for that payment (a contract, an invoice, an acceptance act)? Has your accountant ever withheld tax on a payment to a foreign company?

Thank you! I'll use your answers only for this research, and I won't quote you by name without asking.
```

```text id=m2-en
Thank you, this is really useful. In two sentences, here is what I'm building: a planner that learns what makes each person feel good on a day out and plans around it (moments, not landmarks), with a personal plan for each client.

Would you be open to trying it with a few clients later, unpaid, when it exists? If someone else decides on spending like this, could you introduce me to them? And is there anyone else I should ask?
```

### Русский (Claude's translation: check before sending)

```text id=m1-ru
Здравствуйте, [имя]! Меня зовут Абрам, я живу в Лондоне. Я изучаю, как турагентства помогают клиентам планировать свободные дни в Лондоне. Это небольшой независимый проект, и я ничего не продаю. Если у вас есть 10 минут, не могли бы вы ответить на эти вопросы в сообщении? Можно голосовым, коротких ответов достаточно.

1. Какая у вас должность и сколько примерно клиентов вы отправили в Лондон за последние 12 месяцев?
2. Вспомните последнего клиента, которого вы отправили в Лондон. Чем он занимался в свободные дни и как выбирал, куда пойти?
3. На что он жаловался после поездки или что хотел бы знать заранее?
4. Продаёте ли вы экскурсии, услуги гидов или планы на день в Лондоне? Сколько вы за них платите и сколько берёте с клиента?
5. Сколько вы платите в месяц за инструменты или сервисы (системы бронирования, гиды, маркетинг)? Кто утверждает эти расходы?
6. Как вы в последний раз платили поставщику за границей: картой или банковским переводом? Картой компании или личной? В какой валюте?
7. Какие документы потребовали банк или бухгалтер для этого платежа (договор, инвойс, акт выполненных работ)? Удерживал ли ваш бухгалтер когда-нибудь налог с платежа иностранной компании?

Спасибо! Ваши ответы я использую только для этого исследования и не буду цитировать вас по имени без вашего согласия.
```

```text id=m2-ru
Спасибо, это очень полезно. Коротко о том, что я делаю: планировщик, который узнаёт, от чего каждому человеку хорошо в поездке, и строит день вокруг этого (моменты, а не достопримечательности), с личным планом для каждого клиента.

Были бы вы готовы позже попробовать его бесплатно с несколькими клиентами, когда он будет готов? Если решения о таких расходах принимает кто-то другой, не могли бы вы нас познакомить? И с кем ещё мне стоит поговорить?
```

### O'zbekcha (Claude's translation: check before sending)

```text id=m1-uz
Assalomu alaykum, [ism]! Mening ismim Abram, Londonda yashayman. Sayyohlik agentliklari mijozlarga Londondagi bo'sh kunlarini rejalashtirishda qanday yordam berishini o'rganyapman. Bu kichik mustaqil loyiha, men hech narsa sotmayman. Agar 10 daqiqa vaqtingiz bo'lsa, quyidagi savollarga xabar orqali javob bera olasizmi? Ovozli xabar ham bo'ladi, qisqa javoblar yetarli.

1. Lavozimingiz qanday va so'nggi 12 oyda Londonga taxminan nechta mijoz yubordingiz?
2. Londonga yuborgan oxirgi mijozingizni eslang. U bo'sh kunlarida nima qildi va qayerga borishni qanday tanladi?
3. Safardan keyin nimadan shikoyat qildi yoki nimani oldindan bilishni xohlardi?
4. Londonda ekskursiyalar, gid xizmatlari yoki kunlik rejalar sotasizmi? Ular uchun qancha to'laysiz va mijozdan qancha olasiz?
5. Har oy vositalar yoki xizmatlar (bron qilish tizimlari, gidlar, marketing) uchun qancha to'laysiz? Bu xarajatlarni kim tasdiqlaydi?
6. Oxirgi marta chet eldagi yetkazib beruvchiga qanday to'lov qildingiz: karta orqalimi yoki bank o'tkazmasi orqalimi? Kompaniya kartasimi yoki shaxsiy kartami? Qaysi valyutada?
7. Bu to'lov uchun bank yoki buxgalteringiz qanday hujjatlarni so'radi (shartnoma, invoys, bajarilgan ishlar dalolatnomasi)? Buxgalteringiz hech qachon xorijiy kompaniyaga to'lovdan soliq ushlab qolganmi?

Rahmat! Javoblaringizni faqat shu tadqiqot uchun ishlataman va ruxsatingizsiz ismingizni keltirmayman.
```

```text id=m2-uz
Rahmat, bu juda foydali. Nima qilayotganimni qisqacha aytsam: har bir odamga sayohatda nima yoqishini o'rganib, kunni shunga qarab rejalashtiradigan dastur (mashhur joylar emas, balki lahzalar), har bir mijoz uchun shaxsiy reja bilan.

Dastur tayyor bo'lgach, uni bir nechta mijozingiz bilan bepul sinab ko'rishga tayyormisiz? Agar bunday xarajatlar bo'yicha qarorni boshqa kishi qabul qilsa, meni u bilan tanishtira olasizmi? Yana kim bilan gaplashishim kerak?
```

---

## C. The intro line (hotel staff contacts)

Use it at the end of a call with front-desk, concierge or guest-services staff, or as a follow-up message. An introduction to the budget holder counts as a **commitment** in the read-out.

```text id=intro-en
If you're not the person who decides on guest services or the budget for them, could you introduce me to the manager or budget holder? A two-line email or WhatsApp intro is perfect, and I'll keep it to 25 minutes, with no sales pitch.
```

The recruiting message in `discovery-interviews.md` now ends with the same ask for hotel contacts.
