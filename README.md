# BRUTE-INSTA
A high-performance Instagram brute force scanner utilizing multiple Tor circuits for anonymity. Designed for security research and penetration testing purposes only.

## Features
- Configurable number of Tor instances (default: 5)
- Telegram notification system
- Session resumption capability
- Automatic dependency installation
- Clean shutdown with progress saving
- Russian exit nodes for Tor circuits

## Prerequisites
- Python 3.8+
- Tor service
- Linux/Unix environment (Tested on Kali Linux)

## Installation

### Automated Setup (Recommended)
```bash
git clone https://github.com/furry-execute/BRUTE-INSTA.git
cd BRUTE-INSTA
pip install -r requirements.txt 
python BRUTE-INSTA.py
```

### Manual Installation
1. Install system dependencies:
```bash
sudo apt update && sudo apt install -y tor python3 python3-pip
```

2. Install Python packages:
```bash
pip3 install stem requests
```

3. Clone repository:
```bash
git clone https://github.com/furry-execute/BRUTE-INSTA.git
cd BRUTE-INSTA
```

## Configuration

### Telegram Setup
1. Create a new bot with [BotFather](https://t.me/BotFather)
2. Get your chat ID by messaging your bot and visiting:
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```
3. Edit the script and replace:
   ```python
   TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"
   TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"
   ```

### Tor Configuration
Modify the number of Tor instances by changing:
```python
TOR_INSTANCES = 5  # Change this value
```

## Usage
```bash
python BRUTE-INSTA.py
```

When prompted:
1. Enter target Instagram username
2. Specify password list file (default: common-passwords.txt)
3. The scanner will automatically:
   - Initialize Tor circuits
   - Verify connections
   - Begin brute force attack

## Command Line Options
```bash
python3 brute.py --resume  # Resume previous session
python3 brute.py --config  # Edit configuration
```

## Troubleshooting

### Tor Connection Issues
```bash
sudo service tor restart
```

### Missing Dependencies
```bash
sudo apt install -y tor python3 python3-pip
pip install -r requirements.txt
```

### Telegram Notifications Not Working
1. Verify bot token and chat ID
2. Ensure the bot has been started with `/start`
3. Check firewall settings for outbound connections

## Legal Disclaimer
This tool is provided for educational and authorized penetration testing purposes only. The developers assume no liability and are not responsible for any misuse or damage caused by this program. Always obtain proper authorization before testing any systems.
