Secure Image Steganography CLI Tool

A Python-based terminal-style GUI tool for securely hiding and retrieving messages in PNG images using LSB (Least Significant Bit) steganography combined with Fernet encryption. The tool provides a modern CLI-like interface, password protection, and real-time progress visualization for encoding and decoding processes.

💡 Features

Secure Encryption: Messages are encrypted using Fernet symmetric encryption derived from a user-defined password.

LSB Steganography: Hides encrypted messages inside the least significant bits of an image without noticeable changes.

Password Protected: Only users with the correct password can decode messages.

Responsive CLI-style GUI: Terminal-themed dark interface with monospaced fonts for a professional look.

Live Progress Indicator: Smooth, animated progress bar with percentage overlay for both encoding and decoding.

Large File Support: Optimized vectorized LSB embedding/extraction ensures minimal lag even on large images.

Separate Encode/Decode Image Selection: Prevents accidental overwriting and improves workflow clarity.

🎨 User Interface

Dark theme terminal-like GUI for a modern developer feel.

Input areas for messages and passwords are monospaced with high-contrast text.

Real-time progress bar visible in the foreground with percentage and status messages.

Separate sections for Encode and Decode operations.

🛠️ Technologies & Libraries

Python 3.x

Tkinter – GUI

Pillow (PIL) – Image processing

NumPy – Efficient array operations for LSB steganography

cryptography (Fernet + PBKDF2HMAC) – Secure encryption/decryption

Threading – Keeps GUI responsive during encoding/decoding

⚡ Installation

Clone the repository

git clone https://github.com/yourusername/secure-steganography-cli.git
cd secure-steganography-cli


Install dependencies

pip install pillow numpy cryptography


Run the program

python steg_cli_tool.py

📦 Usage
Encode a Message

Open the program.

Navigate to the Encode Message section.

Enter the message to hide.

Set a password for encryption.

Select an input PNG image.

Specify the output image filename.

Click “Encode & Save”.

Monitor the animated progress bar.

The message is securely embedded and encrypted in the output image.

Decode a Message

Navigate to the Decode Message section.

Select the encoded PNG image.

Enter the password used during encoding.

Click “Decode Message”.

Monitor the progress bar as the program extracts the hidden message.

The decoded message will appear in the Decoded Message box.

🔒 Security Notes

Encryption uses Fernet symmetric encryption with a password-derived key (PBKDF2HMAC).

Only images with sufficient capacity can store messages; the tool will warn if a message is too large.

Messages are appended with "EOF" during encoding to ensure correct extraction.

🚀 Advantages

CLI Terminal Feel: Perfect for developers who prefer minimal and focused UI.

Safe and Encrypted: No plaintext message is ever stored in the image.

Real-time Feedback: Smooth progress bar ensures users know operation status.

Cross-platform: Runs on Windows, Linux, and MacOS with Python 3.x.

📁 File Structure
secure-steganography-cli/
│
├─ steg_cli_tool.py        # Main Python program
├─ README.md               # Project documentation
├─ requirements.txt        # Dependencies (optional)
└─ examples/               # Example input/output images (optional)

📌 Future Enhancements

Add drag-and-drop support for images.

Export progress log to CLI console.

Support for other image formats (JPEG, BMP).

Add multi-language support for GUI.

📝 License

MIT License – Free for personal and commercial use.
