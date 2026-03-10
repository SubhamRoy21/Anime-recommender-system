import streamlit as st
import pickle
import pandas as pd
import requests

st.set_page_config(page_title="Anime Recommender",layout="wide")

# -----------------------------
# Load Model Files
# -----------------------------

anime_user_data = pickle.load(open('anime_user_data.pkl','rb'))
anime_data = pickle.load(open('anime_data.pkl','rb'))
ratings_matrix = pickle.load(open('ratings_matrix.pkl','rb'))
similarity = pickle.load(open('similarity.pkl','rb'))
anime_df = pickle.load(open('anime.pkl','rb'))

# -----------------------------
# Fetch anime poster
# -----------------------------

def fetch_poster(anime_name):

    url = f"https://api.jikan.moe/v4/anime?q={anime_name}&limit=1"

    data = requests.get(url).json()

    try:
        return data['data'][0]['images']['jpg']['image_url']
    except:
        return "https://via.placeholder.com/210x295?text=No+Image"


# -----------------------------
# Recommendation Function
# -----------------------------

anime_names = list(anime_user_data['name'].unique())

def recommend(anime):
    index = anime_names.index(anime)

    distances = similarity[index]

    anime_list = sorted(list(enumerate(distances)),
     reverse=True,
    key=lambda x:x[1])[1:11]

    recommended = []
    for i in anime_list:
        name = anime_names[i[0]]
        poster = fetch_poster(name)
        recommended.append((name,poster))

    return recommended


# -----------------------------
# Sidebar
# -----------------------------

st.sidebar.title("Anime Recommender")

option = st.sidebar.selectbox(
    "Select Feature",
    ["Top 25 Anime","Top Anime by Community","Recommend by Anime Name","Recommend by Genre"]
)

# -----------------------------
# TOP ANIME SECTION
# -----------------------------

if option == "Top 25 Anime":

    st.title("Top 25 Anime")

    url = "https://api.jikan.moe/v4/top/anime"

    data = requests.get(url).json()

    animes = data['data'][:100]

    cols = st.columns(5)

    for i,anime in enumerate(animes):

        with cols[i%5]:

            st.image(anime['images']['jpg']['image_url'])
            st.write(anime['title'])
            st.write("⭐",anime['score'])


elif option == "Top Anime by Community":

    st.title("Top Anime by Community")

    top_animes = anime_df.sort_values("members", ascending=False).head(20)

    cols = st.columns(5)

    for i,row in enumerate(top_animes.itertuples()):

        poster = fetch_poster(row.name)

        with cols[i % 5]:

            st.image(poster)
            st.write(row.name)
            st.write("Members:", row.members)


# -----------------------------
# RECOMMEND BY ANIME
# -----------------------------
elif option == "Recommend by Anime Name":
    st.title("🎬 Anime Based Recommendation")
    st.write("Select an anime to get recommendations based on user ratings")
    anime = st.selectbox("Select Anime",anime_user_data['name'].unique())
    # st.button("Recommend")
    if st.button("Recommend"):
        recommendations = recommend(anime)

        cols = st.columns(5)

        for i,rec in enumerate(recommendations):

            with cols[i%5]:

                st.image(rec[1])
                st.write(rec[0])


# -----------------------------
# RECOMMEND BY GENRE
# -----------------------------

elif option == "Recommend by Genre":

    st.title("🎭 Genre Based Recommendation")

    genres = anime_df['genre'].dropna().str.split(',').explode().unique()

    selected_genre = st.selectbox("Choose Genre",genres)

    filtered = anime_df[anime_df['genre'].str.contains(selected_genre,na=False)]

    top = filtered.sort_values("rating",ascending=False).head(10)

    cols = st.columns(5)

    for i,row in enumerate(top.itertuples()):

        poster = fetch_poster(row.name)

        with cols[i%5]:

            st.image(poster)
            st.write(row.name)