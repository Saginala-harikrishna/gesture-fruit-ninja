import customtkinter as ctk
from PIL import Image
import subprocess
import json
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

WIDTH = 1100
HEIGHT = 650


class GameLauncher(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.title("AI Gesture Game Arena")
        self.geometry(f"{WIDTH}x{HEIGHT}")

        self.player_name = ""
        self.player_phone = ""
        self.current_game = None

        self.load_data()
        self.build_ui()

    # -----------------------------
    # LOAD DATA
    # -----------------------------

    def load_data(self):

        if not os.path.exists("leaderboard.json"):
            self.data = {"fruit_ninja":[]}
            self.save_data()
        else:
            with open("leaderboard.json") as f:
                self.data = json.load(f)

    def save_data(self):

        with open("leaderboard.json","w") as f:
            json.dump(self.data,f,indent=4)

    # -----------------------------
    # BUILD UI
    # -----------------------------

    def build_ui(self):

        title = ctk.CTkLabel(
            self,
            text="AI Gesture Game Arena",
            font=("Arial",30,"bold")
        )
        title.pack(pady=15)

        main = ctk.CTkFrame(self)
        main.pack(fill="both", expand=True, padx=20, pady=10)

        main.grid_columnconfigure(0, weight=1)
        main.grid_columnconfigure(1, weight=1)

        self.build_games_section(main)
        self.build_leaderboard(main)

    # -----------------------------
    # GAME CARDS
    # -----------------------------

    def build_games_section(self,parent):

        games = ctk.CTkFrame(parent)
        games.grid(row=0,column=0,padx=15,sticky="nsew")

        label = ctk.CTkLabel(
            games,
            text="Games",
            font=("Arial",22,"bold")
        )
        label.pack(pady=10)

        grid = ctk.CTkFrame(games)
        grid.pack()

        img = ctk.CTkImage(
            light_image=Image.open("assets/icons/fruit_ninja.png"),
            size=(220,140)
        )

        # fruit ninja card
        card1 = ctk.CTkButton(
            grid,
            image=img,
            text="Gesture Fruit Ninja",
            compound="top",
            width=240,
            height=180,
            command=lambda:self.open_registration("fruit_ninja")
        )
        card1.grid(row=0,column=0,padx=15,pady=15)

        card1.bind("<Enter>", lambda e: card1.configure(width=250,height=190))
        card1.bind("<Leave>", lambda e: card1.configure(width=240,height=180))

        # coming soon card
        card2 = ctk.CTkButton(
            grid,
            text="New Game\nComing Soon",
            width=240,
            height=180,
            state="disabled"
        )
        card2.grid(row=0,column=1,padx=15,pady=15)

        # registration panel
        self.registration_frame = ctk.CTkFrame(games)
        self.registration_frame.pack(pady=20)

    # -----------------------------
    # REGISTRATION
    # -----------------------------

    def open_registration(self,game):

        self.current_game = game

        for widget in self.registration_frame.winfo_children():
            widget.destroy()

        title = ctk.CTkLabel(
            self.registration_frame,
            text="Enter Player Details",
            font=("Arial",18,"bold")
        )
        title.pack(pady=10)

        self.name_entry = ctk.CTkEntry(
            self.registration_frame,
            placeholder_text="Player Name",
            width=250
        )
        self.name_entry.pack(pady=5)

        self.phone_entry = ctk.CTkEntry(
            self.registration_frame,
            placeholder_text="Phone Number",
            width=250
        )
        self.phone_entry.pack(pady=5)

        start_btn = ctk.CTkButton(
            self.registration_frame,
            text="Start Game",
            command=self.start_game
        )
        start_btn.pack(pady=10)

    # -----------------------------
    # START GAME
    # -----------------------------

    def start_game(self):

        self.player_name = self.name_entry.get()
        self.player_phone = self.phone_entry.get()

        if self.player_name == "" or self.player_phone == "":
            return

        subprocess.run(["python","main.py"])

        self.save_score()

    # -----------------------------
    # SAVE SCORE
    # -----------------------------

    def save_score(self):

        if not os.path.exists("last_score.json"):
            return

        with open("last_score.json") as f:
            score_data = json.load(f)

        score = score_data["score"]

        self.data[self.current_game].append({
            "name":self.player_name,
            "phone":self.player_phone,
            "score":score
        })

        self.save_data()
        self.refresh_leaderboard()

    # -----------------------------
    # LEADERBOARD
    # -----------------------------

    def build_leaderboard(self,parent):

        board = ctk.CTkFrame(parent)
        board.grid(row=0,column=1,padx=15,sticky="nsew")

        label = ctk.CTkLabel(
            board,
            text="Leaderboard",
            font=("Arial",22,"bold")
        )
        label.pack(pady=10)

        self.board_box = ctk.CTkTextbox(
            board,
            width=420,
            height=450,
            font=("Courier",14)
        )
        self.board_box.pack(pady=10)

        self.refresh_leaderboard()

    def refresh_leaderboard(self):

        self.board_box.delete("1.0","end")

        for game,players in self.data.items():

            self.board_box.insert("end",f"\n{game.upper()}\n")
            self.board_box.insert("end","-"*40+"\n")

            players.sort(key=lambda x:x["score"],reverse=True)

            trophies = ["🥇","🥈","🥉"]

            for i,p in enumerate(players[:3]):

                line = f"{trophies[i]} {p['name']} | {p['phone']} | {p['score']}\n"

                self.board_box.insert("end",line)

        self.animate_scores()

    # -----------------------------
    # SCORE ANIMATION
    # -----------------------------

    def animate_scores(self):

        text = self.board_box.get("1.0","end")
        self.board_box.delete("1.0","end")

        for i,char in enumerate(text):

            self.after(i*5,lambda c=char:self.board_box.insert("end",c))


app = GameLauncher()
app.mainloop()