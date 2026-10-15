
import json
from pathlib import Path

import streamlit as st
from supabase import create_client


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Afaan Oromo's Music Recommender",
    page_icon="🎵",
    layout="wide"
)


# --------------------------------------------------
# SUPABASE ADMIN AUTHENTICATION
# --------------------------------------------------

def verify_admin_token(access_token):
    """Verify that the current token belongs to an admin."""
    try:
        client = create_client(
            st.secrets["SUPABASE_URL"],
            st.secrets["SUPABASE_KEY"]
        )

        client.postgrest.auth(access_token)

        result = client.rpc("is_admin").execute()

        return result.data is True

    except Exception:
        return False


# Initialize session information
if "is_admin" not in st.session_state:
    st.session_state["is_admin"] = False

if "admin_email" not in st.session_state:
    st.session_state["admin_email"] = ""

if "admin_access_token" not in st.session_state:
    st.session_state["admin_access_token"] = ""


# Recheck admin permission on each app rerun
saved_token = st.session_state["admin_access_token"]

if saved_token:
    if verify_admin_token(saved_token):
        st.session_state["is_admin"] = True
    else:
        st.session_state["is_admin"] = False
        st.session_state["admin_email"] = ""
        st.session_state["admin_access_token"] = ""
else:
    st.session_state["is_admin"] = False
    st.session_state["admin_email"] = ""


# --------------------------------------------------
# PAGE DESIGN
# --------------------------------------------------

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


# --------------------------------------------------
# ADMIN LOGIN AND LOGOUT
# --------------------------------------------------

st.divider()
st.subheader("🔐 Admin Login")

if st.session_state["is_admin"]:
    st.success(
        f"Logged in as admin: "
        f"{st.session_state['admin_email']}"
    )

    if st.button("🚪 Admin Logout"):
        st.session_state["is_admin"] = False
        st.session_state["admin_email"] = ""
        st.session_state["admin_access_token"] = ""
        st.rerun()

else:
    with st.form("admin_login_form"):
        admin_email = st.text_input("Admin email")

        admin_password = st.text_input(
            "Admin password",
            type="password"
        )

        login_clicked = st.form_submit_button("🔑 Sign In")

    if login_clicked:
        if not admin_email.strip() or not admin_password:
            st.error("Please enter your email and password.")
        else:
            try:
                login_client = create_client(
                    st.secrets["SUPABASE_URL"],
                    st.secrets["SUPABASE_KEY"]
                )

                response = login_client.auth.sign_in_with_password({
                    "email": admin_email.strip(),
                    "password": admin_password
                })

                if response.session:
                    access_token = response.session.access_token

                    login_client.postgrest.auth(access_token)

                    admin_check = login_client.rpc(
                        "is_admin"
                    ).execute()

                    if admin_check.data is True:
                        st.session_state["is_admin"] = True
                        st.session_state["admin_email"] = (
                            admin_email.strip()
                        )
                        st.session_state["admin_access_token"] = (
                            access_token
                        )

                        st.rerun()

                    else:
                        st.error(
                            "Login succeeded, but admin access "
                            "was not confirmed."
                        )

                else:
                    st.error("No login session was returned.")

            except Exception as error:
                st.error(
                    f"Login failed: "
                    f"{type(error).__name__}: {error}"
                )


# --------------------------------------------------
# LOAD THE SONG LIBRARY
# --------------------------------------------------

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


# --------------------------------------------------
# ADMIN-ONLY SONG MANAGEMENT
# --------------------------------------------------

if st.session_state["is_admin"]:

    # ----------------------------------------------
    # ADD A NEW SONG
    # ----------------------------------------------

    st.divider()
    st.subheader("➕ Add a New Song")

    with st.form("add_song_form"):
        new_title = st.text_input("Song title")
        new_artist = st.text_input("Artist name")

        new_youtube_url = st.text_input(
            "YouTube video URL (optional)"
        )

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

    if add_song_clicked:
        if not new_title.strip() or not new_artist.strip():
            st.error("Please enter both the song title and artist.")

        elif any(
            song["title"].strip().casefold()
            == new_title.strip().casefold()
            and song["artist"].strip().casefold()
            == new_artist.strip().casefold()
            for song in songs
        ):
            st.warning(
                "This song by this artist is already in your library."
            )

        else:
            new_song = {
                "title": new_title.strip(),
                "artist": new_artist.strip(),
                "genre": new_genre,
                "mood": new_mood,
                "energy": new_energy,
                "youtube_url": new_youtube_url.strip(),
                "favorite": False
            }

            updated_songs = songs + [new_song]

            with open(songs_file, "w", encoding="utf-8") as file:
                json.dump(
                    updated_songs,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

            st.success(
                f"Added '{new_title.strip()}' successfully!"
            )
            st.rerun()


    # ----------------------------------------------
    # EDIT AN EXISTING SONG
    # ----------------------------------------------

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

            edited_youtube_url = st.text_input(
                "YouTube video URL (optional)",
                value=selected_edit_song.get("youtube_url", "")
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
                st.error(
                    "Please enter both the song title and artist."
                )

            elif any(
                i != edit_index
                and song["title"].strip().casefold()
                == edited_title.strip().casefold()
                and song["artist"].strip().casefold()
                == edited_artist.strip().casefold()
                for i, song in enumerate(songs)
            ):
                st.warning(
                    "Another song by this artist already has that title."
                )

            else:
                updated_songs = [song.copy() for song in songs]

                updated_songs[edit_index]["title"] = edited_title.strip()
                updated_songs[edit_index]["artist"] = edited_artist.strip()
                updated_songs[edit_index]["genre"] = edited_genre
                updated_songs[edit_index]["mood"] = edited_mood
                updated_songs[edit_index]["energy"] = edited_energy
                updated_songs[edit_index]["youtube_url"] = (
                    edited_youtube_url.strip()
                )

                with open(songs_file, "w", encoding="utf-8") as file:
                    json.dump(
                        updated_songs,
                        file,
                        indent=4,
                        ensure_ascii=False
                    )

                st.success("Song updated successfully! 🎉")
                st.rerun()

    else:
        st.info("Add a song before trying to edit one.")


    # ----------------------------------------------
    # DELETE A SONG
    # ----------------------------------------------

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

                updated_songs = [
                    song for i, song in enumerate(songs)
                    if i != delete_index
                ]

                with open(songs_file, "w", encoding="utf-8") as file:
                    json.dump(
                        updated_songs,
                        file,
                        indent=4,
                        ensure_ascii=False
                    )

                st.success(
                    f"'{deleted_title}' was deleted successfully! 🎉"
                )
                st.rerun()

            else:
                st.error("Please confirm before deleting the song.")

    else:
        st.info("There are no songs to delete.")

else:
    st.info(
        "🔒 Song management is available to authenticated admins only. "
        "Sign in above to add, edit, or delete songs."
    )


# --------------------------------------------------
# RECOMMENDATION SCORING
# --------------------------------------------------

def calculate_similarity(song, selected_song):
    score = 0

    if song["genre"].casefold() == selected_song["genre"].casefold():
        score += 2

    if song["mood"].casefold() == selected_song["mood"].casefold():
        score += 2

    if song["energy"] == selected_song["energy"]:
        score += 1

    return score


# --------------------------------------------------
# PUBLIC MUSIC RECOMMENDATIONS
# --------------------------------------------------

st.divider()
st.subheader("🎧 Find Your Next Favorite Song")

if not songs:
    st.info("The song library is empty. Check back later!")

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
            if index == selected_index:
                continue

            score = calculate_similarity(song, selected_song)

            if song["mood"].casefold() == user_mood.casefold():
                score += 3

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

        recommendations.sort(
            key=lambda item: (
                item["score"],
                item["song"]["mood"].casefold() == user_mood.casefold(),
                item["song"]["genre"].casefold()
                == selected_song["genre"].casefold(),
                item["song"]["energy"] == selected_song["energy"]
            ),
            reverse=True
        )

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

                    youtube_url = song.get("youtube_url", "").strip()

                    if youtube_url:
                        st.link_button(
                            "▶️ Watch on YouTube",
                            youtube_url
                        )


# --------------------------------------------------
# ADMIN-ONLY FAVORITE MANAGEMENT
# --------------------------------------------------

if st.session_state["is_admin"]:
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
                updated_songs = [song.copy() for song in songs]
                updated_songs[favorite_index]["favorite"] = False

                with open(songs_file, "w", encoding="utf-8") as file:
                    json.dump(
                        updated_songs,
                        file,
                        indent=4,
                        ensure_ascii=False
                    )

                st.success("Song removed from favorites!")
                st.rerun()

        else:
            st.write("This song is not currently a favorite.")

            if st.button("❤️ Add to Favorites"):
                updated_songs = [song.copy() for song in songs]
                updated_songs[favorite_index]["favorite"] = True

                with open(songs_file, "w", encoding="utf-8") as file:
                    json.dump(
                        updated_songs,
                        file,
                        indent=4,
                        ensure_ascii=False
                    )

                st.success("Song added to favorites!")
                st.rerun()

    else:
        st.info("Add a song before managing favorites.")


# --------------------------------------------------
# PUBLIC FAVORITE SONG DISPLAY
# --------------------------------------------------

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
        st.info("There are no favorite songs to display yet.")

    else:
        st.write(f"Favorite songs: {len(favorite_songs)}")

        for song in favorite_songs:
            with st.container(border=True):
                st.write(f"❤️ **{song['title']}**")
                st.write(f"🎤 Artist: {song['artist']}")
                st.write(f"🎼 Genre: {song['genre']}")
                st.write(f"😊 Mood: {song['mood']}")
                st.write(f"⚡ Energy: {song['energy']}/5")

                youtube_url = song.get("youtube_url", "").strip()

                if youtube_url:
                    st.link_button(
                        "▶️ Watch on YouTube",
                        youtube_url
                    )


# --------------------------------------------------
# PUBLIC SONG LIBRARY AND SEARCH
# --------------------------------------------------

st.divider()
st.subheader("🎶 Your Song Library")


def clear_search():
    st.session_state["song_search"] = ""


st.button(
    "✖ Clear search",
    on_click=clear_search
)

search_query = st.text_input(
    "🔍 Search songs",
    placeholder="Type a song title, artist, genre, or mood...",
    key="song_search"
)

st.write(f"Total songs: {len(songs)}")

filtered_songs = []
query = search_query.strip().casefold()

for song in songs:
    if (
        query in song["title"].casefold()
        or query in song["artist"].casefold()
        or query in song["genre"].casefold()
        or query in song["mood"].casefold()
    ):
        filtered_songs.append(song)

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

            youtube_url = song.get("youtube_url", "").strip()

            if youtube_url:
                st.link_button(
                    "▶️ Watch on YouTube",
                    youtube_url
                )
