
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
# HELPER FUNCTIONS
# --------------------------------------------------

def normalize_text(value):
    """Normalize text for reliable, case-insensitive comparisons."""
    return str(value or "").strip().casefold()


def get_song_style(song):
    """Support both the current style field and older genre data."""
    return song.get("style") or song.get("genre") or ""


def get_song_scale(song):
    """Return the song's assigned scale, normalized for comparison."""
    return normalize_text(song.get("scale"))


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

        new_style = st.selectbox(
            "Style",
            [
                "Waltz",
                "Slow Rock",
                "Reggae",
                "Ballaad",
                "Disco",
                "Chikchika",
                "Walloo",
                "Shawaa"
            ]
        )

        new_scale = st.selectbox(
            "Scale",
            [
                "First (C)",
                "Second (D)",
                "Fifth (G)",
                "Sixth (A)"
            ]
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
                "style": new_style,
                "scale": new_scale,
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

            style_options = [
                "Waltz",
                "Slow Rock",
                "Reggae",
                "Ballaad",
                "Disco",
                "Chikchika",
                "Walloo",
                "Shawaa"
            ]

            current_style = selected_edit_song.get(
                "style",
                selected_edit_song.get("genre", "Waltz")
            )

            if current_style not in style_options:
                style_options.append(current_style)

            edited_style = st.selectbox(
                "Style",
                style_options,
                index=style_options.index(current_style)
            )

            scale_options = [
                "Not assigned",
                "First (C)",
                "Second (D)",
                "Fifth (G)",
                "Sixth (A)"
            ]

            current_scale = selected_edit_song.get(
                "scale", "Not assigned"
            )

            edited_scale = st.selectbox(
                "Scale",
                scale_options,
                index=scale_options.index(
                    current_scale
                    if current_scale in scale_options
                    else "Not assigned"
                )
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
                updated_songs[edit_index]["style"] = edited_style
                updated_songs[edit_index]["scale"] = (
                    edited_scale
                    if edited_scale != "Not assigned"
                    else ""
                )
                updated_songs[edit_index].pop("genre", None)

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

    song_style = normalize_text(get_song_style(song))
    selected_style = normalize_text(get_song_style(selected_song))

    if song_style and song_style == selected_style:
        score += 2

    song_scale = get_song_scale(song)
    selected_scale = get_song_scale(selected_song)

    if song_scale and song_scale == selected_scale:
        score += 5

    if normalize_text(song.get("mood")) == normalize_text(
        selected_song.get("mood")
    ):
        score += 2

    if song.get("energy") == selected_song.get("energy"):
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

    selected_style = get_song_style(selected_song)
    selected_scale_display = selected_song.get("scale") or "Not assigned"

    st.write(
        f"**Style:** {selected_style or 'Unknown'} | "
        f"**Scale:** {selected_scale_display} | "
        f"**Mood:** {selected_song['mood']} | "
        f"**Energy:** {selected_song['energy']}/5"
    )

    if st.button("🎵 Recommend Songs", type="primary"):

        recommendations = []

        selected_scale = get_song_scale(selected_song)
        selected_style_key = normalize_text(get_song_style(selected_song))

        # Consider every other song in the library.
        for index, song in enumerate(songs):

            # Never recommend the exact song the user selected.
            if index == selected_index:
                continue

            # Calculate similarity using style, scale, mood, and energy.
            score = calculate_similarity(song, selected_song)

            # Give extra points when the song matches the user's mood.
            matches_user_mood = (
                normalize_text(song.get("mood"))
                == normalize_text(user_mood)
            )

            if matches_user_mood:
                score += 3

            song_style = normalize_text(get_song_style(song))
            song_scale = get_song_scale(song)

            same_style = bool(
                song_style and song_style == selected_style_key
            )

            same_scale = bool(
                selected_scale and song_scale == selected_scale
            )

            same_mood = (
                normalize_text(song.get("mood"))
                == normalize_text(selected_song.get("mood"))
            )

            same_energy = (
                song.get("energy") == selected_song.get("energy")
            )

            reasons = []

            if same_style:
                reasons.append("same style (+2)")

            if same_scale:
                reasons.append("same scale (+5)")

            if same_mood:
                reasons.append("same mood (+2)")

            if same_energy:
                reasons.append("same energy (+1)")

            if matches_user_mood:
                reasons.append("matches your chosen mood (+3)")

            recommendations.append({
                "score": score,
                "song": song,
                "reasons": reasons,
                "same_scale": same_scale,
                "matches_user_mood": matches_user_mood,
                "same_style": same_style,
                "same_energy": same_energy
            })

        # Show same-scale songs first.
        # Within each group, higher-scoring songs come first.
        recommendations.sort(
            key=lambda item: (
                item["same_scale"],
                item["score"],
                item["matches_user_mood"],
                item["same_style"],
                item["same_energy"]
            ),
            reverse=True
        )

        # IMPORTANT:
        # Include ALL same-scale songs, even if their score is zero.
        # Also keep other songs that have a positive similarity score.
        top_matches = [
            item for item in recommendations
            if item["same_scale"] or item["score"] > 0
        ]

        st.subheader("✨ Your Recommendations")

        same_scale_matches = [
            item for item in top_matches
            if item["same_scale"]
        ]

        if selected_scale:
            st.caption(
                f"🎼 Found {len(same_scale_matches)} other song(s) "
                f"with scale {selected_scale_display}."
            )

        if not top_matches:
            st.info("Sorry, no similar songs found.")

        else:
            if same_scale_matches:
                st.markdown("### 🎼 Songs with the Same Scale")

                for item in same_scale_matches:
                    song = item["song"]

                    with st.container(border=True):
                        st.subheader(f"🎵 {song['title']}")
                        st.write(f"🎤 **Artist:** {song['artist']}")

                        song_style = get_song_style(song) or "Unknown"
                        song_scale = song.get("scale") or "Not assigned"

                        st.write(
                            f"🎼 **Style:** {song_style} | "
                            f"**Scale:** {song_scale}"
                        )
                        st.write(f"😊 **Mood:** {song['mood']}")
                        st.write(f"⚡ **Energy:** {song['energy']}/5")
                        st.write(
                            f"🏆 **Similarity score:** {item['score']}"
                        )

                        st.write(
                            "🎼 **Why this song?** "
                            "It uses the same scale as your selected song."
                        )

                        # Include any additional reasons.
                        other_reasons = [
                            reason for reason in item["reasons"]
                            if reason != "same scale (+5)"
                        ]

                        if other_reasons:
                            st.write(
                                "**Also matches:** "
                                + ", ".join(other_reasons)
                            )

                        youtube_url = (
                            song.get("youtube_url") or ""
                        ).strip()

                        if youtube_url:
                            st.link_button(
                                "▶️ Watch on YouTube",
                                youtube_url
                            )

            # Other recommendations are displayed separately,
            # without repeating the same-scale songs.
            other_matches = [
                item for item in top_matches
                if not item["same_scale"]
            ]

            if other_matches:
                st.markdown("### ✨ Other Similar Songs")

                for item in other_matches:
                    song = item["song"]

                    with st.container(border=True):
                        st.subheader(f"🎵 {song['title']}")
                        st.write(f"🎤 **Artist:** {song['artist']}")

                        song_style = get_song_style(song) or "Unknown"
                        song_scale = song.get("scale") or "Not assigned"

                        st.write(
                            f"🎼 **Style:** {song_style} | "
                            f"**Scale:** {song_scale}"
                        )
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

                        youtube_url = (
                            song.get("youtube_url") or ""
                        ).strip()

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

                song_style = get_song_style(song) or "Unknown"
                song_scale = song.get("scale") or "Not assigned"

                st.write(
                    f"🎼 Style: {song_style} | Scale: {song_scale}"
                )
                st.write(f"😊 Mood: {song['mood']}")
                st.write(f"⚡ Energy: {song['energy']}/5")

                youtube_url = (
                    song.get("youtube_url") or ""
                ).strip()

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
    placeholder="Type a song title, artist, style, mood, or scale...",
    key="song_search"
)

st.write(f"Total songs: {len(songs)}")

filtered_songs = []
query = search_query.strip().casefold()

for song in songs:
    if (
        query in song["title"].casefold()
        or query in song["artist"].casefold()
        or query in normalize_text(get_song_style(song))
        or query in normalize_text(song.get("mood"))
        or query in normalize_text(song.get("scale"))
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

            song_style = get_song_style(song) or "Unknown"
            song_scale = song.get("scale") or "Not assigned"

            st.write(
                f"🎼 Style: {song_style} | Scale: {song_scale}"
            )
            st.write(f"😊 Mood: {song['mood']}")
            st.write(f"⚡ Energy: {song['energy']}/5")

            if song.get("favorite", False):
                st.write("❤️ Favorite")

            youtube_url = (
                song.get("youtube_url") or ""
            ).strip()

            if youtube_url:
                st.link_button(
                    "▶️ Watch on YouTube",
                    youtube_url
                )
