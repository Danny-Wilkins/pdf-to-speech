for %%a in (*.mp3) do (
  echo processing %%a
  ffmpeg -i "%%a" "%%~na.wav"
)