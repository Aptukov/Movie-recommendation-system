import pandas as pd

ratings_data = pd.read_csv("ratings.csv")
movies_names = pd.read_csv("movies.csv")

movies_data = pd.merge(ratings_data, movies_names, on="movieId")

ratings_mean_count = pd.DataFrame(movies_data.groupby("title")["rating"].mean())

ratings_mean_count["rating_count"] = pd.DataFrame(movies_data.groupby("title")["rating"].count())

ratings_mean_count["rating_count"] = ratings_mean_count["rating_count"].astype(int)

promising_films = ratings_mean_count.loc[ratings_mean_count["rating_count"] >= 5]

userid = int(input("ID пользователя: "))
n = int(input("Количество фильмов: "))

user_genres = movies_names["genres"].str.get_dummies("|")

mean_genres = user_genres.mean().sort_values(ascending=False)

like_genres = mean_genres[:3]

like_genres = like_genres.index.values.tolist()