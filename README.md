<!-- Improved compatibility of back to top link -->
<a id="readme-top"></a>

<!-- PROJECT SHIELDS -->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![project_license][license-shield]][license-url]

<!-- HEADER -->
<br />
<div align="center">
  <a href="https://github.com/github_username/repo_name">
    <img src="marslogo.png" alt="Logo" width="250" height="250">
  </a>

  <h3 align="center">Multi Agent Recommender System (MARS)</h3>

  <p align="center">
    A Telegram Bot and API that helps users with namaz-related questions using a multi-agent recommender architecture.
    <br />
    <a href="https://github.com/github_username/repo_name"><strong>Explore the docs »</strong></a>
    <br />
    <a href="https://demo-video-link.com">📺 Watch Demo Video</a>
    <br />
    <a href="https://github.com/github_username/repo_name">🌐 View Live Product</a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#project-goal-and-description">Project Goal and Description</a></li>
    <li><a href="#project-context-diagram">Project Context Diagram</a></li>
    <li><a href="#built-with">Built With</a></li>
    <li><a href="#getting-started">Getting Started</a></li>
    <li><a href="#usage">Usage Guide</a></li>
    <li><a href="#roadmap">Feature Roadmap</a></li>
    <li><a href="#development">Development</a></li>
    <li><a href="#quality-assurance">Quality Assurance</a></li>
    <li><a href="#build-and-deployment">Build & Deployment</a></li>
    <li><a href="#architecture">Architecture</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>


<!-- ABOUT THE PROJECT -->
## 🧭 Project Goal and Description

The goal of this project is to build a multi-agent recommendation system that assists users with Islamic prayer guidance through an interactive Telegram bot. The system is backed by a FastAPI server and uses MongoDB to store users and conversations.


### Key Objectives:
- Provide helpful recommendations and answers about namaz in a conversational way.
- Maintain and analyze user interactions to improve personalized responses.

### System Structure:
- A **Telegram bot** (using `python-telegram-bot`) that communicates with users.
- A **FastAPI backend** that handles data storage, business logic, and API routing.
- A **MongoDB database** accessed via the async `motor` driver.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


## 🧩 Project Context Diagram

![cnotext diagram](https://github.com/Black-persik/bot_aio/blob/main/images/context.jpg)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 🛠️ Built With

[![Python][Python-shield]][Python-url]
[![FastAPI][FastAPI-shield]][FastAPI-url]
[![MongoDB][Mongo-shield]][Mongo-url]
[![Motor][Motor-shield]][Motor-url]
[![Telegram Bot API][Telegram-shield]][Telegram-url]
[![Pydantic][Pydantic-shield]][Pydantic-url]
[![Dotenv][Dotenv-shield]][Dotenv-url]
[![Uvicorn][Uvicorn-shield]][Uvicorn-url]
[![HTTPX][Httpx-shield]][Httpx-url]
[![Requests][Requests-shield]][Requests-url]
[![Docker][Docker-shield]][Docker-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>



## 🛣️ Feature Roadmap

- [x] Recomender System for namaz help
- [x] Telegram Bot frontend
- [x] FastAPI endpoints
- [x] MongoDB integration  
- [ ] Voice interface

<p align="right">(<a href="#readme-top">back to top</a>)</p>


## 📘 Usage Guide

### 🤖 Telegram Bot

You can either use [our](https://t.me/) bot or deploy our project and create your own see [Getting Started].

1. Start the Telegram bot and create:
   ```bash
   python bot_main.py
   ```

2. Open Telegram and search for your bot (e.g., `@your_bot_username`) or use the direct link:
   ```
   https://t.me/your_bot_username
   ```

3. Use the bot:
   - Send `/start` to begin
   - Ask questions via `/ask`
   - Interact with any other available features


### 🌐 FastAPI Backend

To use the recommender system you can contact us to get API endpoints or you can deploy our system by yourself see [Getting Started](#getting-started) section:

1. Start the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```

2. Visit the auto-generated swagger documentation.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



## 🚀 Getting Started

### 📦 Local Development

1. Clone the repo:
   ```bash
   git clone https://github.com/Black-persik/bot_aio.git
   cd bot_aio
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the requirements:
   ```bash
   pip install -r requirements.txt
   ```

4. Create an `.env` file (copy from `.env.example`) and configure:
   ```env
   BOT_TOKEN=your_telegram_bot_token
   MONGODB_URI=your_mongodb_connection_uri
   ```

5. Run services:
   ```bash
   uvicorn main:app --reload      # FastAPI backend
   python bot_main.py             # Telegram bot
   ```

### 🐳 Docker Deployment

1. Run with Docker Compose:
   ```bash
   docker-compose up --build
   ```
<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- CONTRIBUTING -->
## 🚀 Contributing

Contributions make the open source community an incredible place to learn and grow. Any help is **greatly appreciated**!

Have an idea to improve `bot_aio`? Fork the repo, make your changes, and open a pull request. Or just open an issue with the tag `enhancement`.

1. Fork the project  
2. Create your branch (`git checkout -b feature/MyFeature`)  
3. Commit your changes (`git commit -m 'Add MyFeature'`)  
4. Push (`git push origin feature/MyFeature`)  
5. Open a pull request

<p align="right">(<a href="#readme-top">back to top</a>)</p>



## 🌟 Top Contributors

<a href="https://github.com/Black-persik/bot_aio/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Black-persik/bot_aio" alt="Top contributors" />
</a>



## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



## 📬 Contact

Black-persik – [@black_persik](https://t.me/black_persik)  
Project: [github.com/Black-persik/bot_aio](https://github.com/Black-persik/bot_aio)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



## 🙏 Acknowledgments

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) – Telegram Bot Framework  
- [FastAPI](https://github.com/tiangolo/fastapi) – Web framework  
- [Motor](https://github.com/mongodb/motor) – Async MongoDB driver  
- [python-dotenv](https://github.com/theskumar/python-dotenv) – Manage environment variables  
- [contrib.rocks](https://contrib.rocks) – Contributor avatars


<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
[contributors-shield]: https://img.shields.io/github/contributors/Black-persik/bot_aio.svg?style=for-the-badge
[contributors-url]: https://github.com/Black-persik/bot_aio/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/Black-persik/bot_aio.svg?style=for-the-badge
[forks-url]: https://github.com/Black-persik/bot_aio/network/members
[stars-shield]: https://img.shields.io/github/stars/Black-persik/bot_aio.svg?style=for-the-badge
[stars-url]: https://github.com/Black-persik/bot_aio/stargazers
[issues-shield]: https://img.shields.io/github/issues/Black-persik/bot_aio.svg?style=for-the-badge
[issues-url]: https://github.com/Black-persik/bot_aio/issues
[license-shield]: https://img.shields.io/github/license/Black-persik/bot_aio.svg?style=for-the-badge
[license-url]: https://github.com/Black-persik/bot_aio/blob/main/LICENSE.txt

[Python-shield]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white
[Python-url]: https://www.python.org/

[FastAPI-shield]: https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi
[FastAPI-url]: https://fastapi.tiangolo.com/

[Mongo-shield]: https://img.shields.io/badge/MongoDB-4EA94B?style=for-the-badge&logo=mongodb&logoColor=white
[Mongo-url]: https://www.mongodb.com/

[Motor-shield]: https://img.shields.io/badge/Motor-00ACD7?style=for-the-badge
[Motor-url]: https://motor.readthedocs.io/

[Telegram-shield]: https://img.shields.io/badge/python--telegram--bot-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white
[Telegram-url]: https://docs.python-telegram-bot.org/

[Pydantic-shield]: https://img.shields.io/badge/Pydantic-00B2FF?style=for-the-badge&logo=pydantic&logoColor=white
[Pydantic-url]: https://docs.pydantic.dev/

[Dotenv-shield]: https://img.shields.io/badge/dotenv-0A0A0A?style=for-the-badge
[Dotenv-url]: https://pypi.org/project/python-dotenv/

[Uvicorn-shield]: https://img.shields.io/badge/Uvicorn-008489?style=for-the-badge&logo=uvicorn&logoColor=white
[Uvicorn-url]: https://www.uvicorn.org/

[Httpx-shield]: https://img.shields.io/badge/HTTPX-003569?style=for-the-badge
[Httpx-url]: https://www.python-httpx.org/

[Requests-shield]: https://img.shields.io/badge/Requests-2C8EBB?style=for-the-badge
[Requests-url]: https://requests.readthedocs.io/

[Docker-shield]: https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white
[Docker-url]: https://www.docker.com/



