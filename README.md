# SENTINEL
### IP Threat Intelligence & Reputation Analyzer — OSINT Reconnaissance Toolkit

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Linux-lightgrey?style=flat-square)
![OSINT](https://img.shields.io/badge/Type-OSINT-blueviolet?style=flat-square)

> 🛡️ Part of the **DOMINI Suite** — a two-tool passive OSINT framework.  
> SENTINEL analyzes IPs. [DOMINUS](https://github.com/KristinaSabitova/dominus) analyzes domains.  
> Together they map the full attack surface of any target.

---

## What is SENTINEL?

SENTINEL is a passive OSINT threat intelligence tool focused on **IP addresses**. Given an IP, it aggregates reputation data, geolocation, abuse history, active threat feeds, cloud provider context, and Tor/VPN detection — then calculates a transparent **Threat Score from 0 to 100** and generates a fully standalone HTML report with an interactive geolocalization map.

Where [DOMINUS](https://github.com/KristinaSabitova/dominus) asks *"how exposed is this organization?"*, **SENTINEL asks "is this IP a threat?"**

---

## What does it find?

| Phase | Data collected |
|-------|---------------|
| **Geolocation** | Country, city, coordinates, ASN, ISP, organization — via ip-api.com (no key required) |
| **Abuse** | Total abuse reports, confidence score, attack categories, last report date — via AbuseIPDB |
| **Threat Feeds** | Presence in AlienVault OTX pulses, indicator types, threat actor associations |
| **Ports** | Open TCP services and version banners via nmap |
| **Cloud Detection** | Identifies if the IP belongs to AWS, Azure, GCP, or Cloudflare using public IP range files — no API needed |
| **Tor Detection** | Real-time lookup against dan.me.uk/torlist — detects active Tor exit nodes instantly |

---

## What does the Threat Score mean?

Every finding contributes weighted points to a **Threat Score from 0 to 100**:

| Score | Level | What it means |
|-------|-------|---------------|
| 0–25 | 🟢 Low | Clean IP, no abuse history, legitimate provider |
| 26–50 | 🟡 Medium | Some abuse reports, or Tor/VPN detected |
| 51–75 | 🔴 High | Multiple abuse categories, appears in threat feeds |
| 76–100 | 🔥 Critical | Active attacker IP, high-confidence abuse, multiple threat feed hits |

**Each point is explained.** The report shows exactly which finding contributed what score — no black boxes, no guessing.

---

## What is it useful for?

**SOC analysts** use it to triage alerts — when an IP appears in logs, SENTINEL tells you in seconds if it's a known threat, a Tor exit node, a cloud provider, or a clean residential address.

**Incident responders** use it during active investigations to profile attacker infrastructure — where are they coming from, what provider, are they using anonymization, have others reported them.

**Penetration testers** use it to verify their own infrastructure isn't flagged before an engagement — running a test from a burned IP defeats the purpose.

**Threat hunters** use it to enrich indicators of compromise (IOCs) — turning a raw IP from a SIEM alert into a full threat profile.

**Students and researchers** use it to understand how threat intelligence platforms work and what data is publicly available about any IP address.

**Real-world scenarios where SENTINEL adds value:**

- An IP appears repeatedly in your SSH logs — is it a scanner, a bot, or a targeted attacker?
- You receive a phishing email — what does the sending IP reveal about the infrastructure?
- A client reports suspicious traffic — SENTINEL profiles the source in seconds
- You're building a blocklist — SENTINEL validates which IPs are genuinely malicious
- You want to know if a server you're about to connect to is flagged in threat databases

---

## Understanding the results: a real example

**Target: 185.220.101.1**

```
Threat Score  : 32 / 100 — MEDIUM
Country       : Germany · Brandenburg
ASN           : AS60729 Stiftung Erneuerbare Freiheit
Tor Node      : ✓ ACTIVE EXIT NODE DETECTED
Abuse reports : 143 (SSH brute force, port scanning, DDoS)
Cloud         : Not a known cloud provider
Open ports    : 80, 443
```

**What this tells you:** This IP is a Tor exit node — meaning hundreds of different users route traffic through it anonymously. The 143 abuse reports are not necessarily from one attacker; they reflect the accumulated activity of everyone who has used this exit node maliciously. Blocking this single IP provides limited protection because the attacker can trivially switch to another exit node.

**SENTINEL's recommendations in this case:**
- Block the full Tor exit node range, not just this IP
- Implement MFA on exposed services — brute force via Tor is IP-rotation resistant
- Add to SIEM for historical correlation
- Report to AbuseIPDB to contribute to the community database

This is the difference between a raw IP lookup and **actionable threat intelligence**.

---

## SENTINEL + DOMINUS: the full picture

SENTINEL and DOMINUS are designed to work together as a complete reconnaissance framework:

```
1. Run DOMINUS on a domain → discovers infrastructure and extracts IPs from DNS
2. Take those IPs → run SENTINEL on each one
3. Cross-reference findings → complete threat picture
```

**Example with example.es:**

```bash
# Step 1: DOMINUS maps the domain
python dominus.py example.es --only dns
# DNS records reveal two IPs: XX.XXX.XXX.XXX and XX.XX.XXX.XXX

# Step 2: SENTINEL profiles each IP
python sentinel.py XX.XXX.XXX.XXX
# → OVH/Wetopi · Spain · Threat Score 2/100 · Clean

python sentinel.py XX.XX.XXX.XXX
# → OVH/Wetopi · Netherlands · Threat Score 2/100 · Clean
```

**Combined conclusion:** example.es has email authentication issues at the DNS level (DMARC p=none, SPF soft-fail) but its underlying infrastructure is clean, European-hosted, with no abuse history. The risk is in the configuration, not the servers.

This kind of layered analysis — domain configuration + IP reputation — is standard practice in professional security assessments. DOMINUS and SENTINEL automate it completely.

> 🔗 See [DOMINUS](https://github.com/KristinaSabitova/dominus) for domain-level reconnaissance.

---

## The report

A single `.html` file. Open it anywhere. Send it to anyone.

- IP address displayed prominently with country flag and ASN
- Animated SVG threat score ring with cyan accent
- **Interactive Leaflet.js map** with pulsing marker at the exact IP location
- Tor/VPN detection banner with pulse animation when detected
- Abuse category timeline with proportional horizontal bars
- Cloud provider context cards
- Port table with color-coded severity
- Numbered actionable recommendations with priority badges
- Collapsible raw data per phase
- **JSON export button** — downloads raw structured data directly from the HTML
- **Language switcher: 🇪🇸 Spanish / 🇷🇺 Russian** — instant, no page reload
- Fully standalone — all CSS and JS inline (except Google Fonts and Leaflet CDN)

---

## Installation

```bash
git clone https://github.com/KristinaSabitova/sentinel.git
cd sentinel
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
brew install nmap        # macOS
sudo apt install nmap    # Linux
```

**API keys (optional but recommended):**

```bash
cp .env.example .env
# Edit .env and add:
# ABUSEIPDB_KEY=your_key    → free tier: 1000 checks/day at abuseipdb.com
# OTX_KEY=your_key          → free, unlimited at otx.alienvault.com
```

Both APIs have free tiers. SENTINEL works without them — those phases are skipped gracefully and marked in the report.

---

## Usage

```bash
# Full scan
.venv/bin/python sentinel.py XXX.XXX.XXX.X

# Skip port scan (faster)
.venv/bin/python sentinel.py XXX.XXX.XXX.X --skip ports

# Specific phases only
.venv/bin/python sentinel.py XXX.XXX.XXX.X --only geo abuse tor

# Full scan + JSON export
.venv/bin/python sentinel.py XXX.XXX.XXX.X --json
```

---

## Tech stack

| Library | Purpose |
|---------|---------|
| `requests` | ip-api.com, AbuseIPDB, OTX, Tor list, cloud range files |
| `python-nmap` | Port scanning |
| `jinja2` | HTML report templating |
| `rich` | Terminal output formatting |
| Leaflet.js (CDN) | Interactive geolocation map in report |

---

## Project structure

```
sentinel/
├── sentinel.py
├── requirements.txt
├── .env.example
├── sentinel/
│   ├── core/
│   │   ├── engine.py        # Orchestrates phases, handles errors per phase
│   │   └── scoring.py       # Threat Score logic with weighted contributions
│   ├── modules/
│   │   ├── geo_module.py
│   │   ├── abuse_module.py
│   │   ├── threat_module.py
│   │   ├── ports_module.py
│   │   ├── cloud_module.py
│   │   └── tor_module.py
│   ├── report/
│   │   ├── generator.py
│   │   └── templates/report.html
│   └── utils/logger.py
└── output/
```

---


<img width="1510" height="2585" alt="sentinel" src="https://github.com/user-attachments/assets/60f53c5d-5feb-4455-b8d2-7f12a00022d3" />

## Legal notice

SENTINEL performs **passive reconnaissance only**. It queries publicly available data — IP geolocation APIs, public abuse databases, open threat intelligence feeds, and publicly documented cloud IP ranges. It does not exploit vulnerabilities, access restricted systems, or modify any data.

Always obtain proper authorization before scanning infrastructure you do not own.

---

## Author

Built for an academic cybersecurity practice at **Evolve Academy**.
Designed to demonstrate IP-level threat intelligence as a professional OSINT capability.

Part of the **DOMINI Suite** alongside [DOMINUS](https://github.com/KristinaSabitova/dominus).

---

*SENTINEL — know who's knocking before you open the door.*
