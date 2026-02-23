# HKRE App

A web scraping application for extracting property development information from Hong Kong government websites (SRPE OPIP). Data is stored in Google Sheets and PDFs are uploaded to Google Drive.

## Features

- Automated scraping of property developments (**t18m** and **non-t18m**)
- Compares scraped data to existing rows in the **devm** sheet; only downloads PDFs when content (SB, RT, PO) has changed
- Granular PDF downloads: e.g. only the specific Price Order or Sales Brochure file that changed, not the whole category
- Register of Transactions (RT): special handling for legacy (no RT in DB) vs. stored RT; RT downloads piggyback when PO or SB changes
- PDF upload to Google Drive and PDF→CSV conversion (Tabula-Java) for PO/PR/RT files
- New/updated rows inserted into **devm t18m** or **devm non-t18m**; text wrap applied to note columns

## Project Structure

```
HKRE App/
├── config/              # Configuration (settings.py, credentials)
├── src/
│   ├── main.py          # Entry point, run loop
│   ├── scraping/        # Browser, property processing, file_download
│   ├── extractors/      # sales_brochure, register_of_transactions, price_orders
│   ├── google_services/ # Sheets, Drive, Docs, auth
│   └── converters/      # PDF to CSV (Tabula wrapper)
├── data/                # Local download dirs (t18m / non-t18m)
├── main.py              # Convenience launcher (runs src/main.py)
└── requirements.txt
```

## Quick Start

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Prerequisites**
   - **Python 3.9+**
   - **Java** (for Tabula-Java PDF→CSV)
   - **Google Chrome**
   - Google API credentials: place `credentials.json` in `config/` (or set path in config). Use `.env` for optional overrides (e.g. `CHROME_EXE_PATH`).

3. **Run**
   From project root:
   ```bash
   python main.py
   ```
   Or:
   ```bash
   python src/main.py
   ```

## Configuration

- `config/settings.py` — timeouts, Chrome path, URLs (T18M / non-T18M), data dir, credentials path.
- Environment: copy `.env.example` to `.env` if you use one; credentials and run folder IDs are typically set there or in code.

## Requirements (requirements.txt)

- **Web:** selenium, selenium-stealth  
- **Data:** pandas, numpy  
- **Google:** google-api-python-client, google-auth*, gspread  
- **Other:** requests, python-dotenv  

Java is required separately for Tabula-based PDF conversion.
