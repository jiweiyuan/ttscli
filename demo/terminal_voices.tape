# Terminal Scene 1: Install & Setup
# Duration target: ~16s
# Showcases: curl one-liner install, tts init, tts --version

Output out/terminal1.mp4
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

# One-line install via curl
Type "curl -fsSL https://raw.githubusercontent.com/jiweiyuan/ttscli/main/install.sh | bash"
Sleep 150ms
Enter
Sleep 4000ms

# Initialize — auto-detects backend and downloads model
Type "tts init"
Sleep 150ms
Enter
Sleep 4000ms

# Verify it works
Type "tts --version"
Sleep 150ms
Enter
Sleep 1500ms

# Quick hello world to prove it's live
Type 'tts say "Hello from TTS CLI!"'
Sleep 150ms
Enter
Sleep 3000ms

Sleep 400ms
