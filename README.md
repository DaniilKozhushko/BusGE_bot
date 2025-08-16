# BusGE_bot
Bot for tracking buses at public transport stops in Georgia (Tbilisi and Batumi).  
To get started, the user needs to select a city and then enter the stop number. If available, the time until the next buses arrive will be displayed.
<div align="right">
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" height="40" alt="python logo"  />
  <img width="2" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/sqlite/sqlite-original.svg" height="40" alt="sqlite logo"  />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/docker/docker-original.svg" height="50" alt="docker logo"  />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/linux/linux-original.svg" height="40" alt="linux logo"  />
  <img width="2" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/git/git-original.svg" height="40" alt="git logo"  />
</div>


## ⭐️ Features
The user selects their city (Tbilisi or Batumi), enters the stop number, and then receives the schedule of the nearest buses arriving at that stop.
Users can also save frequently used stops with custom names for quick access.

## ⚙️ Technologies
- `Python` 3.11+
- `Aiogram` 3+
- `aiosqlite`
- `httpx`
- `dotenv`

## 🗂 Project Structure

```
.
├── handlers/ # Bot handlers
│   └── user_router.py # Router with logic and commands for users
├── images/
├── keyboards/ # Keyboards for bot
│   └── inline.py # Inline-keyboards
├── utils/ # Different functions
│   ├── async_utils.py # Asynchronous server request functions
│   └── utils.py # Schedule parsing functions
├── .env # Environment variables
├── .gitignore # Files and folders excluded from Git
├── batumi_data.json # Main file with routes in Batumi
├── config.py # Loading settings from .env via dotenv
├── database.py # Working with the database
├── main.py # Entry point: bot launch
└── README.md # Project description
```

## 🚀 Installation & Run

1. Clone the repository:

   ```bash
   git clone https://github.com/DaniilKozhushko/BusGE_bot.git
   ```
   
   ```bash
   cd BusGE_bot
   ```

2. Create a .env file:

   ```bash
   nano .env
   ```

   ```env
   TELEGRAM_BOT_TOKEN=telegram_bot_token
   TTC_BUS_API=ttc_api_key
   BASE_TBILISI_URL=tbilisi_base_url
   BASE_BATUMI_URL=batumi_base_url
   ```
   
3. Create and activate a virtual environment:

   ```bash
   python3 -m venv venv
   ```
   
   ```bash
   source venv/bin/activate
   ```
   
4. Install requirements:

   ```bash
   pip install -r requirements.txt
   ```

5. Send a .json file from local computer with route data:

	```bash
 	scp -P <port> <file_name>.json <user>@<ipv4>:/path/to/bot
 	```
   
6. Run:

	```bash
	python main.py
	```

## 📝License

This project is licensed under the [MIT License](LICENSE)

<p align="center">
  <a href="https://t.me/BusGE_bot" target="_blank" rel="noopener noreferrer">
    <img src="./images/logo.png" width="200" alt="Logo" />
  </a>
</p>
