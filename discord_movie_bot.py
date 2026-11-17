import os
import re
import glob
import discord
import requests
from dotenv import load_dotenv
from rasa.core.agent import Agent

load_dotenv()
DISCORD_TOKEN = os.getenv("TOKEN")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

INTENT_THRESHOLD = 0.60
ENTITY_THRESHOLD = 0.60
MOVIE_INTENTS = {"movieinfo", "director", "releaseYear", "actors", "rating", "recommend", "poster"}

latest_model = max(glob.glob("models/*.tar.gz"), key=os.path.getmtime)
print(f"⏳ Loading Rasa model: {latest_model}...")
rasa_agent = Agent.load(latest_model)
print("✅ Rasa model loaded!")

def detect_traits(text):
    """Analyse le ton global de la phrase (politesse / impatience)."""
    q = text.lower()
    if re.search(r"\b(please|kindly|could you|would you|thank you|thanks)\b", q):
        return "polite"
    if re.search(r"\b(now|hurry|fast|quick|stupid|useless)\b", q) or text.endswith("!!"):
        return "impatient"
    return "neutral"

def apply_trait_tone(trait, user_mention, base_message):
    """Adapte le ton de la réponse selon le trait détecté."""
    if trait == "polite":
        return f"With pleasure, {user_mention}! 😊 {base_message}"
    elif trait == "impatient":
        return f"Right away, {user_mention}! ⚡ {base_message}"
    return f"{user_mention}, {base_message[0].lower() + base_message[1:]}"

def get_movie_data(movie_title):
    if not movie_title:
        return None
    base_url = "https://api.themoviedb.org/3"
    search_resp = requests.get(
        f"{base_url}/search/movie",
        params={"api_key": TMDB_API_KEY, "query": movie_title, "language": "en-US"},
        timeout=5
    )
    if search_resp.status_code != 200:
        return None

    results = search_resp.json().get("results", [])
    if not results:
        return None

    movie = results[0]
    movie_id = movie["id"]

    details = requests.get(
        f"{base_url}/movie/{movie_id}",
        params={"api_key": TMDB_API_KEY, "append_to_response": "credits,recommendations"},
        timeout=5
    ).json()

    crew = details.get("credits", {}).get("crew", [])
    cast = details.get("credits", {}).get("cast", [])
    recs = details.get("recommendations", {}).get("results", [])

    directors = [p["name"] for p in crew if p.get("job") == "Director"]
    actors = [f"• **{p['name']}** ({p.get('character', 'Role unknown')})" for p in cast[:5]]
    similar_movies = [f"• **{r['title']}** ({r.get('release_date', '')[:4]})" for r in recs[:5]]
    poster_path = movie.get("poster_path")
    poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None

    return {
        "title": movie.get("title", movie_title),
        "release_date": movie.get("release_date", "Unknown"),
        "overview": movie.get("overview", "No overview available."),
        "rating": round(movie.get("vote_average", 0), 1),
        "directors": ", ".join(directors) if directors else "Unknown",
        "actors_list": "\n".join(actors) if actors else "• Unknown",
        "similar_list": "\n".join(similar_movies) if similar_movies else "• No recommendations found",
        "poster": poster_url
    }

def get_actor_movies(actor_name):
    if not actor_name:
        return None
    base_url = "https://api.themoviedb.org/3"
    resp = requests.get(
        f"{base_url}/search/person",
        params={"api_key": TMDB_API_KEY, "query": actor_name, "language": "en-US"},
        timeout=5
    )
    if resp.status_code != 200:
        return None

    results = resp.json().get("results", [])
    if not results:
        return None

    person = results[0]
    person_id = person["id"]
    profile_path = person.get("profile_path")
    photo_url = f"https://image.tmdb.org/t/p/w500{profile_path}" if profile_path else None

    credits_resp = requests.get(
        f"{base_url}/person/{person_id}/movie_credits",
        params={"api_key": TMDB_API_KEY, "language": "en-US"},
        timeout=5
    ).json()

    cast_movies = credits_resp.get("cast", [])
    cast_movies.sort(key=lambda m: m.get("popularity", 0), reverse=True)

    seen = set()
    movie_lines = []
    for m in cast_movies:
        title = m.get("title")
        if title and title not in seen:
            seen.add(title)
            year = m.get("release_date", "")[:4]
            year_str = f" ({year})" if year else ""
            movie_lines.append(f"• **{title}**{year_str}")
        if len(movie_lines) >= 10:
            break

    return {
        "name": person.get("name", actor_name),
        "movies_list": "\n".join(movie_lines) if movie_lines else "• No movies found",
        "photo": photo_url
    }

class MovieBotClient(discord.Client):
    def __init__(self, agent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agent = agent
        self.pending_intent = {}

    async def on_ready(self):
        print(f"🎬 Logged in as {self.user.name} (ID: {self.user.id})")

    async def parse_async(self, text):
        result = await self.agent.parse_message(text)
        intent = result["intent"]["name"]
        confidence = result["intent"]["confidence"]

        entities = {}
        for ent in result.get("entities", []):
            if ent.get("confidence_entity", 0.0) >= ENTITY_THRESHOLD:
                entities[ent["entity"]] = ent["value"]

        return intent, confidence, entities

    async def on_message(self, message):
        if message.author == self.user:
            return

        user_id = message.author.id
        user_mention = message.author.mention
        text = message.content.strip()
        trait = detect_traits(text)

        print(f"Message sent by {message.author} [Trait: {trait}]: {text}")

        if user_id in self.pending_intent:
            intent = self.pending_intent.pop(user_id)
            confidence = 1.0
            entities = {"actor": text} if intent == "actor_movies" else {"movie": text}
        else:
            intent, confidence, entities = await self.parse_async(text)
            print(f"Rasa NLU -> Intent: {intent} ({confidence:.2f}) | Entities: {entities}")

            if confidence < INTENT_THRESHOLD or intent == "out_of_scope":
                reply = f"{user_mention}, I'm not sure I understood that 🤔 Could you rephrase your question about a movie or an actor?"
                print(f"Bot response: {reply}")
                await message.channel.send(reply)
                return

        if intent == "greeting":
            await message.add_reaction("👋")
            await message.channel.send(f"Hello {user_mention}! 🎬 Ask me anything about movies, posters, or actors!")
            return
        elif intent == "bye":
            await message.add_reaction("🍿")
            await message.channel.send(f"Goodbye {user_mention}! Enjoy your next movie! 🎥")
            return
        elif intent == "help":
            await message.channel.send(
                f"{user_mention}, here is what you can ask me:\n"
                "• *Tell me about Inception*\n"
                "• *Who directed Iron Man?*\n"
                "• *When was Interstellar released?*\n"
                "• *Who starred in The Matrix?*\n"
                "• *Which movies did Tom Hanks play in?*\n"
                "• *Show me the poster of Avatar*\n"
                "• *What is the rating of The Dark Knight?*\n"
                "• *Recommend movies like Dune*"
            )
            return

        if intent == "actor_movies":
            actor_name = entities.get("actor")
            if not actor_name:
                self.pending_intent[user_id] = "actor_movies"
                await message.add_reaction("❓")
                await message.channel.send(f"{user_mention}, which actor are you asking about? 🎭")
                return

            await message.add_reaction("🎭")
            actor_data = get_actor_movies(actor_name)
            if not actor_data:
                await message.channel.send(f"❌ Sorry {user_mention}, I couldn't find **{actor_name}** on TMDB.")
                return

            header = apply_trait_tone(trait, user_mention, f"Here are the top movies featuring **{actor_data['name']}**:")
            desc = f"{header}\n\n{actor_data['movies_list']}"
            embed = discord.Embed(title=f"🎭 {actor_data['name']} — Filmography", description=desc, color=discord.Color.blue())
            if actor_data["photo"]:
                embed.set_thumbnail(url=actor_data["photo"])
            embed.set_footer(text=f"Intent: {intent} ({confidence:.0%}) • Trait: {trait} • Rasa & TMDB")
            await message.channel.send(embed=embed)
            return

        movie_title = entities.get("movie")
        if intent in MOVIE_INTENTS and not movie_title:
            self.pending_intent[user_id] = intent
            await message.add_reaction("❓")
            await message.channel.send(f"{user_mention}, which movie are you asking about? 🎞️")
            return

        await message.add_reaction("🎬")
        data = get_movie_data(movie_title)

        if not data:
            await message.channel.send(f"❌ Sorry {user_mention}, I couldn't find any movie matching **{movie_title}** on TMDB.")
            return

        embed = discord.Embed(title=f"🎬 {data['title']}", color=discord.Color.gold())

        if intent == "poster":
            if data["poster"]:
                embed.description = apply_trait_tone(trait, user_mention, f"Here is the official poster for **{data['title']}**!")
                embed.set_image(url=data["poster"])
            else:
                embed.description = f"Sorry {user_mention}, no poster is available for **{data['title']}**."
        else:
            if data["poster"]:
                embed.set_thumbnail(url=data["poster"])

            if intent == "movieinfo":
                embed.description = apply_trait_tone(trait, user_mention, data["overview"])
                embed.add_field(name="📅 Release Date", value=data["release_date"], inline=True)
                embed.add_field(name="⭐ Rating", value=f"{data['rating']}/10", inline=True)
            elif intent == "director":
                embed.description = apply_trait_tone(trait, user_mention, f"**{data['title']}** was directed by **{data['directors']}**.")
            elif intent == "releaseYear":
                embed.description = apply_trait_tone(trait, user_mention, f"**{data['title']}** was released on **{data['release_date']}**.")
            elif intent == "actors":
                header = apply_trait_tone(trait, user_mention, f"Here is the main cast of **{data['title']}**:")
                embed.description = f"{header}\n\n{data['actors_list']}"
            elif intent == "rating":
                embed.description = apply_trait_tone(trait, user_mention, f"**{data['title']}** has an average rating of ⭐ **{data['rating']}/10** on TMDB.")
            elif intent == "recommend":
                header = apply_trait_tone(trait, user_mention, f"If you liked **{data['title']}**, you should watch:")
                embed.description = f"{header}\n\n{data['similar_list']}"

        embed.set_footer(text=f"Intent: {intent} ({confidence:.0%}) • Trait: {trait} • Rasa & TMDB")
        print(f"Bot response [EMBED]: {embed.title} -> {embed.description}")
        await message.channel.send(embed=embed)

intents = discord.Intents.default()
intents.message_content = True

client = MovieBotClient(agent=rasa_agent, intents=intents)
client.run(DISCORD_TOKEN)