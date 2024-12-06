import streamlit as st
import pandas as pd
import pickle
from sklearn.metrics.pairwise import cosine_similarity
import requests
import warnings

# Suppress Streamlit's deprecation warnings
warnings.filterwarnings("ignore", category=UserWarning, message=".*deprecated.*")

# Load the saved models
movies_dict = pickle.load(open('/Users/nandhinivijayakumar/Desktop/ADM/FinalProject_NandhiniVijayakumar/movie_dict.pkl', 'rb'))
movies = pd.DataFrame.from_dict(movies_dict)
similarity = pickle.load(open('/Users/nandhinivijayakumar/Desktop/ADM/FinalProject_NandhiniVijayakumar/similarity.pkl', 'rb'))

# Function to fetch movie posters from TMDb API
def fetch_poster(movie_id):
    api_key = '020b311fe0559698373a16008dc6a672'
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US'
    response = requests.get(url)
    data = response.json()
    return "https://image.tmdb.org/t/p/w500/" + data.get('poster_path', '')

# Function to fetch movie details (e.g., genres, rating)
def fetch_movie_details(movie_id):
    api_key = '020b311fe0559698373a16008dc6a672'
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US'
    response = requests.get(url)
    data = response.json()
    return data['genres'], data['vote_average'], data['overview']

# Function to get movie recommendations
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    
    recommended_movies = []
    recommended_movies_posters = []
    recommended_movies_details = []
    for x in movies_list:
        movie_id = movies.iloc[x[0]].movie_id
        recommended_movies.append(movies.iloc[x[0]].title)
        recommended_movies_posters.append(fetch_poster(movie_id))
        genres, rating, overview = fetch_movie_details(movie_id)
        recommended_movies_details.append((genres, rating, overview))
    
    return recommended_movies, recommended_movies_posters, recommended_movies_details

# Streamlit UI
st.title("Movie Recommendation System")

# Dropdown menu for selecting a movie
movie_title = st.selectbox("Select a Movie", movies['title'].tolist())

if movie_title:
    # Fetch recommendations when a movie title is selected
    recommended_movies, recommended_movies_posters, recommended_movies_details = recommend(movie_title)
    
    # Display the selected movie details
    st.subheader(f"Selected Movie: {movie_title}")
    selected_movie_id = movies[movies['title'] == movie_title].iloc[0]['movie_id']
    selected_genres, selected_rating, selected_overview = fetch_movie_details(selected_movie_id)
    
    st.write(f"Genres: {', '.join([genre['name'] for genre in selected_genres])}")
    st.write(f"Rating: {selected_rating}/10")
    st.write(f"Overview: {selected_overview}")
    st.image(fetch_poster(selected_movie_id), use_container_width=True)
    
    # Display recommended movies
    st.subheader(f"Recommended movies based on '{movie_title}':")
    for i in range(5):
        st.write(f"{i+1}. {recommended_movies[i]}")
        st.write(f"Genres: {', '.join([genre['name'] for genre in recommended_movies_details[i][0]])}")
        st.write(f"Rating: {recommended_movies_details[i][1]}/10")
        st.write(f"Overview: {recommended_movies_details[i][2]}")
        st.image(recommended_movies_posters[i], use_container_width=True)
else:
    st.write("Please select a movie to get recommendations.")
