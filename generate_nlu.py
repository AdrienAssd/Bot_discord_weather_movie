import os

os.makedirs("data", exist_ok=True)

movies = [
    "iron man", "spider man", "inception", "the lord of the rings", "interstellar",
    "the untouchables", "avatar", "titanic", "the dark knight", "the matrix",
    "pulp fiction", "forrest gump", "gladiator", "the godfather", "star wars",
    "harry potter", "jurassic park", "the avengers", "black panther", "joker",
    "fight club", "goodfellas", "the lion king", "toy story", "finding nemo",
    "shrek", "frozen", "dune", "oppenheimer", "barbie", "parasite", "whiplash",
    "mad max fury road", "blade runner 2049", "the prestige", "memento",
    "django unchained", "inglourious basterds", "kill bill", "tenet",
    "back to the future", "indiana jones", "alien", "terminator", "rocky",
    "the silence of the lambs", "se7en", "the shawshank redemption", "coco", "up",
    "the wolf of wall street", "shutter island", "catch me if you can", "the departed",
    "saving private ryan", "schindlers list", "the pianist", "braveheart", "300",
    "watchmen", "deadpool", "logan", "doctor strange", "thor ragnarok",
    "guardians of the galaxy", "captain america", "ant man", "batman begins",
    "man of steel", "wonder woman", "aquaman", "the batman", "top gun maverick",
    "mission impossible", "john wick", "james bond", "skyfall", "casino royale",
    "the bourne identity", "pirates of the caribbean", "alice in wonderland",
    "charlie and the chocolate factory", "edward scissorhands", "beetlejuice",
    "ghostbusters", "men in black", "et", "jaws", "the shining", "psycho",
    "vertigo", "rear window", "2001 a space odyssey", "a clockwork orange",
    "full metal jacket", "apocalypse now", "taxi driver", "raging bull", "scarface",
    "heat"
]

actors_list = [
    "tom hanks", "leonardo dicaprio", "brad pitt", "robert downey jr",
    "scarlett johansson", "morgan freeman", "tom cruise", "will smith",
    "johnny depp", "keanu reeves", "christian bale", "matt damon",
    "natalie portman", "emma stone", "ryan gosling", "denzel washington",
    "samuel l jackson", "robert de niro", "al pacino", "meryl streep",
    "tom holland", "zendaya", "timothee chalamet", "cillian murphy",
    "margot robbie", "ryan reynolds", "hugh jackman", "chris evans",
    "chris hemsworth", "mark ruffalo", "anne hathaway", "jennifer lawrence",
    "joaquin phoenix", "heath ledger", "harrison ford", "arnold schwarzenegger",
    "sylvester stallone", "bruce willis", "nicolas cage", "jim carrey"
]

movie_templates = {
    "movieinfo": [
        "tell me about [{m}](movie)",
        "what is [{m}](movie) about",
        "give me info on [{m}](movie)",
        "can you summarize [{m}](movie)",
        "i want to know more about the movie [{m}](movie)",
        "what is the plot of [{m}](movie)",
        "describe the film [{m}](movie)",
        "info about [{m}](movie) please",
        "synopsis of [{m}](movie)",
        "what happens in [{m}](movie)",
        "give me a summary of [{m}](movie)",
        "could you tell me the story of [{m}](movie)",
        "explain the plot of [{m}](movie)",
        "what is the movie [{m}](movie) all about",
        "share some details about [{m}](movie)",
        "i need information regarding [{m}](movie)",
        "overview of [{m}](movie)",
        "tell me the storyline of [{m}](movie)",
        "what can you tell me about [{m}](movie)",
        "briefly describe [{m}](movie)"
    ],
    "director": [
        "who directed [{m}](movie)",
        "who is the director of [{m}](movie)",
        "who made the movie [{m}](movie)",
        "director of [{m}](movie)",
        "who was behind [{m}](movie)",
        "can you tell me who directed [{m}](movie)",
        "which director filmed [{m}](movie)",
        "who directed the film [{m}](movie)",
        "name the director of [{m}](movie)",
        "by whom was [{m}](movie) directed",
        "who is the filmmaker of [{m}](movie)",
        "tell me who directed [{m}](movie)",
        "who was the director on [{m}](movie)",
        "who created the film [{m}](movie)",
        "do you know who directed [{m}](movie)",
        "which filmmaker made [{m}](movie)",
        "who shot [{m}](movie)",
        "who is credited as director for [{m}](movie)",
        "find the director of [{m}](movie)",
        "give me the name of the director of [{m}](movie)"
    ],
    "releaseYear": [
        "when was [{m}](movie) released",
        "what is the release date of [{m}](movie)",
        "which year did [{m}](movie) come out",
        "when did [{m}](movie) hit theaters",
        "release year of [{m}](movie)",
        "what year was [{m}](movie) made",
        "when was the movie [{m}](movie) released",
        "tell me the release date for [{m}](movie)",
        "how old is the movie [{m}](movie)",
        "when did [{m}](movie) release",
        "in what year was [{m}](movie) launched",
        "date of release for [{m}](movie)",
        "when did [{m}](movie) premiere",
        "what year did [{m}](movie) come out in cinemas",
        "can you give me the release year of [{m}](movie)",
        "when was [{m}](movie) first shown",
        "which year was [{m}](movie) released",
        "release date [{m}](movie)",
        "when did people first see [{m}](movie)",
        "what year is [{m}](movie) from"
    ],
    "actors": [
        "who starred in [{m}](movie)",
        "who are the main actors in [{m}](movie)",
        "cast of [{m}](movie)",
        "who played in [{m}](movie)",
        "who is the lead actor of [{m}](movie)",
        "which actors are in [{m}](movie)",
        "tell me the cast for [{m}](movie)",
        "who acted in [{m}](movie)",
        "main characters and actors in [{m}](movie)",
        "who was the main actor of [{m}](movie)",
        "list the actors of [{m}](movie)",
        "who plays the lead role in [{m}](movie)",
        "name the cast of [{m}](movie)",
        "who are the stars of [{m}](movie)",
        "which actors starred in [{m}](movie)",
        "can you list the cast of [{m}](movie)",
        "who featured in [{m}](movie)",
        "give me the main cast for [{m}](movie)",
        "who is in the movie [{m}](movie)",
        "actors in [{m}](movie)"
    ],
    "rating": [
        "what is the rating of [{m}](movie)",
        "how good is [{m}](movie)",
        "what score did [{m}](movie) get",
        "is [{m}](movie) a good movie",
        "reviews for [{m}](movie)",
        "what is the audience score of [{m}](movie)",
        "rate [{m}](movie)",
        "how is [{m}](movie) rated",
        "what are the ratings for [{m}](movie)",
        "is [{m}](movie) worth watching",
        "tell me the score of [{m}](movie)",
        "how many stars does [{m}](movie) have",
        "what do people think about [{m}](movie)",
        "popularity of [{m}](movie)",
        "give me the rating for [{m}](movie)",
        "what is the tmdb score of [{m}](movie)",
        "did [{m}](movie) get good reviews",
        "how well did [{m}](movie) score",
        "rating of [{m}](movie)",
        "check the rating of [{m}](movie)"
    ],
    "recommend": [
        "recommend movies like [{m}](movie)",
        "similar movies to [{m}](movie)",
        "what should i watch if i liked [{m}](movie)",
        "suggest a film like [{m}](movie)",
        "movies similar to [{m}](movie)",
        "if i love [{m}](movie) what else should i watch",
        "give me recommendations based on [{m}](movie)",
        "films like [{m}](movie)",
        "any movie recommendations similar to [{m}](movie)",
        "find movies like [{m}](movie)",
        "what is a good alternative to [{m}](movie)",
        "suggest something close to [{m}](movie)",
        "i liked [{m}](movie) recommend another one",
        "other movies in the style of [{m}](movie)",
        "recommend something similar to [{m}](movie)",
        "what films resemble [{m}](movie)",
        "more movies like [{m}](movie)",
        "give me films like [{m}](movie)",
        "can you recommend a movie like [{m}](movie)",
        "suggestions like [{m}](movie)"
    ],
    "poster": [
        "show me the poster of [{m}](movie)",
        "poster for [{m}](movie)",
        "can i see the cover of [{m}](movie)",
        "send me the image of [{m}](movie)",
        "display the movie poster for [{m}](movie)",
        "what does the poster of [{m}](movie) look like",
        "get the poster of [{m}](movie)",
        "show cover art for [{m}](movie)",
        "picture of [{m}](movie)",
        "movie poster [{m}](movie)",
        "i want to see the poster of [{m}](movie)",
        "find the poster for [{m}](movie)",
        "artwork of [{m}](movie)",
        "cover image of [{m}](movie)",
        "show me the cover for [{m}](movie)",
        "send the poster of [{m}](movie)",
        "give me the poster of [{m}](movie)",
        "poster [{m}](movie)",
        "look at the poster of [{m}](movie)",
        "can you show the poster of [{m}](movie)"
    ]
}

actor_movies_templates = [
    "which movies did [{a}](actor) play in",
    "what films has [{a}](actor) starred in",
    "movies with [{a}](actor)",
    "filmography of [{a}](actor)",
    "list movies starring [{a}](actor)",
    "what movies is [{a}](actor) in",
    "show me films with [{a}](actor)",
    "which films did [{a}](actor) act in",
    "give me a list of [{a}](actor) movies",
    "what are [{a}](actor) best movies",
    "tell me the movies [{a}](actor) played in",
    "in which movies did [{a}](actor) appear",
    "famous movies of [{a}](actor)",
    "what films did [{a}](actor) make",
    "find movies featuring [{a}](actor)"
]

lines = ['version: "3.1"\n', 'nlu:\n']

for idx, (intent, tmpls) in enumerate(movie_templates.items()):
    lines.append(f"- intent: {intent}\n")
    lines.append("  examples: |\n")
    start = (idx * 10) % (len(movies) - 20)
    selected_movies = movies[start : start + 20]
    for m in selected_movies:
        for t in tmpls:
            lines.append(f"    - {t.format(m=m)}\n")

lines.append("- intent: actor_movies\n")
lines.append("  examples: |\n")
for a in actors_list[:20]:
    for t in actor_movies_templates:
        lines.append(f"    - {t.format(a=a)}\n")

basic_intents = {
    "greeting": [
        "hi", "hello", "hey", "good morning", "good evening", "hi there",
        "hello bot", "hey there", "greetings", "howdy", "yo", "what's up",
        "hi how are you", "hello can you help me", "hey buddy", "good afternoon",
        "hello moviebot", "hi bot", "hey friend", "hiya"
    ],
    "bye": [
        "bye", "goodbye", "see you later", "see you", "exit", "quit",
        "have a nice day", "bye bye", "talk to you later", "cya", "i am leaving",
        "stop", "end conversation", "farewell", "good night", "see ya",
        "catch you later", "im done", "close chat", "bye bot"
    ],
    "help": [
        "help", "help me", "what can you do", "how do you work", "i need help",
        "what are your features", "can you assist me", "show me commands",
        "how can i use this bot", "what questions can i ask", "guide me",
        "explain what you do", "help please", "instructions", "what do you know",
        "how does this work", "can you help me find movies", "menu", "options", "info"
    ],
    "out_of_scope": [
        "what is the weather in paris", "book a table for 2", "order a pizza",
        "what time is it", "tell me a joke", "how to cook pasta",
        "what is the capital of france", "play some music", "translate this to french",
        "who won the world cup", "what is 2 plus 2", "i need a taxi",
        "how is the stock market today", "send an email to john", "set an alarm for 7am",
        "what is the temperature outside", "who is the president", "sing a song",
        "buy me a flight ticket", "how to fix my computer"
    ]
}

for intent, examples in basic_intents.items():
    lines.append(f"- intent: {intent}\n")
    lines.append("  examples: |\n")
    for ex in examples:
        lines.append(f"    - {ex}\n")

lines.append("- lookup: movie\n")
lines.append("  examples: |\n")
for m in movies:
    lines.append(f"    - {m}\n")

lines.append("- lookup: actor\n")
lines.append("  examples: |\n")
for a in actors_list:
    lines.append(f"    - {a}\n")

synonyms = {
    "spider man": ["spiderman", "spider-man"],
    "iron man": ["ironman", "iron-man"],
    "the lord of the rings": ["lotr", "lord of the rings"],
    "star wars": ["starwars"],
    "the dark knight": ["dark knight"],
    "robert downey jr": ["rdj", "robert downey junior"],
    "leonardo dicaprio": ["leo dicaprio", "dicaprio"]
}

for target, variants in synonyms.items():
    lines.append(f"- synonym: {target}\n")
    lines.append("  examples: |\n")
    for v in variants:
        lines.append(f"    - {v}\n")

with open("data/nlu.yml", "w", encoding="utf-8") as f:
    f.writelines(lines)

print(f"✅ Fichier data/nlu.yml généré avec succès ! Total : {len(lines)} lignes.")