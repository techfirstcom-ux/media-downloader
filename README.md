# media-downloader
Universal Media Downloader is a lightweight yet powerful Flask-based web application that allows users to download media content from multiple platforms including YouTube, Instagram, Facebook, Twitter (X), TikTok, and more. The application provides an intuitive interface where users can paste a media link, choose their preferred download type, and select from available formats.

The app focuses on flexibility and user control. For videos, it lists all the standard resolutions — ranging from 144p up to 2160p (4K) — along with estimated file sizes. For audio-only downloads, it shows available audio qualities such as 128 kbps, 192 kbps, 256 kbps, and 320 kbps, again with size estimations. This makes it easy for users to save bandwidth by selecting a lower quality or go for the best available quality when storage and speed are not a concern.

A key feature of the application is that when users choose Video + Audio, the two streams are automatically merged into a single media file. Many platforms serve audio and video separately, but Universal Media Downloader handles this behind the scenes, delivering a complete and ready-to-play file.

The UI is designed with a modern neon-inspired theme, ensuring both usability and aesthetics. It guides users through each step — from pasting the URL and selecting the platform, to choosing the desired format. Error messages and invalid URLs are handled gracefully, so users receive clear feedback when something goes wrong.

This project is ideal for anyone who wants a self-hosted media downloader that’s simple to set up and works across multiple platforms. Since it runs on Flask, it can be easily deployed on your local machine, VPS, or even cloud services.

Features:

Supports YouTube, Instagram, Facebook, Twitter (X), TikTok, and more.

Download videos in resolutions up to 2160p (4K).

Download high-quality audio with size estimation.

Automatic merging of video + audio.

Modern, responsive, and user-friendly interface.

Free and open-source.

Universal Media Downloader combines simplicity, functionality, and style to give users full control over the content they download.










🌐 Universal Media Downloader

Universal Media Downloader is a free, open-source Flask web application that allows you to download videos and audio from multiple platforms including YouTube, Instagram, Facebook, Twitter (X), TikTok, and more. With a simple and modern interface, it provides high flexibility in choosing the exact media quality you need — whether it’s 144p for saving data or 2160p (4K) for the best experience.
This project is powered by yt-dlp



✨ Features


🎥 Video downloads in all common resolutions: 144p, 240p, 360p, 480p, 720p, 1080p, 1440p, and 2160p.

🎧 Audio-only downloads with estimated sizes and available bitrates.

🔗 Automatic merging of video + audio when required (done with FFmpeg).

🌐 Multi-platform support: YouTube, Facebook, Instagram, Twitter (X), TikTok, and more.

📊 Estimated file sizes displayed before downloading.

🎨 Modern and responsive UI, easy for anyone to use.

⚡ Lightweight & self-hosted, so you’re always in control.





















🚀 Installation

1. Clone the Repository
   git clone https://github.com/your-username/universal-media-downloader.git
   cd universal-media-downloader

2. Install Dependencies
   pip install -r requirements.txt

3. Install FFmpeg (Required)
   Linux (Ubuntu/Debian): sudo apt update && sudo apt install ffmpeg
   Windows: Download from ffmpeg.org
   macOS: brew install ffmpeg















   

▶️ Usage

1. Start the Flask server:
   python app.py
         or
   python3 app.py
   
2. Open your browser at:
   http://127.0.0.1:5000

3. Paste a video/audio link.

4. Select your desired video resolution or audio quality.

5. Click Download and the file will be prepared for you.

















⚠️ Disclaimer

This project is for educational and personal use only. Please ensure that your usage complies with the copyright laws and terms of service of each respective platform.









🤝 Contributing

Contributions are welcome! Feel free to fork the repository and submit pull requests.






📜 License

This project is licensed under the MIT License.
