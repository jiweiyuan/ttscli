# Terminal Scene 2: Voice Cloning & Speech
# Duration target: ~16s
# Showcases: voice add from audio, voice list, say with cloned voice, instruct style

Output out/terminal2.mp4
Set Width 1920
Set Height 1080
Set Framerate 30
Set FontFamily "Menlo"
Set FontSize 22
Set Theme "Github"
Set Padding 40
Set TypingSpeed 30ms
Set CursorBlink true
Set Shell zsh

Sleep 400ms

# Clone a voice from an audio sample
Type "tts voice add examples/james.wav --voice james"
Sleep 150ms
Enter
Sleep 2500ms

# List voices to see it registered
Type "tts voice list"
Sleep 150ms
Enter
Sleep 2000ms

# Speak with the cloned voice
Type 'tts say "Hello, this is my cloned voice speaking." --voice james'
Sleep 150ms
Enter
Sleep 3500ms

# Use --instruct for style control
Type 'tts say "Breaking news today." --voice james --instruct "Speak like a news anchor"'
Sleep 150ms
Enter
Sleep 3500ms

Sleep 400ms
