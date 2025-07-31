<p align="center">
  <a href="#"><img title="Open Source" src="https://img.shields.io/badge/Open%20Source-%E2%9D%A4-green?style=for-the-badge"></a>
  <a href="https://www.python.org/"><img title="Python" src="https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge"></a>
  <a href="https://developer.mozilla.org/en-US/docs/Web/JavaScript"><img title="JavaScript" src="https://img.shields.io/badge/JavaScript-yellow?style=for-the-badge&logo=javascript&logoColor=black"></a>
  <img title="TypeScript" src="https://img.shields.io/badge/TypeScript-4.x-blue?style=for-the-badge&logo=typescript&logoColor=white">
  <a href="https://github.com/iamunixtz/JSNinja/stargazers"><img title="Stars" src="https://img.shields.io/github/stars/iamunixtz/JSNinja?style=for-the-badge"></a>
  <a href="https://github.com/iamunixtz/JSNinja/issues"><img title="Issues" src="https://img.shields.io/github/issues/iamunixtz/JSNinja?style=for-the-badge"></a>
</p>

<div align="center">
  <h1>JSNinja</h1>
  <p>
    
**Hunting Bugs in JavaScript!**
  <img width="1280" height="720" alt="jsninja" src="https://github.com/user-attachments/assets/023e4ebb-755e-495c-ac01-209035166b02" />

  </p>
</div>


**JSNinja is a powerful, open-source tool for security researchers, bug bounty hunters, and developers. It analyzes JavaScript files and web applications to extract sensitive information—such as API keys and tokens—URLs, and endpoints. It also includes JS monitoring with diff alerts. Built with Flask and CLI support, JSNinja features notification integrations (Telegram, Discord), exportable results, and more.**


##  Features

### JSNinja Features

| Feature                                | Description                                                                                                           |
| -------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
|  **Sensitive Information Detection** | Detects secrets like AWS, Stripe, GitHub, Telegram, etc. <br> Severity levels: **Critical**, **High**, **Medium**     |
| **URL & API Endpoint Extraction**   | Extracts absolute and relative URLs <br> Detects **REST**, **GraphQL**, and **webhook** endpoints                     |
| **JavaScript Monitoring**           | Tracks JavaScript changes with diffs <br> Sends alerts via **Telegram** or **Discord**                                |
| **Notifications**                   | Integrates with **Telegram** and **Discord** <br> Notifies on scan completion or critical findings                    |
| **Export Capabilities**             | Export scan results to **CSV** or **JSON**                                                                            |
| **Web Interface**                   | Flask-powered dashboard for managing projects, scans, and monitors                                                    |
| **Bulk & CLI Support**             | Scan single or multiple URLs from `.txt` files <br> Stores results in **SQLite (rezon.db)**                           |
|  **Security Features**              | Rate-limited login <br> Rotating **User‑Agents** <br> Logging to `rezon.log` <br> Code formatting with `jsbeautifier` |



## Installation

### Requirements
- Python 3.9+
- Dependencies in `requirements.txt`

### Setup
```bash
sudo apt update && sudo apt install git python3 python3-pip -y

git clone https://github.com/iamunixtz/JSNinja.git
cd JSNinja

pip3 install -r requirements.txt

# (Optional) Add CLI to PATH:
sudo cp jsninja /usr/local/bin
jsninja -h
````

##  Web Interface
![JSNinja Demo](https://github.com/user-attachments/assets/2942e656-e3f7-4b0e-b09a-3518d2b336d7)

```bash
python3 app.py
```

Access the UI at [http://localhost:5000](http://localhost:5000).

Default credentials:

* Username: `jsninja`
* Password: `jsninja`

###  JSNinja Features

| Feature                                | Description                                                                                                           |
| -------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
|  **Sensitive Information Detection** | Detects secrets like AWS, Stripe, GitHub, Telegram, etc. <br> Severity levels: **Critical**, **High**, **Medium**     |
|  **URL & API Endpoint Extraction**   | Extracts absolute and relative URLs <br> Detects **REST**, **GraphQL**, and **webhook** endpoints                     |
|  **JavaScript Monitoring**           | Tracks JavaScript changes with diffs <br> Sends alerts via **Telegram** or **Discord**                                |
|  **Notifications**                   | Integrates with **Telegram** and **Discord** <br> Notifies on scan completion or critical findings                    |
|  **Export Capabilities**             | Export scan results to **CSV** or **JSON**                                                                            |
|  **Web Interface**                   | Flask-powered dashboard for managing projects, scans, and monitors                                                    |
|  **Bulk & CLI Support**             | Scan single or multiple URLs from `.txt` files <br> Stores results in **SQLite (rezon.db)**                           |
|  **Security Features**              | Rate-limited login <br> Rotating **User‑Agents** <br> Logging to `rezon.log` <br> Code formatting with `jsbeautifier` |

**Optional**: To bypass Cloudflare restrictions:

```bash
pip3 install cloudscraper
```

Then update fetch logic to use `cloudscraper`.

## Usage

### CLI

```bash
python3 jsninja.py \
  -u https://example.com/script.js \
  --secrets --urls \
  --output_file results.txt
```

**Options:**

* `-u, --url`: Specify a JS URL
* `--secrets`: Extract secrets
* `--urls`: Extract URLs
* `-o, --output_file`: Save results
* `-h, --help`: Display help

### Web UI

1. Log into the dashboard
2. Create or open a project
3. Scan via URL input, `.txt` file upload, or JS paste
4. Set up monitors to track changes
5. Enable Telegram/Discord in settings
6. Export results via results screen

## Supported Patterns

| Pattern               | Example Match                                          |
| --------------------- | ------------------------------------------------------ |
| AWS Access Key ID     | `AKIA[0-9A-Z]{16}`                                     |
| AWS Secret Access Key | `[A-Za-z0-9/+=]{40}`                                   |
| GitHub Token          | `ghp_[A-Za-z0-9]{36}` or `github_pat_[A-Za-z0-9_]{82}` |
| Stripe Live Token     | `sk_live_[A-Za-z0-9]{24}`                              |
| Twilio Account SID    | `AC[A-Za-z0-9]{32}`                                    |
| Telegram Bot Token    | `\d{8,10}:[A-Za-z0-9_-]{35}`                           |
| JWT Token             | `eyJ[A-Za-z0-9_-]+\.[\w-]+\.[\w-]+`                    |


## API Endpoint Detection

* REST: patterns like `/api/v1/…`, `/users`, `/auth/…`
* GraphQL: `/graphql`
* Webhook endpoints: `/webhook`, `/hook`, `/callback`

## JavaScript Monitoring

* SHA‑256-based change detection
* Unified diff output
* Alerts on monitored JS changes
* Interval monitoring (e.g. every 5 minutes)
* History tracking & export


## Notifications

Configured via settings page:

* **Telegram**: Bot token and chat ID
* **Discord**: Webhook URL

**Alerts for scan results, critical findings, and script changes include details and severity.**


##  Troubleshooting

* **403 Forbidden**: Install `cloudscraper` for enhanced bypass capability
* **404 Not Found**: Ensure valid URLs; filter out pages with `null` segments
* **SSL Issues**: Use `pip3 install certifi`; configuration fallback available
* **Dynamic Content**: Consider Selenium or Playwright for JS-rendered pages


## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/xyz`)
3. Commit your changes (`git commit -m "Add feature xyz"`)
4. Push to branch and open a Pull Request

Report bugs or request enhancements via GitHub Issues. See the Code of Conduct for guidelines.


## Disclaimer 
**Bro am not programmer or developer just vibe coding**

