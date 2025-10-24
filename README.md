# LeetCode Reminder Bot

[![Build Status](https://github.com/rajat069/leetcode-reminder-bot/actions/workflows/build-image.yml/badge.svg)](https://github.com/rajat069/leetcode-reminder-bot/actions/workflows/build-image.yml)
[![Docker Image](https://img.shields.io/badge/ghcr.io-rajat069%2Fleetcode--reminder--bot-blue?logo=docker)](https://github.com/orgs/Rajat069/packages?repo_name=leetcode-reminder-bot)
[![Python Version](https://img.shields.io/badge/python-3.10-blue?logo=python)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

### About

**LeetCode AI Coach Bot** is a smart, containerized reminder and coaching bot that **keeps you consistent** with your daily LeetCode practice — and gives you **AI-powered hints** when you need them most!

It checks whether users have solved the **Problem of the Day**, then:
- Sends a **Reminder Email** (with AI hints + motivational quotes) if unsolved.
- Sends a **Congratulations Email** when solved.

> Built for developers who want to stay sharp, motivated, and consistent — all automatically.

---

## Key Features

### 💡 Smart Email Logic
- Sends **“Congratulations”** or **“Reminder”** emails automatically.
- Dynamic templates keep every message engaging.

###  AI-Powered Coaching (Gemini)
- **Adaptive Hints:** Number of hints varies by difficulty and acceptance rate.  
- **Helpful Hints:** Uses official problem data to generate intuitive AI hints.  
- **Motivational Quotes:** Fetches inspiring movie quotes to boost motivation.

### 🐳 Fully Containerized
- Runs as a **single lightweight Docker container**.  
- Supports both **amd64** and **arm64** architectures (Intel/AMD + Apple/Raspberry Pi).

### ⚙️ CI/CD Pipeline
- Automatically builds and pushes Docker images to GHCR.  
- Triggers on every `git push` to `main`.

### 🧱 Clean & Modular Code
- Organized by logical services: `api/`, `email/`, `config/`, and `core/`.  
- Built for scalability and easy maintenance.

---

## 🖼️ Gallery

| Reminder Email (Unsolved) | Congratulations Email (Solved) |
|----------------------------|--------------------------------|
| *(Screenshot coming soon)* | *(Screenshot coming soon)* |

---

## 🏗️ Architecture Overview

**“Set it and forget it” — built for autonomous operation.**

```text
┌─────────────┐        ┌──────────────┐        ┌────────────┐
│  Git Push   │ ─────▶ │ GitHub Action│ ─────▶ │ GHCR Image │
└─────────────┘        └──────────────┘        └────────────┘
                                                     │
                                                     ▼
                                              ┌──────────────┐
                                              │   Your VM     │
                                              │ (Docker Run)  │
                                              └──────────────┘
                                                     │
                                                     ▼
                                        Python bot runs every few hours
                                          - Checks user activity
                                          - Sends email via SMTP
                                          - Uses Gemini AI for hints
```
## ⚡ Deployment (Production)

This bot is designed to run **24/7** on a server or VM using Docker.

---

### Prerequisites

- A VM/server with **Docker installed**
- A **GitHub Personal Access Token (PAT)** with `read:packages` scope
- **GMAIL_APP_PASSWORD**
- **GEMINI_API_KEY**

---
### Step 1: Log in to GHCR

```bash
sudo docker login ghcr.io -u YOUR_USERNAME -p YOUR_PAT
``` 
### Step 2: Create Configuration Files
```bash
/home/{vm-username}/leetcode.env
```
> Note: Replace {vm-username} with your actual VM's username.

Your environment variables — no quotes needed.
```
GMAIL_APP_PASSWORD=YOUR_GMAIL_APP_PASSWORD_HERE
SMTP_USER={your-mail}@gmail.com
GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
/home/{vm-username}/users.json
```
>Note: Replace {your-mail} with your actual e-mail.

Your user list in JSON format.
```json
[
  {
    "username": "pam",
    "email": "pam06@gmail.com"
  },
  {
    "username": "simrunn",
    "email": "simranxxxxx@gmail.com"
  }
]
```
🧠 Step 3: Run the Bot
Pull and start the service with one command:
```bash
sudo docker run \
    --detach \
    --restart=always \
    --name leetcode-bot \
    --dns=8.8.8.8 \
    --env-file /home/{vm-username}/leetcode.env \
    -v /home/{vm-username}/users.json:/app/users.json \
    ghcr.io/{github-username}/leetcode-reminder-bot:latest
```
> Note: Replace {vm-username} and github-username} with your actual details.

🪵 Check logs anytime:
```bash
sudo docker logs -f leetcode-bot
```
## Local Development

1️⃣ Clone the Repository
```bash
git clone https://github.com/rajat069/leetcode-reminder-bot.git
cd leetcode-reminder-bot
```
2️⃣ Create a .env File
```bash
GMAIL_APP_PASSWORD=YOUR_GMAIL_APP_PASSWORD_HERE
SMTP_USER={your-mail}@gmail.com
GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
```
3️⃣ Create a users.json File
```json
[
  { "username": "pam", "email": "pam01@gmail.com" }
]
```
4️⃣ Install Dependencies
``` bash
pip install -r requirements.txt
```
5️⃣ Run Locally
``` bash
python main.py
```
## Configuration Reference

| Variable | Description | Required | Default |
| :--- | :--- | :--- | :--- |
| `GMAIL_APP_PASSWORD` | Google App Password for email sending | ✅ Yes | — |
| `SMTP_USER` | Gmail address used for SMTP | ✅ Yes | — |
| `GEMINI_API_KEY` | API key from Google AI Studio | ✅ Yes | — |
| `SMTP_SERVER` | SMTP server hostname | ❌ No | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP port number | ❌ No | `587` |

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.
