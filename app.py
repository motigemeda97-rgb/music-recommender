
import json
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="Afaan Oromo's Music Recommender",
    page_icon="🎵",
    layout="wide"
)

st.markdown("""
<style>
    .block-container {
        max-width: 1000px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .hero {
        padding: 2rem;
        border-radius: 20px;
        background: linear-gradient(135deg, #182848, #4b6cb7);
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }

    .hero h1 {
        color: white;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }

    .hero p {
        color: #eef3ff;
        font-size: 1.1rem;
    }

    div.stButton > button {
        width: 100%;
        border-radius: 12px;
        min-height: 3rem;
        font-weight: bold;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid rgba(128, 128, 128, 0.25);
        border-radius: 16px;
        padding: 12px;
        margin-bottom: 12px;
    }

    h2, h3 {
        letter-spacing: -0.3px;
    }

    div[data-testid="stSelectbox"] {
        margin-bottom: 12px;
    }
</style>

<div class="hero">
    <h1>🎵 Afaan Oromo's Music Recommender</h1>
    <p>Find the songs that match your mood and your taste.</p>
    <p>Discover your next favorite Afan Oromo song! ❤️</p>
</div>
""", unsafe_allow_html=True)


# Find and load the saved song library
project_folder = Path(__file__).parent
songs_file = project_folder / "songs.json"

try:
    with open(songs_file, "r", encoding="utf-8") as file:
        songs = json.load(file)
except FileNotFoundError:
    st.error("songs.json was not found in the project folder.")
    st.stop()
except json.JSONDecodeError:
    st.error("songs.json contains invalid JSON.")
    st.stop()

if not songs:
    st.warning("Your song library is empty.")
    st.stop()


# Calculate similarity using our existing scoring rules
def calculate_similarity(song, selected_song):
    score = 0

    if song["genre"] == selected_song["genre"]:
        score += 2

    if song["mood"] == selected_song["mood"]:
        score += 2

    if song["energy"] == selected_song["energy"]:
        score += 1

    return score


# Recommendation controls
st.subheader("🎧 Find Your Next Favorite Song")

user_mood = st.selectbox(
    "How are you feeling today?",
    ["Happy", "Calm", "Energetic", "Sad"]
)

selected_index = st.selectbox(
    "Choose a song you already like:",
    range(len(songs)),
    format_func=lambda i: (
        f"{songs[i]['title']} — {songs[i]['artist']}"
    )
)

selected_song = songs[selected_index]

st.write(f"**Selected song:** {selected_song['title']}")
st.write(
    f"**Genre:** {selected_song['genre']} | "
    f"**Mood:** {selected_song['mood']} | "
    f"**Energy:** {selected_song['energy']}/5"
)


# Generate recommendations when the button is clicked
if st.button("🎵 Recommend Songs", type="primary"):

    recommendations = []

    for index, song in enumerate(songs):

        # Do not recommend the song the user selected
        if index == selected_index:
            continue

        score = calculate_similarity(song, selected_song)

        # Extra points for matching the user's chosen mood
        if song["mood"] == user_mood:
            score += 3

        # Explain why this song matches
        reasons = []

        if song["genre"] == selected_song["genre"]:
            reasons.append("same genre (+2)")

        if song["mood"] == selected_song["mood"]:
            reasons.append("same mood (+2)")

        if song["energy"] == selected_song["energy"]:
            reasons.append("same energy level (+1)")

        if song["mood"] == user_mood:
            reasons.append("matches your chosen mood (+3)")

        recommendations.append({
            "score": score,
            "song": song,
            "reasons": reasons
        })

    # Highest-scoring songs first
    recommendations.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    # Display up to two positive-score recommendations
    top_matches = [
        item for item in recommendations
        if item["score"] > 0
    ][:2]

    st.subheader("✨ Your Recommendations")

    if not top_matches:
        st.info("Sorry, no similar songs found.")
    else:
        for item in top_matches:
            song = item["song"]

            with st.container(border=True):
                st.subheader(f"🎵 {song['title']}")
                st.write(f"🎤 **Artist:** {song['artist']}")
                st.write(f"🎼 **Genre:** {song['genre']}")
                st.write(f"😊 **Mood:** {song['mood']}")
                st.write(f"⚡ **Energy:** {song['energy']}/5")
                st.write(
                    f"🏆 **Similarity score:** {item['score']}"
                )

                if item["reasons"]:
                    st.write(
                        "**Why this song?** "
                        + ", ".join(item["reasons"])
                    )


# Display the complete library
st.divider()
st.subheader("🎶 Your Song Library")


# Function to clear the search field
def clear_search():
    st.session_state["song_search"] = ""


# Clear search button
st.button(
    "✖ Clear search",
    on_click=clear_search
)


# Search box with automatic updates
search_query = st.text_input(
    "🔍 Search songs",
    placeholder="Type a song title, artist, genre, or mood...",
    key="song_search"
)


# Count the total songs
st.write(f"Total songs: {len(songs)}")


# Find songs that match the search
filtered_songs = []

for song in songs:
    if (
        search_query.lower() in song["title"].lower()
        or search_query.lower() in song["artist"].lower()
        or search_query.lower() in song["genre"].lower()
        or search_query.lower() in song["mood"].lower()
    ):
        filtered_songs.append(song)


# Display the matching songs
if not filtered_songs:
    st.info("No songs found. Try another search.")
else:
    st.write(f"Songs found: {len(filtered_songs)}")

    for song in filtered_songs:
        with st.container(border=True):
            st.write(f"**{song['title']}**")
            st.write(f"🎤 Artist: {song['artist']}")
            st.write(f"🎼 Genre: {song['genre']}")
            st.write(f"😊 Mood: {song['mood']}")
            st.write(f"⚡ Energy: {song['energy']}/5")

            if song.get("favorite", False):
                st.write("❤️ Favorite")