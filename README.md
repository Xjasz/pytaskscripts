# 🛠️ PyTaskScripts

**pytaskscripts** is a modular Python project designed to collect, manage, and run standalone or grouped utility scripts from a single, unified CLI interface.

Whether you're scraping websites, generating keys, automating browser tasks, or building crypto tools — this repo lets you keep everything centralized and scalable.

Stake Referral Link: [https://stake.us/?c=KGW4Lep4](https://stake.us/?c=KGW4Lep4)


---

## 🚀 Current Tasks

### ✅ `btc_task`
Runs Bitcoin-related generators and scanners.

- Modes:
  - `KEY`: Generate keys from input seeds and scan against known addresses
  - `PASS`: Generate passphrases
- Pass types:
  - `WORD`: Wordlist-based
  - `SEED`: Seed/rng-based
- Fast, low-level crypto tools

---

### ✅ `crypto_monitor`
Monitors **Twitter** and **Truth Social** posts from key accounts and alerts on crypto keywords.

- Sends alerts via **email** and **SMS**
- Uses headless browser scraping
- Prevents duplicate notifications
- Supports optional carrier gateway testing

---

### ✅ `stake_task`
Scrapes and analyzes **Crash** and **Slide** game data from Stake.us.

- Modes: `CRASH`, `SLIDE`, `BOTH`
- Supports CSV, JSON, and MySQL output
- Headless browser automation with Selenium

---

## 🧰 How It Works

- Central `main.py` is the entrypoint for all task execution
- Configuration for each module lives in `config.json`
- Logs are dynamically created per task in `logs/<task>.log`
- All modules follow a unified logger pattern

---

## 🔧 Usage

```bash
# General syntax
python main.py <task> --log_mode [append|overwrite]

# Examples
python main.py stake_task --log_mode append
python main.py btc_task --log_mode overwrite
python main.py crypto_monitor --log_mode append
