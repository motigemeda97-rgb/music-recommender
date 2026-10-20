
import json
from pathlib import Path

import streamlit as st
from supabase import create_client


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Afaan Oromo's Music Recommender",
    page_icon="🎵",
    layout="wide",
)


# ==================================================
# HELPER FUNCTIONS
# ==================================================

def normalize_text(value):
    """Normalize text for case-insensitive comparisons."""
    return str(value or "").strip().casefold()


def get_song_style(song):
    """Support current style data and older genre data."""
    return song.get("style") or song.get("genre") or ""


def get_song_scale(song):
    """Normalize a song's musical scale."""
    return normalize_text(song.get("scale"))


def get_supabase_client():
    """Create a Supabase client using the app's configured credentials."""
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"],
    )


def verify_user_token(access_token):
    """Ask Supabase Auth to verify the token and return trusted identity."""
    if not access_token:
        return None

    try:
        client = get_supabase_client()
        response = client.auth.get_user(access_token)

        if not response or not response.user:
            return None

        return {
            "user_id": str(response.user.id),
            "email": response.user.email or "",
        }

    except Exception:
        return None


def verify_admin_token(access_token):
    """Check the verified token's admin role through the database."""
    if not access_token:
        return False

    try:
        client = get_supabase_client()

        # The RPC must run as the authenticated user.
        client.postgrest.auth(access_token)
        result = client.rpc("is_admin").execute()

        return result.data is True

    except Exception:
        return False


def load_songs_from_supabase(client):
    """Load songs from the permanent Supabase database."""
    response = (
        client.table("songs")
        .select("*")
        .order("id")
        .execute()
    )
    return response.data or []


def insert_song_into_supabase(client, song):
    """Insert a song into Supabase."""
    database_song = {
        "title": song["title"],
        "artist": song["artist"],
        "genre": song.get("style") or song.get("genre") or "",
        "scale": song.get("scale") or None,
        "mood": song.get("mood") or "Calm",
        "energy": int(song.get("energy", 3)),
        "youtube_url": song.get("youtube_url") or None,
        "favorite": bool(song.get("favorite", False)),
        "approval_status": song.get("approval_status", "approved"),
    }

    return client.table("songs").insert(database_song).execute()


def update_song_in_supabase(client, song_id, changes):
    """Update an existing song by its database ID."""
    return (
        client.table("songs")
        .update(changes)
        .eq("id", song_id)
        .execute()
    )


def delete_song_from_supabase(client, song_id):
    """Delete a song by its database ID."""
    return (
        client.table("songs")
        .delete()
        .eq("id", song_id)
        .execute()
    )


def song_label(song):
    return f"{song.get('title', 'Untitled')} — {song.get('artist', 'Unknown artist')}"


# ==================================================
# SESSION STATE
# ==================================================

for key, default in {
    "user_access_token": "",
    "user_id": "",
    "user_email": "",
    "is_admin": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ==================================================
# PAGE DESIGN
# ==================================================

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


# ==================================================
# SHARED USER AND ADMIN AUTHENTICATION
# ==================================================

st.divider()
st.subheader("🔐 Your Account")

st.write(
    "Sign in or create an account."
)

project_folder = Path(__file__).parent

bundle_path = (
    project_folder
    / "auth-frontend"
    / "build"
    / "auth-component.js"
)

if not bundle_path.exists():
    st.error(
        "The browser authentication component was not found. "
        "Build auth-frontend first, then restart the app."
    )
    st.stop()

try:
    js_code = bundle_path.read_text(encoding="utf-8")
    auth_component = st.components.v2.component(
        name="afaan_oromoo_browser_auth",
        js=js_code,
    )

    auth_result = auth_component(
        data={
            "supabase_url": st.secrets["SUPABASE_URL"],
            "supabase_anon_key": st.secrets["SUPABASE_KEY"],
        },
        default={
            "access_token": "",
            "user_id": "",
            "email": "",
            "auth_event": "",
        },
        on_access_token_change=lambda: None,
        on_user_id_change=lambda: None,
        on_email_change=lambda: None,
        on_auth_event_change=lambda: None,
        key="afaan_oromoo_browser_auth_instance",
    )

except Exception as error:
    st.error(
        "The authentication interface could not be loaded. "
        f"Error type: {type(error).__name__}"
    )
    st.stop()


# Only trust the token after verifying it with Supabase Auth.
browser_token = (
    getattr(auth_result, "access_token", "") or ""
).strip()

verified_identity = verify_user_token(browser_token)

if verified_identity:
    verified_user_id = verified_identity["user_id"]
    verified_email = verified_identity["email"]

    # Never trust the user ID or email supplied by the browser.
    st.session_state["user_access_token"] = browser_token
    st.session_state["user_id"] = verified_user_id
    st.session_state["user_email"] = verified_email

    # Admin status is independently checked in the database.
    st.session_state["is_admin"] = verify_admin_token(browser_token)

else:
    # Clear identity and permissions immediately when signed out
    # or when Supabase rejects the supplied token.
    st.session_state["user_access_token"] = ""
    st.session_state["user_id"] = ""
    st.session_state["user_email"] = ""
    st.session_state["is_admin"] = False


user_access_token = st.session_state["user_access_token"]
user_id = st.session_state["user_id"]
user_email = st.session_state["user_email"]
is_admin = st.session_state["is_admin"]


# Create the database client used for this user's favorites.
user_client = get_supabase_client()

if user_access_token:
    user_client.postgrest.auth(user_access_token)

    if is_admin:
        st.success(f"✅ Administrator verified: {user_email}")
        st.info(
            "You have administrator permissions. "
            "Your song-management controls are available below."
        )
    else:
        st.success(f"✅ Signed in as: {user_email}")
        st.caption(
            "Your account has regular-user permissions. "
            "You can manage your own personal favorites."
        )



# ==================================================
# LOAD THE SONG LIBRARY FROM SUPABASE
# ==================================================

try:
    songs = load_songs_from_supabase(user_client)

    for song in songs:
        song["style"] = song.get("genre") or ""
        song["scale"] = song.get("scale") or ""

except Exception as error:
    st.error(
        "Could not load the song library from Supabase. "
        f"Error type: {type(error).__name__}"
    )
    st.stop()



# ==================================================
# ADMIN-ONLY SONG MANAGEMENT
# ==================================================

if is_admin:

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
                "Shawaa",
            ],
        )

        new_scale = st.selectbox(
            "Scale",
            [
                "First (C)",
                "Second (D)",
                "Fifth (G)",
                "Sixth (A)",
            ],
        )

        new_mood = st.selectbox(
            "Mood",
            ["Happy", "Calm", "Energetic", "Sad"],
        )

        new_energy = st.slider(
            "Energy level",
            min_value=1,
            max_value=5,
            value=3,
        )

        add_song_clicked = st.form_submit_button("➕ Add Song")

    if add_song_clicked:
        if not new_title.strip() or not new_artist.strip():
            st.error("Please enter both the song title and artist.")

        elif any(
            normalize_text(song.get("title"))
            == normalize_text(new_title)
            and normalize_text(song.get("artist"))
            == normalize_text(new_artist)
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
                "favorite": False,
            }

            try:
                insert_song_into_supabase(user_client, new_song)
                st.success(f"Added '{new_title.strip()}' successfully!")
                st.rerun()
            except Exception as error:
                st.error(
                    "Could not save the song to Supabase. "
                    f"Error type: {type(error).__name__}"
                )

    # ----------------------------------------------
    # EDIT AN EXISTING SONG
    # ----------------------------------------------

    st.divider()
    st.subheader("✏️ Edit an Existing Song")

    if songs:
        edit_index = st.selectbox(
            "Choose a song to edit:",
            range(len(songs)),
            format_func=lambda i: song_label(songs[i]),
            key="edit_song_index",
        )

        selected_edit_song = songs[edit_index]

        with st.form("edit_song_form"):
            edited_title = st.text_input(
                "Song title",
                value=selected_edit_song.get("title", ""),
            )

            edited_artist = st.text_input(
                "Artist name",
                value=selected_edit_song.get("artist", ""),
            )

            edited_youtube_url = st.text_input(
                "YouTube video URL (optional)",
                value=selected_edit_song.get("youtube_url", ""),
            )

            style_options = [
                "Waltz",
                "Slow Rock",
                "Reggae",
                "Ballaad",
                "Disco",
                "Chikchika",
                "Walloo",
                "Shawaa",
            ]

            current_style = get_song_style(selected_edit_song) or "Waltz"

            if current_style not in style_options:
                style_options.append(current_style)

            edited_style = st.selectbox(
                "Style",
                style_options,
                index=style_options.index(current_style),
            )

            scale_options = [
                "Not assigned",
                "First (C)",
                "Second (D)",
                "Fifth (G)",
                "Sixth (A)",
            ]

            current_scale = (
                selected_edit_song.get("scale") or "Not assigned"
            )

            if current_scale not in scale_options:
                scale_options.append(current_scale)

            edited_scale = st.selectbox(
                "Scale",
                scale_options,
                index=scale_options.index(current_scale),
            )

            mood_options = ["Happy", "Calm", "Energetic", "Sad"]
            current_mood = selected_edit_song.get("mood", "Happy")

            if current_mood not in mood_options:
                mood_options.append(current_mood)

            edited_mood = st.selectbox(
                "Mood",
                mood_options,
                index=mood_options.index(current_mood),
            )

            current_energy = selected_edit_song.get("energy", 3)
            current_energy = max(1, min(5, int(current_energy)))

            edited_energy = st.slider(
                "Energy level",
                min_value=1,
                max_value=5,
                value=current_energy,
            )

            edit_clicked = st.form_submit_button("💾 Save Changes")

        if edit_clicked:
            if not edited_title.strip() or not edited_artist.strip():
                st.error("Please enter both the song title and artist.")

            elif any(
                i != edit_index
                and normalize_text(song.get("title"))
                == normalize_text(edited_title)
                and normalize_text(song.get("artist"))
                == normalize_text(edited_artist)
                for i, song in enumerate(songs)
            ):
                st.warning(
                    "Another song by this artist already has that title."
                )

            else:
                changes = {
                    "title": edited_title.strip(),
                    "artist": edited_artist.strip(),
                    "genre": edited_style,
                    "scale": (
                        None if edited_scale == "Not assigned"
                        else edited_scale
                    ),
                    "mood": edited_mood,
                    "energy": edited_energy,
                    "youtube_url": edited_youtube_url.strip() or None,
                }

                try:
                    update_song_in_supabase(
                        user_client,
                        selected_edit_song["id"],
                        changes,
                    )
                    st.success("Song updated successfully! 🎉")
                    st.rerun()

                except Exception as error:
                    st.error(
                        "Could not update the song in Supabase. "
                        f"Error type: {type(error).__name__}"
                    )


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
            format_func=lambda i: song_label(songs[i]),
            key="delete_song_index",
        )

        song_to_delete = songs[delete_index]

        st.warning(f"You selected: {song_label(song_to_delete)}")

        confirm_delete = st.checkbox(
            "Yes, I want to delete this song.",
            key="confirm_delete_song",
        )

        if st.button("🗑️ Delete Song"):
            if confirm_delete:
                deleted_title = songs[delete_index].get("title", "Song")
                try:
                    delete_song_from_supabase(
                        user_client,
                        song_to_delete["id"],
                    )
                    st.success(
                        f"'{deleted_title}' was deleted successfully!"
                    )
                    st.rerun()

                except Exception as error:
                    st.error(
                        "Could not delete the song from Supabase. "
                        f"Error type: {type(error).__name__}"
                    )


            else:
                st.error("Please confirm before deleting the song.")

    else:
        st.info("There are no songs to delete.")

else:
    st.info(
        "🔒 Song management is available to verified administrators only."
    )


# ==================================================
# RECOMMENDATION SCORING
# ==================================================

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


# ==================================================
# PUBLIC MUSIC RECOMMENDATIONS
# ==================================================

st.divider()
st.subheader("🎧 Find Your Next Favorite Song")

if not songs:
    st.info("The song library is empty. Check back later!")

else:
    user_mood = st.selectbox(
        "How are you feeling today?",
        ["Happy", "Calm", "Energetic", "Sad"],
    )

    selected_index = st.selectbox(
        "Choose a song you already like:",
        range(len(songs)),
        format_func=lambda i: song_label(songs[i]),
    )

    selected_song = songs[selected_index]

    st.write(f"**Selected song:** {selected_song.get('title', '')}")

    selected_style = get_song_style(selected_song)
    selected_scale_display = selected_song.get("scale") or "Not assigned"

    st.write(
        f"**Style:** {selected_style or 'Unknown'} | "
        f"**Scale:** {selected_scale_display} | "
        f"**Mood:** {selected_song.get('mood', 'Unknown')} | "
        f"**Energy:** {selected_song.get('energy', '?')}/5"
    )

    if st.button("🎵 Recommend Songs", type="primary"):
        recommendations = []

        selected_scale = get_song_scale(selected_song)
        selected_style_key = normalize_text(get_song_style(selected_song))

        for index, song in enumerate(songs):
            if index == selected_index:
                continue

            score = calculate_similarity(song, selected_song)

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
                "same_energy": same_energy,
            })

        recommendations.sort(
            key=lambda item: (
                item["same_scale"],
                item["score"],
                item["matches_user_mood"],
                item["same_style"],
                item["same_energy"],
            ),
            reverse=True,
        )

        # Keep every same-scale match and every other positive match.
        top_matches = [
            item for item in recommendations
            if item["same_scale"] or item["score"] > 0
        ]

        st.subheader("✨ Your Recommendations")

        # Split recommendations into non-overlapping groups so each song
        # appears in only one section.
        same_scale_and_style = [
            item for item in top_matches
            if item["same_scale"] and item["same_style"]
        ]
        same_scale_only = [
            item for item in top_matches
            if item["same_scale"] and not item["same_style"]
        ]
        same_style_only = [
            item for item in top_matches
            if item["same_style"] and not item["same_scale"]
        ]
        other_matches = [
            item for item in top_matches
            if not item["same_scale"] and not item["same_style"]
        ]

        def show_recommendation_table(heading, matches):
            st.markdown(f"### {heading}")
            rows = []
            for item in matches:
                song = item["song"]
                rows.append({
                    "Song": song.get("title", "Untitled"),
                    "Artist": song.get("artist", "Unknown"),
                    "Scale": get_song_scale(song) or "Not assigned",
                    "Style": get_song_style(song) or "Unknown",
                    "Score": item["score"],
                    "Why it matches": ", ".join(item["reasons"]),
                    "YouTube": (song.get("youtube_url") or "").strip(),
                })

            st.dataframe(
                rows,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "YouTube": st.column_config.LinkColumn(
                        "YouTube",
                        display_text="▶️ Watch",
                    )
                },
            )

        st.markdown(
            "Compare recommendations in separate tables. Each song appears "
            "in only one group, with scale and style matches shown first."
        )

        if same_scale_and_style:
            show_recommendation_table(
                "🎼 Same Scale + Same Style",
                same_scale_and_style,
            )
        else:
            st.info("No other songs match both the selected scale and style.")

        if selected_scale:
            st.caption(
                f"🎹 Found {len(same_scale_and_style) + len(same_scale_only)} "
                f"other song(s) with scale {selected_scale_display}."
            )

        if same_scale_only:
            show_recommendation_table(
                "🎹 Same Scale, Different Style",
                same_scale_only,
            )
        elif selected_scale:
            st.caption("No additional songs match the scale with a different style.")

        if same_style_only:
            show_recommendation_table(
                "🎶 Same Style, Different Scale",
                same_style_only,
            )
        else:
            st.caption("No additional songs match the style with a different scale.")

        if other_matches:
            st.markdown("### ✨ Other Similar Songs")
            for item in other_matches:
                song = item["song"]

                with st.container(border=True):
                    st.subheader(f"🎵 {song.get('title', 'Untitled')}")
                    st.write(f"🎤 **Artist:** {song.get('artist', 'Unknown')}")
                    st.write(
                        f"🎼 **Style:** {get_song_style(song) or 'Unknown'} | "
                        f"**Scale:** {get_song_scale(song) or 'Not assigned'}"
                    )
                    st.write(f"😊 **Mood:** {song.get('mood', 'Unknown')}")
                    st.write(f"⚡ **Energy:** {song.get('energy', '?')}/5")
                    st.write(f"🏆 **Similarity score:** {item['score']}")

                    if item["reasons"]:
                        st.write("**Why this song?** " + ", ".join(item["reasons"]))

                    youtube_url = (song.get("youtube_url") or "").strip()
                    if youtube_url:
                        st.link_button("▶️ Watch on YouTube", youtube_url)

        if not top_matches:
            st.info("Sorry, no similar songs found.")

# ==================================================
# ADMIN-ONLY GLOBAL FAVORITE MANAGEMENT
# ==================================================

if is_admin:
    st.divider()
    st.subheader("❤️ Manage Favorite Songs")

    if songs:
        favorite_index = st.selectbox(
            "Choose a song:",
            range(len(songs)),
            format_func=lambda i: song_label(songs[i]),
            key="favorite_song_index",
        )

        selected_favorite_song = songs[favorite_index]
        if selected_favorite_song.get("favorite", False):
            st.write("❤️ This song is currently marked as a favorite.")
            if st.button("💔 Remove from Favorites"):
                song_to_update = songs[favorite_index]

                try:
                    update_song_in_supabase(
                        user_client,
                        song_to_update["id"],
                        {"favorite": False},
                    )
                    st.success("Song removed from favorites!")
                    st.rerun()

                except Exception as error:
                    st.error(
                        "Could not update favorites in Supabase. "
                        f"Error type: {type(error).__name__}"
                    )
        else:
            st.write("This song is not currently marked as a favorite.")
            if st.button("❤️ Add to Favorites"):
                song_to_update = songs[favorite_index]

                try:
                    update_song_in_supabase(
                        user_client,
                        song_to_update["id"],
                        {"favorite": True},
                    )
                    st.success("Song added to favorites!")
                    st.rerun()

                except Exception as error:
                    st.error(
                        "Could not update favorites in Supabase. "
                        f"Error type: {type(error).__name__}"
                    )
    else:
        st.info("Add a song before managing favorites.")
# ==================================================
# PUBLIC DISPLAY OF GLOBALLY MARKED FAVORITES
# ==================================================
st.divider()
st.subheader("💖 Favorite Songs")

show_favorites_only = st.checkbox(
    "Show only songs marked as favorites",
    key="show_favorites_only",
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
                st.write(f"❤️ **{song.get('title', 'Untitled')}**")
                st.write(f"🎤 Artist: {song.get('artist', 'Unknown')}")

                st.write(
                    f"🎼 Style: {get_song_style(song) or 'Unknown'} | "
                    f"Scale: {song.get('scale') or 'Not assigned'}"
                )
                st.write(f"😊 Mood: {song.get('mood', 'Unknown')}")
                st.write(f"⚡ Energy: {song.get('energy', '?')}/5")

                youtube_url = (
                    song.get("youtube_url") or ""
                ).strip()

                if youtube_url:
                    st.link_button("▶️ Watch on YouTube", youtube_url)


# ==================================================
# PERSONAL FAVORITES SAVED IN SUPABASE
# ==================================================

st.divider()
st.subheader("❤️ My Personal Favorites")

if user_access_token and user_id:

    try:
        # The client uses this signed-in user's access token.
        user_client.postgrest.auth(user_access_token)

        response = (
            user_client.table("user_favorites")
            .select("song_title, song_artist")
            .eq("user_id", user_id)
            .execute()
        )

        personal_favorites = response.data or []

        favorite_keys = {
            (item["song_title"], item["song_artist"])
            for item in personal_favorites
        }

        # ------------------------------------------
        # ADD A PERSONAL FAVORITE
        # ------------------------------------------

        available_songs = [
            song for song in songs
            if (
                song.get("title", ""),
                song.get("artist", ""),
            ) not in favorite_keys
        ]

        st.write("### ➕ Add a Personal Favorite")

        if available_songs:
            selected_personal_song = st.selectbox(
                "Choose a song:",
                available_songs,
                format_func=song_label,
                key="personal_favorite_song",
            )

            if st.button(
                "❤️ Add to My Favorites",
                key="add_personal_favorite",
            ):
                user_client.table("user_favorites").insert({
                    "user_id": user_id,
                    "song_title": selected_personal_song["title"],
                    "song_artist": selected_personal_song["artist"],
                }).execute()

                st.success("Song added to your personal favorites!")
                st.rerun()

        else:
            st.info(
                "All songs in the library are already your favorites!"
            )

        # ------------------------------------------
        # DISPLAY AND REMOVE PERSONAL FAVORITES
        # ------------------------------------------

        st.write("### 🎵 My Saved Songs")

        if not personal_favorites:
            st.info("You haven't saved any personal favorites yet.")

        else:
            st.write(
                f"You have {len(personal_favorites)} personal favorite(s)."
            )

            for index, favorite in enumerate(personal_favorites):
                title = favorite["song_title"]
                artist = favorite["song_artist"]

                with st.container(border=True):
                    st.write(f"❤️ **{title}**")
                    st.write(f"🎤 Artist: {artist}")

                    matching_song = next(
                        (
                            song for song in songs
                            if song.get("title") == title
                            and song.get("artist") == artist
                        ),
                        None,
                    )

                    if matching_song:
                        st.write(
                            f"🎼 Style: {get_song_style(matching_song) or 'Unknown'} | "
                            f"Scale: {matching_song.get('scale') or 'Not assigned'}"
                        )
                        st.write(
                            f"😊 Mood: {matching_song.get('mood', 'Unknown')}"
                        )

                        youtube_url = (
                            matching_song.get("youtube_url") or ""
                        ).strip()

                        if youtube_url:
                            st.link_button(
                                "▶️ Watch on YouTube",
                                youtube_url,
                                key=f"personal_youtube_{index}",
                            )

                    if st.button(
                        "💔 Remove from My Favorites",
                        key=f"remove_personal_favorite_{index}",
                    ):
                        (
                            user_client.table("user_favorites")
                            .delete()
                            .eq("user_id", user_id)
                            .eq("song_title", title)
                            .eq("song_artist", artist)
                            .execute()
                        )

                        st.success("Removed from your personal favorites.")
                        st.rerun()

    except Exception as error:
        # Avoid displaying database or authentication internals.
        st.error(
            "Could not load or update your personal favorites. "
            f"Error type: {type(error).__name__}"
        )

else:
    st.info(
        "Sign in using the account panel above to save and manage "
        "your own personal favorite songs."
    )


# ==================================================
# PUBLIC SONG LIBRARY AND SEARCH
# ==================================================

st.divider()
st.subheader("🎶 Your Song Library")


def clear_search():
    st.session_state["song_search"] = ""
    st.session_state["song_library_page"] = 1


def reset_song_library_page():
    st.session_state["song_library_page"] = 1


if "song_library_page" not in st.session_state:
    st.session_state["song_library_page"] = 1

st.button("✖ Clear search", on_click=clear_search)

search_query = st.text_input(
    "🔍 Search songs",
    placeholder="Type a song title, artist, style, mood, or scale...",
    key="song_search",
    on_change=reset_song_library_page,
)

st.write(f"Total songs: {len(songs)}")

query = normalize_text(search_query)
filtered_songs = []

for song in songs:
    searchable_values = [
        song.get("title", ""),
        song.get("artist", ""),
        get_song_style(song),
        song.get("mood", ""),
        song.get("scale", ""),
    ]

    if any(query in normalize_text(value) for value in searchable_values):
        filtered_songs.append(song)

if not filtered_songs:
    st.info("No songs found. Try another search.")

else:
    st.write(f"Songs found: {len(filtered_songs)}")

    songs_per_page = 10
    total_pages = max(
        1,
        (len(filtered_songs) + songs_per_page - 1) // songs_per_page,
    )

    current_page = min(
        max(1, st.session_state["song_library_page"]),
        total_pages,
    )
    st.session_state["song_library_page"] = current_page

    start_index = (current_page - 1) * songs_per_page
    end_index = start_index + songs_per_page
    page_songs = filtered_songs[start_index:end_index]

    st.caption(
        f"Showing songs {start_index + 1}–{min(end_index, len(filtered_songs))} "
        f"of {len(filtered_songs)} · Page {current_page} of {total_pages}"
    )

    for song in page_songs:
        with st.container(border=True):
            st.write(f"**{song.get('title', 'Untitled')}**")
            st.write(f"🎤 Artist: {song.get('artist', 'Unknown')}")

            st.write(
                f"🎼 Style: {get_song_style(song) or 'Unknown'} | "
                f"Scale: {song.get('scale') or 'Not assigned'}"
            )
            st.write(f"😊 Mood: {song.get('mood', 'Unknown')}")
            st.write(f"⚡ Energy: {song.get('energy', '?')}/5")

            if song.get("favorite", False):
                st.write("❤️ Favorite")

            youtube_url = (
                song.get("youtube_url") or ""
            ).strip()

            if youtube_url:
                st.link_button("▶️ Watch on YouTube", youtube_url)

    previous_col, page_col, next_col = st.columns([1, 2, 1])

    with previous_col:
        if st.button(
            "⬅️ Previous",
            disabled=current_page <= 1,
            key="song_library_previous",
        ):
            st.session_state["song_library_page"] = current_page - 1
            st.rerun()

    with page_col:
        st.markdown(
            f"<div style='text-align:center; padding-top:0.5rem;'>"
            f"Page <strong>{current_page}</strong> of <strong>{total_pages}</strong>"
            f"</div>",
            unsafe_allow_html=True,
        )

    with next_col:
        if st.button(
            "Next ➡️",
            disabled=current_page >= total_pages,
            key="song_library_next",
        ):
            st.session_state["song_library_page"] = current_page + 1
            st.rerun()
