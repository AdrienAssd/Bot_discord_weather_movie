import os
import re
import random
import datetime
import requests
import discord
import nltk
from nltk.corpus import wordnet
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")
API_KEY = os.getenv("OPENWEATHER_API_KEY")

nltk.download("wordnet", quiet=True)
nltk.download("omw-1.4", quiet=True)

keywords_dict = {
    "greetings": ["hello", "howdy", "hi", "hullo", "how do you do", "hey"],
    "ending": ["bye", "goodbye", "see you", "exit", "quit"],
    "name": ["your name", "who are you", "call you"],
    "gender": ["gender", "male", "female", "boy", "girl", "man", "woman"],
    "time": ["time", "clock", "hour", "what day"],
    "thanks": ["thanks", "thank you", "appreciate"],
    "weather": ["weather", "rain", "temperature", "sunrise", "cold", "hot", "sunny", "cloudy", "forecast"]
}

responses_dict = {
    "greetings": [
        "Hello {user}! How can I help you today? 👋",
        "Hi {user}, you look well today! ✨",
        "Welcome {user}! Ask me about the weather anywhere in the world 🌍",
        "Hiii {user}... I am SkyBot, how are you? 🤖"
    ],
    "ending": [
        "Goodbye {user}! Have a wonderful day! 👋",
        "See you later {user}! Stay safe! ☀️"
    ],
    "name": [
        "I am **SkyBot**, your Discord weather assistant! 🤖",
        "You can call me **WeatherBot**, {user}!"
    ],
    "gender": [
        "I am a Discord bot written in Python, so I don't have a gender! 💻"
    ],
    "thanks": [
        "You're very welcome, {user}! 😊",
        "Happy to help, {user}! 🙌"
    ],
    "unknown": [
        "Sorry {user}, I didn't understand that. Try asking: *What is the weather in Paris tomorrow?* 🤔",
        "Not sure what you mean, {user}! Ask me about the weather in any city 🌤️"
    ]
}

def expand_keywords_wordnet(kw_dict):
    expanded_dict = {}
    for intent, words in kw_dict.items():
        word_set = set(words)
        if intent not in ["greetings", "ending", "name"]:
            for word in words:
                if " " in word:
                    continue
                for syn in wordnet.synsets(word):
                    for lemma in syn.lemmas():
                        synonym = lemma.name().replace("_", " ").lower()
                        synonym = re.sub(r"[^a-z0-9\s-]", "", synonym).strip()
                        if len(synonym) > 2:
                            word_set.add(synonym)
        expanded_dict[intent] = list(word_set)
    return expanded_dict

keywords_dict = expand_keywords_wordnet(keywords_dict)

def handle_typos(word):
    if word == "hello":
        return r"h[ae]l+o+"
    return re.escape(word) + r"+"

regex_dict = {}
for intent, words in keywords_dict.items():
    sorted_words = sorted(words, key=len, reverse=True)
    patterns = [rf".*\b{handle_typos(w)}\b.*" for w in sorted_words]
    regex_dict[intent] = "|".join(patterns)

def matchPattern(user_msg):
    if re.search(regex_dict["weather"], user_msg, re.IGNORECASE):
        return "weather"
    for intent, pattern in regex_dict.items():
        if re.search(pattern, user_msg, re.IGNORECASE):
            return intent
    return "unknown"

def getResponse(intent, user_mention):
    if intent == "time":
        now = datetime.datetime.now().strftime("%H:%M")
        return f"🕒 {user_mention}, the current time is **{now}**."
    template = random.choice(responses_dict.get(intent, responses_dict["unknown"]))
    return template.format(user=user_mention)

weather_entity_pattern = re.compile(
    r"(?:weather|rainy|sunny|cloudy|cold|hot|temperature|forecast).*?\b(?:in|for|at)\s+"
    r"(?P<city>[A-Za-z]+(?:[\s-][A-Za-z]+)*?)"
    r"(?:\s+(?P<time>the day after tomorrow|tomorrow|today|now))?\s*\??$",
    re.IGNORECASE
)

def createEntities(user_msg):
    intent = matchPattern(user_msg)
    entities = {"city": None, "time": None}
    if intent == "weather":
        match = weather_entity_pattern.search(user_msg)
        if match:
            if match.group("city"):
                entities["city"] = match.group("city").strip().title()
            if match.group("time"):
                entities["time"] = match.group("time").strip().lower()
    return {"intent": intent, "entities": entities}

def fetch_weather_data(location, date="today"):
    day_offset = {"today": 0, "now": 0, "tomorrow": 1, "the day after tomorrow": 2}.get(date, 0)

    if API_KEY:
        url = f"https://api.openweathermap.org/data/2.5/forecast?q={location}&appid={API_KEY}&units=metric"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            country = data["city"]["country"]
            idx = min(day_offset * 8, len(data["list"]) - 1)
            temp = data["list"][idx]["main"]["temp"]
            condition = data["list"][idx]["weather"][0]["description"]
            icon_code = data["list"][idx]["weather"][0]["icon"]
            icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"
            return {"status": 200, "city": location, "country": country, "temp": temp, "condition": condition, "icon": icon_url}
        elif response.status_code == 404:
            return {"status": 404, "error": f"❌ Sorry, I couldn't find the city **{location}**."}
        else:
            return {"status": response.status_code, "error": f"⚠️ Weather API error ({response.status_code})."}

    geo = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1&format=json").json()
    if "results" not in geo:
        return {"status": 404, "error": f"❌ Sorry, I couldn't find the city **{location}**."}
    
    place = geo["results"][0]
    w = requests.get(
        f"https://api.open-meteo.com/v1/forecast?latitude={place['latitude']}&longitude={place['longitude']}"
        f"&daily=temperature_2m_max,weathercode&timezone=auto"
    ).json()
    temp = w["daily"]["temperature_2m_max"][day_offset]
    code = w["daily"]["weathercode"][day_offset]
    cond = "Clear sky" if code == 0 else ("Cloudy" if code in [1, 2, 3] else "Rainy")
    return {"status": 200, "city": place["name"], "country": place.get("country", ""), "temp": temp, "condition": cond, "icon": None}

def build_weather_embed(location, date="today", user_msg="", user_mention=""):
    result = fetch_weather_data(location, date)
    if result["status"] != 200:
        return result["error"], None

    temp = round(result["temp"])
    cond = result["condition"]
    city = result["city"]
    country = result["country"]

    if temp <= 8:
        word_temp = "very cold"
        embed_color = discord.Color.blue()
        emoji = "❄️🥶"
        gif_url = "https://media.giphy.com/media/s4Bi420mMDRBK/giphy.gif"
    elif temp <= 22:
        word_temp = "pleasant"
        embed_color = discord.Color.green()
        emoji = "🌤️😊"
        gif_url = "https://media.giphy.com/media/3o7rbY6OwRBrkbx8qI/giphy.gif"
    else:
        word_temp = "super hot"
        embed_color = discord.Color.red()
        emoji = "🔥🥵"
        gif_url = "https://media.giphy.com/media/ToMjGppLes0ENI5osCc/giphy.gif"

    if "rain" in cond.lower():
        emoji = "🌧️☔"
        gif_url = "https://media.giphy.com/media/t7Qb8655Z1VfBGr5XB/giphy.gif"
    elif "cloud" in cond.lower():
        emoji = "☁️"

    prefix = ""
    q = user_msg.lower()
    if "cold" in q:
        prefix = "**Yes, it is!** " if temp <= 10 else "**No, it's not cold.** "
    elif "rainy" in q or "rain" in q:
        prefix = "**Yes, expect rain!** " if "rain" in cond.lower() else f"**No, it will be {cond.lower()}.** "
    elif "sunny" in q:
        prefix = "**Yes, it will be sunny!** " if "clear" in cond.lower() else f"**No, it will be {cond.lower()}.** "

    description = (
        f"Hey {user_mention}! {prefix}It is **{word_temp}** in **{city}, {country}** "
        f"({date}), with **{temp}°C** ({cond}) {emoji}"
    )

    embed = discord.Embed(
        title=f"{emoji} Weather Forecast — {city}, {country}",
        description=description,
        color=embed_color
    )
    embed.add_field(name="🌡️ Temperature", value=f"**{temp}°C**", inline=True)
    embed.add_field(name="📅 Timeframe", value=date.capitalize(), inline=True)
    embed.add_field(name="☁️ Condition", value=cond.capitalize(), inline=True)
    embed.set_image(url=gif_url)
    if result["icon"]:
        embed.set_thumbnail(url=result["icon"])
    embed.set_footer(text="Powered by SkyBot • Session 2 NLP")

    return None, embed

class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pending_users = {}

    async def on_ready(self):
        print(f"✅ Logged in as {self.user.name} (ID: {self.user.id})")

    async def on_message(self, message):
        if message.author == self.user:
            return

        user_id = message.author.id
        user_mention = message.author.mention
        user_msg = message.content.strip()

        print(f"[{message.author}] Message: {user_msg}")

        if user_id in self.pending_users:
            city = user_msg.title()
            time_val = self.pending_users.pop(user_id) or "today"
            await message.add_reaction("🌍")
            err, embed = build_weather_embed(city, time_val, user_msg, user_mention)
            if err:
                await message.channel.send(err)
            else:
                await message.channel.send(embed=embed)
            return

        parsed = createEntities(user_msg)
        intent = parsed["intent"]

        if intent == "greetings":
            await message.add_reaction("👋")
            await message.channel.send(getResponse("greetings", user_mention))

        elif intent == "ending":
            await message.add_reaction("👋")
            await message.channel.send(getResponse("ending", user_mention))

        elif intent == "weather":
            city = parsed["entities"]["city"]
            time_val = parsed["entities"]["time"] or "today"

            if not city:
                self.pending_users[user_id] = time_val
                await message.add_reaction("❓")
                await message.channel.send(f"{user_mention}, which city do you want the weather for? 🏙️")
            else:
                await message.add_reaction("🌤️")
                err, embed = build_weather_embed(city, time_val, user_msg, user_mention)
                if err:
                    await message.channel.send(err)
                else:
                    await message.channel.send(embed=embed)

        else:
            await message.channel.send(getResponse(intent, user_mention))

intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(TOKEN)