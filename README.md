# MI_PRD1

# Reizināšanas spēle

**26. grupa, PR1**

---

## Spēles apraksts

Šī ir divu spēlētāju skaitļu reizināšanas spēle, kurā piedalās cilvēks un dators (izmantojot mākslīgā intelekta algoritmus).

Spēles sākumā cilvēks izvēlas **sākuma skaitli no 8 līdz 18**. Katrs spēlētājs sāk ar **0 punktiem**, un spēlētāji veic gājienus pārmaiņus. Katrā gājienā pašreizējais skaitlis tiek reizināts ar **2, 3 vai 4**.

Punktu aprēķins ir šāds:
- Ja iegūtais skaitlis ir **pāra**, spēlētājs zaudē **1 punktu**;
- Ja iegūtais skaitlis ir **nepāra**, spēlētājs iegūst **+1 punktu**;
- Ja iegūtais skaitlis **beidzas ar 0 vai 5**, **bankai** tiek pievienots **1 punkts**.

Kad reizinātais skaitlis sasniedz vai pārsniedz **1200**, spēle beidzas. Pēdējais spēlētājs saņem **bankas punktus**. Uzvar spēlētājs ar vairāk punktiem. Ja punktu skaits ir vienāds, rezultāts ir **neizšķirts**.

---

## Projekta struktūra

```
.gitignore              # Faili, kas netiek iekļauti versiju kontroles sistēmā
LICENSE                 # Projekta licence (MIT)
README.md               # Šis faila apraksts
speles_logika.py        # Spēles loģika, GUI, AI algoritmi, heiristika un noteikumi
```

---

## Lietošana

Lai palaistu spēli, pārliecinieties, ka Python 3 ir uzstādīts (to var pārbaudīt ar komandu `python --version` vai `python3 --version`).
---

### ⚠️ Piezīme par GitHub Codespaces

Šī programma izmanto `customtkinter`, kas veido grafisku logu. **GitHub Codespaces neatbalsta grafiskās lietotāja saskarnes (GUI)**, tāpēc spēli **nav iespējams palaist Codespaces vidē**.

Lai spēli palaistu pareizi, tā jāizpilda **lokāli uz datora**, kur ir pieejams grafiskais ekrāns (Windows, Mac, vai Linux ar GUI).

Ja tomēr mēģināsiet palaist Codespaces vidē, saņemsiet kļūdu:
_tkinter.TclError: no display name and no $DISPLAY environment variable


1. Pārliecinieties, ka esat projektā ar failu `speles_logika.py`.
2. Ja izmantojat Codespace vai citu jaunu vidi, pirms spēles palaišanas uzstādiet nepieciešamo bibliotēku:

```bash
pip install customtkinter
```
3. Pēc tam palaidiet spēli ar komandu:

```bash
python speles_logika.py
```

Ekrānā būs iespēja:
- izvēlēties spēles sākuma skaitli (no 8 līdz 18),
- izvēlēties, kurš sāk spēli (cilvēks vai dators),
- izvēlēties mākslīgā intelekta algoritmu (Minimax vai Alpha-Beta).

---

## Licence

Šis projekts ir licencēts ar **MIT licenci**. Jūs varat brīvi izmantot, modificēt un izplatīt šo programmu personīgiem vai izglītojošiem mērķiem.
