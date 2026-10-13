
import json


songs = [
    {
        "title": "Hiriyaa Gadhee miti",
        "artist": "Yaadasaa Shirrii",
        "genre": "Waltz",
        "mood": "Calm",
        "energy": 3
    },
    {
        "title": "Goota Mararaa",
        "artist": "Yaadasaa Shirrii",
        "genre": "Shawaa",
        "mood": "Energetic",
        "energy": 5
    },
    {
        "title": "Dirmammaa'ee du'a na baraare",
        "artist": "Dawit Girma",
        "genre": "Shawaa",
        "mood": "Energetic",
        "energy": 5
    },
    {
        "title": "Jalala nama hundaa",
        "artist": "Eeliyaas Gabulaa",
        "genre": "Waltz",
        "mood": "Happy",
        "energy": 3
    },
    {
        "title": "wanti ati anaaf Goote",
        "artist": "Tamaam Faares",
        "genre": "Waltz",
        "mood": "Sad",
        "energy": 2
    },
]


def calculate_similarity(song, selected_song):
    score = 0

    # Compare genres
    if song["genre"] == selected_song["genre"]:
        score += 2

    # Compare moods
    if song["mood"] == selected_song["mood"]:
        score += 2

    # Compare energy levels
    if song["energy"] == selected_song["energy"]:
        score += 1

    return score


def add_song(songs):
    print("\n🎵 Add a New Song")

    title = input("Enter the song title: ").strip()
    artist = input("Enter the artist's name: ").strip()
    genre = input("Enter the genre: ").strip()
    mood = input(
        "Enter the mood (Happy, Calm, Energetic, Sad): "
    ).strip().capitalize()

    if not title or not artist or not genre:
        print("Title, artist, and genre cannot be empty.")
        return

    valid_moods = ["Happy", "Calm", "Energetic", "Sad"]

    if mood not in valid_moods:
        print("Please enter Happy, Calm, Energetic, or Sad.")
        return

    while True:
        energy_input = input(
            "Enter energy level (1-5): "
        ).strip()

        if energy_input.isdigit() and 1 <= int(energy_input) <= 5:
            energy = int(energy_input)
            break
        else:
            print("Please enter a whole number from 1 to 5.")

    new_song = {
        "title": title,
        "artist": artist,
        "genre": genre,
        "mood": mood,
        "energy": energy
    }

    # Check whether this song already exists
    for song in songs:
        if (
            song["title"].lower() == new_song["title"].lower()
            and song["artist"].lower() == new_song["artist"].lower()
        ):
            print(f"\n⚠️ '{title}' by {artist} already exists!")
            return

    songs.append(new_song)
    save_songs(songs)

    print(f"\n✅ '{title}' by {artist} was added!")


def view_songs(songs):
    print("\n🎵 YOUR SONG LIBRARY")
    print("=" * 40)

    if not songs:
        print("Your song library is empty.")
        return

    for index, song in enumerate(songs, start=1):
        print(f"\n{index}. {song['title']}")
        print(f"   Artist: {song['artist']}")
        print(f"   Genre: {song['genre']}")
        print(f"   Mood: {song['mood']}")
        print(f"   Energy: {song['energy']}/5")

    print("\n" + "=" * 40)
    print(f"Total songs: {len(songs)}")


def edit_song(songs):
    print("\n✏️ EDIT A SONG")
    print("=" * 40)

    if not songs:
        print("Your song library is empty.")
        return

    # Display all songs
    for index, song in enumerate(songs, start=1):
        print(f"{index}. {song['title']}")

    # Choose a song
    while True:
        choice = input(
            "\nEnter the number of the song to edit: "
        ).strip()

        if choice.isdigit():
            choice = int(choice)

            if 1 <= choice <= len(songs):
                break

        print("Invalid choice. Please enter a valid song number.")

    song = songs[choice - 1]

    print(f"\nEditing: {song['title']}")

    # Choose which field to edit
    fields = ["title", "artist", "genre", "mood", "energy"]

    print("\nWhat would you like to edit?")

    for index, field_name in enumerate(fields, start=1):
        print(f"{index}. {field_name.title()}")

    while True:
        field_choice = input(
            "\nEnter the number of the field to edit: "
        ).strip()

        if field_choice.isdigit():
            field_choice = int(field_choice)

            if 1 <= field_choice <= len(fields):
                break

        print("Invalid choice. Please enter a number from 1 to 5.")

    field_name = fields[field_choice - 1]

    # Ask for the new value
    new_value = input(
        f"Enter the new {field_name}: "
    ).strip()

    if not new_value:
        print("Value cannot be empty.")
        return

    # Validate the new value before updating the song
    if field_name == "energy":
        if new_value.isdigit() and 1 <= int(new_value) <= 5:
            new_value = int(new_value)
        else:
            print("Invalid energy. Enter a number from 1 to 5.")
            return

    elif field_name == "mood":
        valid_moods = ["Happy", "Calm", "Energetic", "Sad"]

        matching_mood = next(
            (
                mood for mood in valid_moods
                if mood.lower() == new_value.lower()
            ),
            None
        )

        if matching_mood is None:
            print("Please enter Happy, Calm, Energetic, or Sad.")
            return

        new_value = matching_mood

    # Update the song only after validation
    song[field_name] = new_value

    # Save the updated song library
    save_songs(songs)

    print(f"{field_name.title()} updated successfully! ✅")

    # Display updated song details
    print("\nUpdated song details:")
    print(f"Title: {song['title']}")
    print(f"Artist: {song['artist']}")
    print(f"Genre: {song['genre']}")
    print(f"Mood: {song['mood']}")
    print(f"Energy: {song['energy']}/5")


def search_song(songs):
    print("\n🔎 SEARCH FOR A SONG")

    search_text = input(
        "Enter a song title or artist name: "
    ).strip().lower()

    if not search_text:
        print("Please enter a song title or artist name.")
        return

    found_songs = []

    for song in songs:
        if (
            search_text in song["title"].lower()
            or search_text in song["artist"].lower()
        ):
            found_songs.append(song)

    if found_songs:
        print("\n🎵 Search results:")

        for song in found_songs:
            print(f"{song['title']} - {song['artist']}")
    else:
        print("❌ No matching songs found.")


def save_songs(songs):
    with open("songs.json", "w", encoding="utf-8") as file:
        json.dump(songs, file, indent=4, ensure_ascii=False)

    print("💾 Your songs have been saved!")



def delete_song(songs):
    if not songs:
        print("The song library is empty.")
        return

    print("\n--- Delete a Song ---")

    for number, song in enumerate(songs, start=1):
        print(f"{number}. {song['title']} - {song['artist']}")
        
    while True:
        choice = input("Enter the number of the song to delete: ")

        if choice.isdigit():
            choice = int(choice)

            if 1 <= choice <= len(songs):
                break

        print("Invalid choice. Please enter a valid song number.")
        
    deleted_song = songs.pop(choice - 1)

    save_songs(songs)

    print(f"Successfully deleted: {deleted_song['title']}")



def favorite_song(songs):
    if not songs:
        print("The song library is empty.")
        return

    print("\n--- Choose a Song to Favorite ---")

    for number, song in enumerate(songs, start=1):
        print(f"{number}. {song['title']} - {song['artist']}")

    while True:
        choice = input("Enter the number of the song to favorite: ")

        if choice.isdigit():
            choice = int(choice)

            if 1 <= choice <= len(songs):
                break

        print("Invalid choice. Please enter a valid song number.")

    selected_song = songs[choice - 1]

    if selected_song.get("favorite", False):
        selected_song["favorite"] = False
        message = f"💔 Removed '{selected_song['title']}' from favorites!"
    else:
        selected_song["favorite"] = True
        message = f"❤️ Added '{selected_song['title']}' to favorites!"

    save_songs(songs)

    print(message)



def view_favorites(songs):
    print("\n--- ❤️ Your Favorite Songs ---")
    favorites = []

    for song in songs:
        if song.get("favorite", False):
            favorites.append(song)

    if not favorites:
        print("You haven't added any favorite songs yet.")
        return

    for number, song in enumerate(favorites, start=1):
        print(f"{number}. {song['title']} - {song['artist']}")



def load_songs():
    try:
        with open("songs.json", "r", encoding="utf-8") as file:
            songs = json.load(file)

            for song in songs:
                if "favorite" not in song:
                    song["favorite"] = False

            return songs

    except FileNotFoundError:
        return None



saved_songs = load_songs()

if saved_songs is not None:
    songs = saved_songs

print("🎵 Welcome to Moti's Music Recommender!\n")


def choose_mood():
    print("\nHow are you feeling today?")
    print("1. Happy")
    print("2. Calm")
    print("3. Energetic")
    print("4. Sad")

    moods = {
        "1": "Happy",
        "2": "Calm",
        "3": "Energetic",
        "4": "Sad"
    }

    while True:
        mood_choice = input("Choose your mood (1-4): ").strip()

        if mood_choice in moods:
            return moods[mood_choice]
        else:
            print("Please choose a number from 1 to 4.")


user_mood = choose_mood()
print(f"\nYour mood is: {user_mood} 🎵")

should_exit = False

# Repeat the recommendation process
while True:

    print("\n🎵 MAIN MENU")
    print("1. Get a recommendation")
    print("2. Add a new song")
    print("3. View song library")
    print("4. Search for a song")
    print("5. Edit a song")
    print("6. Delete a song")
    print("7. Favorite a song")
    print("8. View favorite songs")
    print("9. Exit")
    menu_choice = input("Choose an option (1-9): ").strip()
    
    if menu_choice == "2":
        add_song(songs)
        continue

    elif menu_choice == "3":
        view_songs(songs)
        continue

    elif menu_choice == "4":
        search_song(songs)
        continue

    elif menu_choice == "5":
        edit_song(songs)
        continue

    elif menu_choice == "6":
        delete_song(songs)
        continue

    elif menu_choice == "7":
        favorite_song(songs)
        continue

    elif menu_choice == "8":
        view_favorites(songs)
        continue

    elif menu_choice == "9":        
        print("🎵 Thanks for using Moti's Music Recommender !")
        break

    elif menu_choice != ("1","9"):
        print("Please choose 1, 2, 3, 4, 5, or 6.")
        continue

    if not songs:
        print("Your song library is empty. Add some songs first.")
        continue

    # Display all songs with numbers
    for index, song in enumerate(songs, start=1):
        print(f"{index}. {song['title']}")

    # Keep asking until the user chooses a valid song
    while True:
        song_choice = input(
            "\nChoose a song by entering its number: "
        ).strip()

        if song_choice.isdigit():
            song_number = int(song_choice)

            if 1 <= song_number <= len(songs):
                selected_song = songs[song_number - 1]
                break
            else:
                print(
                    "❌ Invalid number! Choose from 1 to",
                    len(songs)
                )
        else:
            print("❌ Please enter a number, such as 1 or 2.")

    # Recommend songs after a valid choice
    print("\n🎵 Songs you might like:")

    recommendations = []

    # Compare the selected song with other songs
    for song in songs:

        # Skip the song the user selected
        if song["title"] == selected_song["title"]:
            continue

        # Calculate the similarity score
        score = calculate_similarity(song, selected_song)

        # Give extra points when a song matches the user's mood
        if song["mood"] == user_mood:
            score += 3

        # Store the score and song together
        recommendations.append((score, song))

    # Sort from highest score to lowest
    recommendations.sort(
        key=lambda item: item[0],
        reverse=True
    )

    # Display the top 2 recommendations with positive scores
    shown = 0

    for score, song in recommendations:

        if score > 0:
            print(
                f"\n{song['title']} - {song['artist']} | Score: {score}"
            )

            # Explain why the song was recommended
            reasons = []

            if song["genre"] == selected_song["genre"]:
                reasons.append("same genre")

            if song["mood"] == user_mood:
                reasons.append("matches your mood")

            if song["energy"] == selected_song["energy"]:
                reasons.append("same energy level")

            if reasons:
                print("   Why? " + ", ".join(reasons))

            shown += 1

            if shown == 2:
                break

    if shown == 0:
        print("Sorry, no similar songs found.")

    print(f"\nWe found {shown} recommended song(s) for you!")

    # Ask whether the user wants another recommendation
    while True:
        answer = input(
            "\nWould you like another recommendation? (yes/no): "
        ).strip().lower()

        if answer in ("yes", "y"):
            user_mood = choose_mood()
            print(f"\nYour new mood is: {user_mood} 🎵")
            break

        elif answer in ("no", "n"):
            print("\n🎵 Thanks for using Moti's Music Recommender!")
            should_exit = True
            break

        else:
            print("❌ Please enter yes or no.")

    # Exit the outer loop if the user chooses no
    if should_exit:
        break
