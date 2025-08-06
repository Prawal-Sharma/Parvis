# Pi-Jarvis Quick Start Guide

**🎉 Your AI Assistant is Ready! Here's how to use it in 5 minutes.**

## What You Have

Pi-Jarvis is a **100% offline AI assistant** that:
- Listens for "Parvis" wake word
- Understands voice commands
- Responds with speech
- Can see with computer vision
- Runs automatically 24/7

**Current Status: 89% Complete - Production Ready!**

---

## Step 1: Install Pi-Jarvis (One Command)

Open terminal and run:

```bash
cd /home/raspberry/Desktop/Parvis
./systemd/install-service.sh
```

**What this does:**
- Sets up Pi-Jarvis to start automatically when Pi boots
- Configures health monitoring (checks every 5 minutes)
- Sets up log management
- Tests that everything works

**Expected output:** Should say "🎉 Pi-Jarvis production deployment complete!"

---

## Step 2: Check It's Running

```bash
# Check service status
systemctl status pi-jarvis.service

# Should show: Active (running)
```

If it says "Unit pi-jarvis.service could not be found", the installation didn't complete. Try Step 1 again.

---

## Step 3: Start Talking!

**Say:** "Parvis" (wait for response) then give a command

### Try These Commands:

**🕐 Time & Timers:**
- "Parvis" → "What time is it?"
- "Parvis" → "Set a timer for 5 minutes"
- "Parvis" → "What's today's date?"

**🌍 Translations:**
- "Parvis" → "How do you say hello in Spanish?"
- "Parvis" → "Translate water to French"

**👁️ Computer Vision:**
- "Parvis" → "What do you see?"
- "Parvis" → "Describe what's in front of you"

**💬 General Chat:**
- "Parvis" → "Tell me a joke"
- "Parvis" → "What's the weather like?" (explains offline mode)

---

## Step 4: Service Management

**Control Pi-Jarvis:**

```bash
# Start Pi-Jarvis
sudo systemctl start pi-jarvis.service

# Stop Pi-Jarvis  
sudo systemctl stop pi-jarvis.service

# Restart Pi-Jarvis
sudo systemctl restart pi-jarvis.service

# Watch what it's doing (live logs)
journalctl -u pi-jarvis.service -f
```

---

## No Hardware? No Problem!

Test everything without microphone/camera:

```bash
cd /home/raspberry/Desktop/Parvis
source venv/bin/activate

# Test all features (no hardware needed)
python -m assistant.test_intents

# Chat by typing instead of speaking
python -m assistant.main text

# Full simulation mode
python -m assistant.parvis simulation true
```

---

## Troubleshooting

### Pi-Jarvis Won't Start?

1. **Check logs:**
   ```bash
   journalctl -u pi-jarvis.service -n 20
   ```

2. **Reinstall:**
   ```bash
   cd /home/raspberry/Desktop/Parvis
   ./systemd/install-service.sh
   ```

### Can't Hear Responses?

1. **Test audio:**
   ```bash
   espeak "Hello Pi-Jarvis"
   ```

2. **Check volume:** Make sure Pi audio isn't muted

### Wake Word Not Working?

1. **Check microphone:**
   ```bash
   arecord -l  # Should list input devices
   ```

2. **Test recording:**
   ```bash
   arecord -d 5 test.wav
   aplay test.wav
   ```

3. **Use text mode for testing:**
   ```bash
   python -m assistant.main text
   ```

---

## Hardware Recommendations

**For full functionality:**
- 🎤 **USB Microphone** (any USB mic or headset)
- 📷 **Pi Camera v3** (for "What do you see?" commands)
- 🔊 **Speaker** (HDMI/3.5mm already work)

**Without hardware:** Everything still works in simulation/text mode!

---

## Health Monitoring

Pi-Jarvis monitors itself:

```bash
# Manual health check
./systemd/health-check.sh

# View health logs
tail -f /var/log/pi-jarvis/health-check.log

# Weekly status report  
./systemd/status-report.sh
```

---

## 🎯 That's It!

**You now have a production-ready AI assistant running 24/7 on your Pi!**

- **Starts automatically** when Pi boots
- **Monitors itself** and restarts if needed
- **Works offline** - no internet required
- **Extensible** - easy to add new features

**Next:** Just say "Parvis" and start using your AI assistant! 

For advanced features and development, see the full documentation:
- `README.md` - Complete installation guide
- `ARCHITECTURE.md` - How it works
- `TESTING.md` - Advanced testing
- `DEVELOPMENT.md` - Add new features