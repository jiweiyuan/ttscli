# ttscli Demo Recording
# Requires: vhs (https://github.com/charmbracelet/vhs)
# Run: vhs ttscli_demo.tape

Output out/terminal.mp4
Set Width 1920
Set Height 1080
Set Framerate 30
Set FontFamily "Menlo"
Set FontSize 22
Set Theme "Dracula"
Set Padding 40
Set TypingSpeed 50ms
Set CursorBlink true
Set Shell zsh

# --- Scene 1: Version check ---
Sleep 500ms
Type "tts --version"
Sleep 300ms
Enter
Sleep 2s

# --- Scene 2: List voices (empty) ---
Type "tts voice list"
Sleep 300ms
Enter
Sleep 3s

# --- Scene 3: Add a voice from sample ---
Type "tts voice add examples/james.wav --voice james"
Sleep 300ms
Enter
Sleep 4s

# --- Scene 4: Verify voice was added ---
Type "tts voice list"
Sleep 300ms
Enter
Sleep 3s

# --- Scene 5: Set default voice ---
Type "tts voice default james"
Sleep 300ms
Enter
Sleep 3s

# --- Scene 6: Basic speech generation ---
Type 'tts say "Hello world! This is the TTS CLI in action."'
Sleep 300ms
Enter
Sleep 6s

# --- Scene 7: Instructed speech style ---
Type 'tts say "Welcome to the future of voice synthesis." --instruct "Speak with enthusiasm and energy"'
Sleep 300ms
Enter
Sleep 6s

# --- Scene 8: Save to file ---
Type 'tts say "This speech is saved to a file." --save output.wav --no-play'
Sleep 300ms
Enter
Sleep 4s

# --- Scene 9: Show configuration ---
Type "tts config show"
Sleep 300ms
Enter
Sleep 4s

# --- Scene 10: Outro ---
Sleep 1s
Type "# Install: pip install tts-cli"
Sleep 300ms
Enter
Sleep 1s
Type "# GitHub: github.com/your-org/ttscli"
Sleep 300ms
Enter
Sleep 3s
