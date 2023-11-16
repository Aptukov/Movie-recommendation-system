# Импортируем pandas для работы с данными
import pandas as pd

# Загружаем базы данных
ratings_data = pd.read_csv("ratings.csv")
movies_names = pd.read_csv("movies.csv")

# Объединяем 2 датафрейма в один
movies_data = pd.merge(ratings_data, movies_names, on="movieId")

# Просим ввести id нужного пользователя и количество фильмов (n)
# К примеру, возьмём id пользователя = 10 и n = 20 (сколько фильмов хотим получить по итогу)
userid = int(input("ID пользователя: "))
n = int(input("Количество запрашиваемых фильмов: "))

# Создаём датафрейм пользователя, с его: оценками фильмов, жанрами оценённых фильмов
# Преобразуем столбец genres в несколько столбцов с названиями жанров
# В ячейках этих столбцов будет: 0(фильм не этого жанра) и 1(фильм этого жанра)
user_genres = movies_data.loc[movies_data["userId"] == userid]

# Оставляем фильмы с рейтингом >= 4
user_genres = user_genres[user_genres["rating"] >= 4]

# Делим столбец жанра на несколько столбцов по жанрам
user_genres = user_genres["genres"].str.get_dummies("|")

# Высчитываем среднее значение каждого жанра
mean_genres = user_genres.mean().sort_values(ascending=False)

# Оставляем 2 любимых жанра и кладём их в список
user_like_genres = mean_genres[:3].index.values.tolist()

# Удаляем все фильмы, которые смотрел пользователь
movies_data = movies_data.loc[movies_data["userId"] != userid]

# Создаём основной датафрейм: название фильма, средний рейтинг, количество оценок, средняя релевантность, жанр фильма
main_df = pd.DataFrame(movies_data.groupby("title")["rating"].mean())

# Переименовываем столбец "rating" в "mean_rating"
main_df = main_df.rename(columns={"rating": "mean_rating"})

# Добавляем столбец "актуальность оценок"
main_df["mean_timestamp"] = movies_data.groupby("title")["timestamp"].mean()

# Добавляем столбец "количество оценок фильма" и преобразуем все его значения в тип "int"
main_df["rating_count"] = movies_data.groupby("title")["rating"].count().astype(int)

# Добавляем столбец "жанр/жанры"
main_df["genres"] = movies_data.groupby("title")["genres"]

# Оставляем в основном датафрейме все фильмы с количеством оценок >= 10
main_df = main_df.loc[main_df["rating_count"] >= 10]

# Оставляем фильмы, жанр которых совпадает с одним из любимых жанров пользователя
main_df["genres"] = main_df["genres"].apply(lambda x: x if (user_like_genres[0] in str(x) or user_like_genres[1] in str(x) or user_like_genres[2] in str(x)) else None)
main_df = main_df.dropna()

# Сортируем по рейтингу
main_df = main_df.sort_values(by="mean_rating", ascending=False)

# Оставляем первые n фильмов
main_df = main_df[:n]

# Сортируем по актуальности оценок
main_df = main_df.sort_values(by="mean_timestamp", ascending=False)

# Преобразуем названия фильмов, средний рейтинг, среднее время оценки и жанры в списки
title_list = main_df.index.values.tolist()
rating_list = main_df["mean_rating"].tolist()
timestamp_list = main_df["mean_timestamp"].tolist()
genres_list = main_df["genres"].tolist()

# Функция по вычислению релевантности
def relevance(t, l):
    return round((0.00000001*int(t)*int(l)), 1)

# Выводим фильмы, релевантность и объяснение к каждому фильму
genres = user_like_genres[0]
print("Рекомендуемые фильмы:")
for i in range(n):
    print(title_list[i]+". Этот фильм имеет релевантность -", relevance(timestamp_list[i], rating_list[i]))
    if user_like_genres[0] in str(genres_list[i]):
        genres = user_like_genres[0]
    elif user_like_genres[1] in str(genres_list[i]):
        genres = user_like_genres[1]
    elif user_like_genres[2] in str(genres_list[i]):
        genres = user_like_genres[2]
    elif user_like_genres[0] in str(genres_list[i]) or user_like_genres[1] in str(genres_list[i] or user_like_genres[2] in str(genres_list[i])):
        print("Алгоритм выбрал этот фильм, так как он ваших любимих жанров - "+user_like_genres[0]+","+user_like_genres[1]+", и имеет высокую оценку -"+str(round(rating_list[i], 1)))
    elif (user_like_genres[0] == "(no genres listed)") or (user_like_genres[1] == "(no genres listed)"):
        print("Алгоритм выбрал этот фильм, так как вам нравятся фильмы на данную тематику, а также он имеет высокую оценку - " + str(round(rating_list[i], 1)))
    print("Алгоритм выбрал этот фильм, так как он вашего любимого жанра - " + genres + ", и имеет высокую оценку - "+str(round(rating_list[i], 1)))
    print("") #Для более удобного чтения разделим выводы пустой строкой

# Ниже представлен вывод для пользователя с id = 10, n = 20

# Рекомендуемые фильмы:
# Parasite (2019). Этот фильм имеет релевантность - 62.8
# Алгоритм выбрал этот фильм, так как он вашего любимого жанра - Drama, и имеет высокую оценку - 4.2
#
# Twin Peaks (1989). Этот фильм имеет релевантность - 62.4
# Алгоритм выбрал этот фильм, так как он вашего любимого жанра - Drama, и имеет высокую оценку - 4.3
#
# Fool's Day (2013). Этот фильм имеет релевантность - 61.7
# Алгоритм выбрал этот фильм, так как он вашего любимого жанра - Drama, и имеет высокую оценку - 4.2
#
# Band of Brothers (2001). Этот фильм имеет релевантность - 61.1
# Алгоритм выбрал этот фильм, так как он вашего любимого жанра - Action, и имеет высокую оценку - 4.4
#
# Over the Garden Wall (2013). Этот фильм имеет релевантность - 61.1
# Алгоритм выбрал этот фильм, так как он вашего любимого жанра - Drama, и имеет высокую оценку - 4.3
#
# Pollyanna (2003). Этот фильм имеет релевантность - 60.8
# Алгоритм выбрал этот фильм, так как он вашего любимого жанра - Drama, и имеет высокую оценку - 4.4
#
# Teens in the Universe (1975). Этот фильм имеет релевантность - 60.6
# Алгоритм выбрал этот фильм, так как он вашего любимого жанра - Sci-Fi, и имеет высокую оценку - 4.2
#
# The House That Swift Built (1982). Этот фильм имеет релевантность - 59.5
# Алгоритм выбрал этот фильм, так как он вашего любимого жанра - Drama, и имеет высокую оценку - 4.2
#
# Guten Tag, Ramón (2013). Этот фильм имеет релевантность - 58.9
# Алгоритм выбрал этот фильм, так как он вашего любимого жанра - Drama, и имеет высокую оценку - 4.2
#
# Lives of Others, The (Das leben der Anderen) (2006). Этот фильм имеет релевантность - 55.1
# Алгоритм выбрал этот фильм, так как он вашего любимого жанра - Drama, и имеет высокую оценку - 4.2
#
# Fight Club (1999). Этот фильм имеет релевантность - 52.3
# Алгоритм выбрал этот фильм, так как он вашего любимого жанра - Action, и имеет высокую оценку - 4.2
#
# 12 Angry Men (1957). Этот фильм имеет релевантность - 50.2
# Алгоритм выбрал этот фильм, так как он вашего любимого жанра - Drama, и имеет высокую оценку - 4.2
#
# Godfather: Part II, The (1974). Этот фильм имеет релевантность - 49.0
# Алгоритм выбрал этот фильм, так как он вашего любимого жанра - Drama, и имеет высокую оценку - 4.3
#
# Godfather, The (1972). Этот фильм имеет релевантность - 49.0
# Алгоритм выбрал этот фильм, так как он вашего любимого жанра - Drama, и имеет высокую оценку - 4.3
#
# One Flew Over the Cuckoo's Nest (1975). Этот фильм имеет релевантность - 48.6
# Алгоритм выбрал этот фильм, так как он вашего любимого жанра - Drama, и имеет высокую оценку - 4.2
#
# Shawshank Redemption, The (1994). Этот фильм имеет релевантность - 48.2
# Алгоритм выбрал этот фильм, так как он вашего любимого жанра - Drama, и имеет высокую оценку - 4.4
#
# Seven Samurai (Shichinin no samurai) (1954). Этот фильм имеет релевантность - 47.8
# Алгоритм выбрал этот фильм, так как он вашего любимого жанра - Action, и имеет высокую оценку - 4.3
#
# Sunset Blvd. (a.k.a. Sunset Boulevard) (1950). Этот фильм имеет релевантность - 47.2
# Алгоритм выбрал этот фильм, так как он вашего любимого жанра - Drama, и имеет высокую оценку - 4.2
#
# Schindler's List (1993). Этот фильм имеет релевантность - 47.0
# Алгоритм выбрал этот фильм, так как он вашего любимого жанра - Drama, и имеет высокую оценку - 4.2
#
# Casablanca (1942). Этот фильм имеет релевантность - 46.8
# Алгоритм выбрал этот фильм, так как он вашего любимого жанра - Drama, и имеет высокую оценку - 4.2