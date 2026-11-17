# TP2 Chatbots and Recommender Systems

This project contains Discord bots built with Python, Discord, Rasa NLU and
the TMDB and weather APIs.

## Requirements

- Python 3.10
- [uv](https://docs.astral.sh/uv/)
- A Discord bot application and token
- A [TMDB API key](https://www.themoviedb.org/settings/api) for the movie bot
- An optional [OpenWeatherMap API key](https://openweathermap.org/api) for
  the weather bot

## Installation

Clone the repository and enter the project directory:

```bash
git clone <repository-url>
cd TP2
```

Create the virtual environment and install the locked dependencies:

```bash
uv sync
```

Create the local environment file:

```bash
cp .env.example .env
```

Edit `.env` and set `TOKEN` and `TMDB_API_KEY`. Set
`OPENWEATHER_API_KEY` if you want to use OpenWeatherMap instead of the
Open-Meteo fallback. Never commit `.env`.

For the Discord bots, enable the **Message Content Intent** in the Discord
Developer Portal.

## Movie bot

Generate the Rasa NLU training data:

```bash
uv run python generate_nlu.py
```

Train the Rasa model:

```bash
uv run rasa train
```

Start the movie bot:

```bash
uv run python discord_movie_bot.py
```

The bot loads the most recently modified model from `models/`.

## Weather bot

Start the weather bot:

```bash
uv run python TP2_weatherBot.py
```

The first run downloads the required NLTK WordNet data.

## Other scripts

Run the basic TMDB example:

```bash
uv run python TP2_MovieBot.py
```

Run the simple Discord echo bot:

```bash
uv run python TP2_Chatbot.py
```

## Project files

- `generate_nlu.py`: generates `data/nlu.yml`.
- `config.yml`: Rasa NLU pipeline configuration.
- `discord_movie_bot.py`: movie and actor Discord bot.
- `TP2_weatherBot.py`: weather Discord bot.
- `TP2_MovieBot.py`: basic TMDB API example.
- `TP2_Chatbot.py`: basic Discord echo bot.