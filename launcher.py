import customtkinter as ctk
from PIL import Image
import subprocess
import json
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class GameLauncher(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.title("AI Gesture Game Arena")
        self.geometry("1000x650")

        self.player_name = ""
        self.player_phone = ""

        self.create_layout()
        self.load_leaderboard()

    # -----------------------------
    # UI LAYOUT
    # -----------------------------

    def create_layout(self):

        title = ctk.CTkLabel(
            self,
            text="AI Gesture Game Arena",
            font=("Arial",30,"bold")
        )
        title.pack(pady=20)

        container = ctk.CTkFrame(self)
        container.pack(fill="both", expand=True, padx=20, pady=10)

        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)

        self.create_game_cards(container)
        self.create_leaderboard(container)

    # -----------------------------
    # GAME CARDS
    # -----------------------------

    def create_game_cards(self, parent):

        card_frame = ctk.CTkFrame(parent)
        card_frame.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")

        label = ctk.CTkLabel(
            card_frame,
            text="Available Games",
            font=("Arial",22,"bold")
        )
        label.pack(pady=10)

        img = ctk.CTkImage(
            light_image=Image.open("assets/icons/fruit_ninja.png"),
            size=(220,140)
        )

        card = ctk.CTkButton(
            card_frame,
            image=img,
            text="Gesture Fruit Ninja",
            compound="top",
            height=180,
            width=240,
            command=self.open_registration
        )
        card.pack(pady=20)

    # -----------------------------
    # PLAYER REGISTRATION
    # -----------------------------

    def open_registration(self):

        self.popup = ctk.CTkToplevel(self)
        self.popup.title("Player Registration")
        self.popup.geometry("350x300")

        label = ctk.CTkLabel(
            self.popup,
            text="Enter Player Details",
            font=("Arial",18,"bold")
        )
        label.pack(pady=20)

        self.name_entry = ctk.CTkEntry(
            self.popup,
            placeholder_text="Player Name",
            width=250
        )
        self.name_entry.pack(pady=10)

        self.phone_entry = ctk.CTkEntry(
            self.popup,
            placeholder_text="Phone Number",
            width=250
        )
        self.phone_entry.pack(pady=10)

        start_btn = ctk.CTkButton(
            self.popup,
            text="Start Game",
            command=self.start_game
        )
        start_btn.pack(pady=20)

    # -----------------------------
    # START GAME
    # -----------------------------

    def start_game(self):

        self.player_name = self.name_entry.get()
        self.player_phone = self.phone_entry.get()

        if self.player_name == "" or self.player_phone == "":
            return

        self.popup.destroy()

        subprocess.run(["python", "main.py"])

        self.save_score()

    # -----------------------------
    # SAVE SCORE
    # -----------------------------

    def save_score(self):

        if not os.path.exists("last_score.json"):
            return

        with open("last_score.json") as f:
            data = json.load(f)

        score = data["score"]

        if os.path.exists("leaderboard.json"):

            with open("leaderboard.json") as f:
                leaderboard = json.load(f)
        else:
            leaderboard = []

        leaderboard.append({
            "name": self.player_name,
            "phone": self.player_phone,
            "score": score
        })

        with open("leaderboard.json", "w") as f:
            json.dump(leaderboard, f, indent=4)

        self.load_leaderboard()

    # -----------------------------
    # LEADERBOARD
    # -----------------------------

    def create_leaderboard(self, parent):

        board_frame = ctk.CTkFrame(parent)
        board_frame.grid(row=0, column=1, padx=20, pady=10, sticky="nsew")

        label = ctk.CTkLabel(
            board_frame,
            text="Leaderboard",
            font=("Arial",22,"bold")
        )
        label.pack(pady=10)

        self.table = ctk.CTkTextbox(
            board_frame,
            width=420,
            height=420,
            font=("Courier",14)
        )
        self.table.pack(pady=10)

    def load_leaderboard(self):

        self.table.delete("1.0", "end")

        if not os.path.exists("leaderboard.json"):
            return

        with open("leaderboard.json") as f:
            data = json.load(f)

        data.sort(key=lambda x: x["score"], reverse=True)

        header = f"{'Rank':<6}{'Name':<15}{'Phone':<15}{'Score':<6}\n"
        self.table.insert("end", header)
        self.table.insert("end", "-"*45 + "\n")

        for i, player in enumerate(data[:10]):

            line = f"{i+1:<6}{player['name']:<15}{player['phone']:<15}{player['score']:<6}\n"

            self.table.insert("end", line)


app = GameLauncher()
app.mainloop()