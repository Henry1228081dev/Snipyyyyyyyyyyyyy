# Snipy 🎯

**Snipy** is a high-speed, minimalist visual search engine and AI assistant designed to live seamlessly in your Windows workflow. Developed by **Taha Usman**, it bridges the gap between your screen and high-intelligence vision models with sub-second latency.

## ✨ Core Concept

Snipy is built for speed and focus. Instead of switching tabs or uploading screenshots manually, Snipy allows you to "snip" any part of your screen and start an AI-powered conversation instantly. It's not just a tool; it's a persistent, intelligent layer over your entire desktop.

## 🚀 Key Features

- **Global Hotkey (`Alt+S`)**: Instantaneous screen dimming and region selection. Capture what matters without breaking your flow.
- **Next-Gen Vision AI**: Powered by **Groq** using the `llama-4-scout-17b-16e-instruct` model. Experience sub-second image analysis and ultra-concise insights.
- **Intelligent Desktop Click-Through**: Utilizing advanced `QRegion` masking, Snipy allows you to interact with background applications while the chat remains visible—truly non-obstructive AI.
- **Persistent Side Panel**: A resizable, rounded, and pinned interface designed for deep-dive conversations without cluttering your workspace.
- **Minimalist Timer Pill**: A subtle focus-loss indicator with a shrinking progress bar that keeps you aware of your session status without being distracting.

## 🏗️ Technical Architecture

Snipy is engineered with a high-performance hybrid stack:

- **Backend**: Python 3.11+ powered by **PyQt6**. It handles global hotkeys, high-speed screen capturing with `mss`, and low-level Windows window management.
- **Frontend**: A modern Web stack (HTML5, CSS3, JavaScript) rendered via `QWebEngine`.
- **The Bridge**: Seamless bidirectional communication between Python and the Web UI is achieved via **`QWebChannel`**, allowing for a responsive, native-feeling experience with the flexibility of web design.
- **Inference**: Direct integration with the **Groq API** for industry-leading inference speeds.

## 🎨 Design Style

Snipy follows a **"Premium Utilitarian Minimalism"** (Editorial) aesthetic. 
- **Typography-driven**: Clear, legible, and hierarchically structured.
- **Translucent UI**: Uses Windows acrylic-style effects for a modern, glass-morphism feel.
- **Micro-animations**: Smooth transitions and progress indicators that provide feedback without the noise.

## 🛠️ Installation & Usage

### Running the Standalone Version
1. Download the latest `Snipy.exe` from the [Releases](https://github.com/tahausman/snipy/releases) page.
2. Run the executable.
3. On first launch, you will be prompted to enter your **Groq API Key**. (You can get one at [console.groq.com](https://console.groq.com)).

### Running from Source
1. Clone the repository:
   ```bash
   git clone https://github.com/Henry1228081dev/Snipyyyyyyyyyyyyy.git
   cd snipy
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Launch the application:
   ```bash
   python main.py
   ```

### How to Use
- **`Alt + S`**: Enter Snip Mode. Click and drag to select a region.
- **Chat**: Once snipped, the side panel opens. Ask anything about the captured region.
- **Interact**: Use your background apps normally; Snipy stays out of the way until you need it.
- **Exit**: Click the "X" or use the tray icon to close.

---

*Developed with ❤️ by Taha.U and gemini.*
