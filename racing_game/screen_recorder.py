import subprocess
import os
import time
import shutil


class ScreenRecorder:

    def __init__(self, player_name):

        self.player_name = player_name
        self.process = None
        self.temp_file = "temp_recording.mp4"

        self.output_folder = "race_recordings"

        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        # Update if your ffmpeg path changes
        self.ffmpeg_path = r"C:\Users\kriha\Downloads\ffmpeg-2026-03-12-git-9dc44b43b2-essentials_build\ffmpeg-2026-03-12-git-9dc44b43b2-essentials_build\bin\ffmpeg.exe"

    def start(self):

        command = [

            self.ffmpeg_path,
            "-y",

            "-use_wallclock_as_timestamps", "1",

            # VIDEO
            "-f", "gdigrab",
            "-framerate", "30",
            "-i", "desktop",

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

            self.temp_file
        ]

        print("Recording started")

        self.process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    def stop(self, final_name):

        if self.process:

            try:

                print("Stopping recording...")

                self.process.stdin.write(b"q")
                self.process.stdin.flush()

                self.process.wait()

                time.sleep(2)

            except Exception as e:
                print("Error stopping ffmpeg:", e)

        if os.path.exists(self.temp_file):

            final_path = os.path.join(self.output_folder, final_name)

            try:

                shutil.move(self.temp_file, final_path)

                print("Recording saved successfully")
                print("Saved to:", final_path)

            except Exception as e:

                print("Error saving recording:", e)