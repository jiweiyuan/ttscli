# Terminal Scene 3: Generate, Export & Workflow
# Duration target: ~16s
# Showcases: generate to file, stdin pipe, config, JSON output

Output out/terminal3.mp4
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

# Generate speech and save to WAV file
Type 'tts generate "Welcome to our podcast." --voice james -o podcast_intro.wav'
Sleep 150ms
Enter
Sleep 3000ms

# Pipe text from stdin
Type 'echo "Piped from the shell" | tts say --voice james'
Sleep 150ms
Enter
Sleep 3000ms

# Show configuration
Type "tts config show"
Sleep 150ms
Enter
Sleep 2500ms

# JSON output for scripting & automation
Type "tts voice list --json"
Sleep 150ms
Enter
Sleep 2500ms

# Outro — install reminder
Type "# curl -fsSL https://raw.githubusercontent.com/jiweiyuan/ttscli/main/install.sh | bash"
Sleep 150ms
Enter
Sleep 1500ms

Sleep 400ms
