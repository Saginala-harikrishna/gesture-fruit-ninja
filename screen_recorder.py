import subprocess
import os


class ScreenRecorder:

    def __init__(self, player_name):

        self.player_name = player_name
        self.process = None
        self.temp_file = "temp_recording.mp4"

        # change this if your ffmpeg path is different
        self.ffmpeg_path = r"C:\Users\kriha\Downloads\ffmpeg-2026-03-12-git-9dc44b43b2-essentials_build\ffmpeg-2026-03-12-git-9dc44b43b2-essentials_build\bin\ffmpeg.exe"


    def start(self):

        command = [
            self.ffmpeg_path,
            "-y",
            "-f", "gdigrab",
            "-framerate", "30",
            "-i", "desktop",
            "-vcodec", "libx264",
            "-preset", "ultrafast",
            "-pix_fmt", "yuv420p",
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
                # send 'q' to ffmpeg to stop recording safely
                self.process.stdin.write(b"q")
                self.process.stdin.flush()
                self.process.wait()
            except:
                pass

        if os.path.exists(self.temp_file):

            os.rename(self.temp_file, final_name)

            print("Recording saved:", final_name)