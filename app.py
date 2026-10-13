
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


# Add a new song to the library
st.divider()
st.subheader("➕ Add a New Song")

with st.form("add_song_form"):
    new_title = st.text_input("Song title")
    new_artist = st.text_input("Artist name")

    new_genre = st.selectbox(
        "Genre",
        ["Waltz", "Shawaa", "Other"]
    )

    new_mood = st.selectbox(
        "Mood",
        ["Happy", "Calm", "Energetic", "Sad"]
    )

    new_energy = st.slider(
        "Energy level",
        min_value=1,
        max_value=5,
        value=3
    )

    add_song_clicked = st.form_submit_button("➕ Add Song")


# Save the new song when the form is submitted
if add_song_clicked:
    if not new_title.strip() or not new_artist.strip():
        st.error("Please enter both the song title and artist.")
    elif any(
        song["title"].strip().casefold() == new_title.strip().casefold()
        and song["artist"].strip().casefold() == new_artist.strip().casefold()
        for song in songs
    ):
        st.warning("This song by this artist is already in your library.")
    else:
        new_song = {
            "title": new_title.strip(),
            "artist": new_artist.strip(),
            "genre": new_genre,
            "mood": new_mood,
            "energy": new_energy,
            "favorite": False
        }

        songs.append(new_song)

        with open(songs_file, "w", encoding="utf-8") as file:
            json.dump(songs, file, indent=4, ensure_ascii=False)

        st.success(f"Added '{new_title.strip()}' successfully!")



# Edit an existing song
st.divider()
st.subheader("✏️ Edit an Existing Song")

if songs:
    edit_index = st.selectbox(
        "Choose a song to edit:",
        range(len(songs)),
        format_func=lambda i: (
            f"{songs[i]['title']} — {songs[i]['artist']}"
        ),
        key="edit_song_index"
    )

    selected_edit_song = songs[edit_index]

    with st.form("edit_song_form"):
        edited_title = st.text_input(
            "Song title",
            value=selected_edit_song["title"]
        )

        edited_artist = st.text_input(
            "Artist name",
            value=selected_edit_song["artist"]
        )

        genre_options = ["Waltz", "Shawaa", "Other"]
        current_genre = selected_edit_song["genre"]

        if current_genre not in genre_options:
            genre_options.append(current_genre)

        edited_genre = st.selectbox(
            "Genre",
            genre_options,
            index=genre_options.index(current_genre)
        )

        mood_options = ["Happy", "Calm", "Energetic", "Sad"]
        current_mood = selected_edit_song["mood"]

        if current_mood not in mood_options:
            mood_options.append(current_mood)

        edited_mood = st.selectbox(
            "Mood",
            mood_options,
            index=mood_options.index(current_mood)
        )

        edited_energy = st.slider(
            "Energy level",
            min_value=1,
            max_value=5,
            value=selected_edit_song["energy"]
        )

        edit_clicked = st.form_submit_button("💾 Save Changes")

    if edit_clicked:
        if not edited_title.strip() or not edited_artist.strip():
            st.error("Please enter both the song title and artist.")
        elif any(
            i != edit_index
            and song["title"].strip().casefold() == edited_title.strip().casefold()
            and song["artist"].strip().casefold() == edited_artist.strip().casefold()
            for i, song in enumerate(songs)
        ):
            st.warning("Another song by this artist already has that title.")
        else:
            songs[edit_index]["title"] = edited_title.strip()
            songs[edit_index]["artist"] = edited_artist.strip()
            songs[edit_index]["genre"] = edited_genre
            songs[edit_index]["mood"] = edited_mood
            songs[edit_index]["energy"] = edited_energy

            with open(songs_file, "w", encoding="utf-8") as file:
                json.dump(songs, file, indent=4, ensure_ascii=False)

            st.success("Song updated successfully! 🎉")
else:
    st.info("Add a song before trying to edit one.")



# Delete a song from the library
st.divider()
st.subheader("🗑️ Delete a Song")

if songs:
    delete_index = st.selectbox(
        "Choose a song to delete:",
        range(len(songs)),
        format_func=lambda i: (
            f"{songs[i]['title']} — {songs[i]['artist']}"
        ),
        key="delete_song_index"
    )

    song_to_delete = songs[delete_index]

    st.warning(
        f"You selected: {song_to_delete['title']} "
        f"by {song_to_delete['artist']}"
    )

    confirm_delete = st.checkbox(
        "Yes, I want to delete this song.",
        key="confirm_delete_song"
    )

    if st.button("🗑️ Delete Song"):
        if confirm_delete:
            deleted_title = songs[delete_index]["title"]

            songs.pop(delete_index)

            with open(songs_file, "w", encoding="utf-8") as file:
                json.dump(songs, file, indent=4, ensure_ascii=False)

            st.success(f"'{deleted_title}' was deleted successfully! 🎉")
            st.rerun()
        else:
            st.error("Please confirm before deleting the song.")
else:
    st.info("There are no songs to delete.")


# Calculate similarity using our existing scoring rules
def calculate_similarity(song, selected_song):
    score = 0

    if song["genre"].casefold() == selected_song["genre"].casefold():
        score += 2

    if song["mood"].casefold() == selected_song["mood"].casefold():
        score += 2

    if song["energy"] == selected_song["energy"]:
        score += 1

    return score


# Recommendation controls
st.divider()
st.subheader("🎧 Find Your Next Favorite Song")

if not songs:
    st.info("Add a song to your library to get recommendations.")
else:
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

    if st.button("🎵 Recommend Songs", type="primary"):
        recommendations = []

        for index, song in enumerate(songs):
            # Do not recommend the selected song itself
            if index == selected_index:
                continue

            score = calculate_similarity(song, selected_song)

            # Extra points for matching the user's chosen mood
            if song["mood"].casefold() == user_mood.casefold():
                score += 3

            # Explain why the song matches
            reasons = []

            if song["genre"].casefold() == selected_song["genre"].casefold():
                reasons.append("same genre (+2)")

            if song["mood"].casefold() == selected_song["mood"].casefold():
                reasons.append("same mood (+2)")

            if song["energy"] == selected_song["energy"]:
                reasons.append("same energy level (+1)")

            if song["mood"].casefold() == user_mood.casefold():
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



# Manage favorite songs
st.divider()
st.subheader("❤️ Manage Favorite Songs")

if songs:
    favorite_index = st.selectbox(
        "Choose a song:",
        range(len(songs)),
        format_func=lambda i: (
            f"{songs[i]['title']} — {songs[i]['artist']}"
        ),
        key="favorite_song_index"
    )

    selected_favorite_song = songs[favorite_index]

    if selected_favorite_song.get("favorite", False):
        st.write("❤️ This song is currently a favorite.")

        if st.button("💔 Remove from Favorites"):
            songs[favorite_index]["favorite"] = False

            with open(songs_file, "w", encoding="utf-8") as file:
                json.dump(songs, file, indent=4, ensure_ascii=False)

            st.success("Song removed from favorites!")
            st.rerun()

    else:
        st.write("This song is not currently a favorite.")

        if st.button("❤️ Add to Favorites"):
            songs[favorite_index]["favorite"] = True

            with open(songs_file, "w", encoding="utf-8") as file:
                json.dump(songs, file, indent=4, ensure_ascii=False)

            st.success("Song added to favorites!")
            st.rerun()
else:
    st.info("Add a song before managing favorites.")



# Filter to show favorite songs only
st.divider()
st.subheader("💖 Your Favorite Songs")

show_favorites_only = st.checkbox(
    "Show only my favorite songs",
    key="show_favorites_only"
)

if show_favorites_only:
    favorite_songs = [
        song for song in songs
        if song.get("favorite", False)
    ]

    if not favorite_songs:
        st.info("You haven't added any favorite songs yet.")
    else:
        st.write(f"Favorite songs: {len(favorite_songs)}")

        for song in favorite_songs:
            with st.container(border=True):
                st.write(f"❤️ **{song['title']}**")
                st.write(f"🎤 Artist: {song['artist']}")
                st.write(f"🎼 Genre: {song['genre']}")
                st.write(f"😊 Mood: {song['mood']}")
                st.write(f"⚡ Energy: {song['energy']}/5")


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
    query = search_query.strip().casefold()

    if (
        query in song["title"].casefold()
        or query in song["artist"].casefold()
        or query in song["genre"].casefold()
        or query in song["mood"].casefold()
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
