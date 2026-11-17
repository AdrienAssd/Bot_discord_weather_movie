import os
from dotenv import load_dotenv
from tmdbv3api import TMDb, Movie

load_dotenv()

tmdb = TMDb()
tmdb.api_key = os.getenv("TMDB_API_KEY")
tmdb.language = "en"

movie_api = Movie()
search = movie_api.search("Iron Man")

if search:
    first_movie = search[0]
    details = movie_api.details(first_movie.id)
    
    directors = [c.name for c in details.casts.crew if c.job == "Director"]
    actors = [a.name for a in details.casts.cast[:3]]
    
    print(f"Film : {details.title} ({details.release_date})")
    print(f"Réalisateur : {', '.join(directors)}")
    print(f"Acteurs : {', '.join(actors)}")
    print(f"Synopsis : {details.overview}")