# Kherwar Calendar — Django Database Edition

এটি Kherwar Calendar-এর Admin ↔ Database ↔ Calendar UI starter system।

## 1. Install

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## 2. URLs

- Calendar: `http://127.0.0.1:8000/`
- Custom Admin: `http://127.0.0.1:8000/admin-panel/`
- Django Admin: `http://127.0.0.1:8000/django-admin/`

Custom Admin staff login না করলে Login page-এ যাবে।

## 3. Lunar rule implemented

- New Moon date নিজে কোনো মাসের 1 তারিখ নয়।
- New Moon-এর **পরের Gregorian day = Lunar Day 1**।
- পরবর্তী New Moon-এর আগের দিন পর্যন্ত day count চলবে।
- প্রতিটি NewMoon record-এ `month_order` দেওয়া যায়; তাই 12/13 month year অনুযায়ী ক্রম নির্ধারণ করা যায়।
- 1900–2024 HistoricalDate থাকলে সেই Gregorian date-এর Santali/Bengali date **automatic calculation-এর উপর priority পায়**।
- Lunar Event = month_order + lunar day; ফলে Gregorian date প্রতি বছর আলাদা হলেও event lunar date-এ থাকবে।

## 4. 12/13 month order

বর্তমান default sequence:

1. ᱢᱟᱜᱽ — MAG
2. ᱯᱷᱟᱹᱜᱩᱱ — FAGUN
3. ᱪᱟᱹᱛ — CHAIT
4. ᱵᱟᱹᱭᱥᱟᱹᱠ — BAISAK
5. ᱡᱷᱮᱸᱴ — JHET
6. ᱵᱟᱺᱰᱭᱟᱹ ᱡᱷᱮᱴ — BADYA JHET (extra)
7. ᱟᱥᱟᲅ — ASAR
8. ᱥᱟᱱ — SAN
9. ᱵᱷᱟᱫᱚᱨ — BHADOR
10. ᱫᱟᱸᱥᱟᱸᱭ — DANSAY
11. ᱥᱚᱨᱦᱟᱭ — SARHAY
12. ᱟᱸᱜᱷᱟᱲ — ANGHAR
13. ᱯᱩᱥ — PUS

12-month year-এ 6 নম্বর extra month ব্যবহার করবেন না; পরের মাসগুলোর order year-specific NewMoon records অনুযায়ী সেট করবেন।

## 5. Bulk Historical CSV format

```csv
gregorian,bengali_day,bengali_month,bengali_year,santali_day,santali_month,santali_year,note
2024-01-01,17,Poush,1430,1,ᱯᱩᱥ,5123,source
```

## 6. Important

1900–2024-এর missing Santali dates এই project নিজে বানিয়ে দেয় না। নির্ভরযোগ্য source থেকে data import করতে হবে। New Moon date-ও verified astronomical/calendar source থেকে দিতে হবে।

## 7. পুরনো database-এ official 13 month sequence বসানো

```bash
python manage.py seed_kherwar --reset-names
```

এটি আপনার month table-এর 1–13 order-এর নামকে বর্তমানে নির্ধারিত sequence-এ বসাবে। **চালানোর আগে backup নিন**, কারণ এটি month names overwrite করবে।

## 8. 1900–2024 bulk import

Admin Panel → Historical → Import Historical CSV ব্যবহার করুন। Template: `sample_data/historical_dates_template.csv`

## 9. New Moon bulk import

Admin Panel → Months → Import Moon CSV। প্রতিটি New Moon record-এ `month_order` দেওয়ার ফলে সেই New Moon-এর পরের দিন থেকে ওই month order-এর দিন 1 হবে।

## 10. Calendar priority

1. HistoricalDate (1900–2024 verified/manual data)
2. NewMoon + month_order (automatic lunar day)
3. Original Calendar fallback logic (যদি DB data না থাকে)

এই fallback ইচ্ছাকৃত—অসম্পূর্ণ database-এর কারণে Calendar blank না রাখার জন্য।

## লোকাল Image Upload
Admin Panel-এর Advertisement, Lunar Event ও Solar Event-এ **📁 Local Image** দিয়ে PC/লোকাল Drive থেকে ছবি নির্বাচন করা যাবে। Upload হওয়ার পরে Django নিজে `/media/calendar_images/...` Image URL তৈরি করে। Advertisement-এর **Target URL** আলাদাভাবে দিতে হবে—ব্যবহারকারী বিজ্ঞাপনের ছবিতে ক্লিক করলে ওই URL-এ যাবে।

লোকাল development-এ media URL কাজ করবে `DEBUG=True` অবস্থায়।
