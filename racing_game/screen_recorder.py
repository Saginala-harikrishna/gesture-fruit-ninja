import subprocess
import os
import time


class ScreenRecorder:

    def __init__(self, player_name):

        self.player_name = player_name
        self.process = None

        self.output_folder = "race_recordings"

        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        # Update if your ffmpeg path changes
        self.ffmpeg_path = r"C:\Users\kriha\Downloads\ffmpeg-2026-03-12-git-9dc44b43b2-essentials_build\ffmpeg-2026-03-12-git-9dc44b43b2-essentials_build\bin\ffmpeg.exe"

        self.output_file = None

    def start(self):

        timestamp = int(time.time())
        self.output_file = os.path.join(
            self.output_folder,
            f"{self.player_name}_{timestamp}.mp4"
        )

        command = [

            self.ffmpeg_path,
            "-y",

            "-use_wallclock_as_timestamps", "1",

            # VIDEO
            "-f", "gdigrab",
            "-framerate", "30",
            "-draw_mouse", "0",
            "-video_size", "900x700",
            "-i", "title=Gesture Racing",

            # AUDIO
            "-thread_queue_size", "512",
            "-f", "dshow",
            "-i", "audio=CABLE Output (VB-Audio Virtual Cable)",

            "-map", "0:v",
            "-map", "1:a",

            "-c:v", "libx264",
            "-preset", "veryfast",
            "-pix_fmt", "yuv420p",

            "-c:a", "aac",
            "-b:a", "192k",

            "-movflags", "+faststart",

            self.output_file
        ]

        print("Recording started")

        self.process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    def stop(self):

        if self.process:

            try:

                print("Stopping recording...")

                self.process.stdin.write(b"q")
                self.process.stdin.flush()
                self.process.stdin.close()

                self.process.wait()

                print("Recording saved successfully")
                print("Saved to:", self.output_file)

            except Exception as e:
                print("Error stopping ffmpeg:", e)

            finally:
                self.process = None