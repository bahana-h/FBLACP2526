# 🚀 Quick Start Guide

## Run the Website in 3 Seconds!

### Step 1: Download/Clone the Repository
```bash
git clone <repository-url>
cd FBLACP2526
```

### Step 2: Run One Command

**macOS/Linux:**
```bash
./start.sh
```

**Windows:**
```bash
start.bat
```

**Or (works everywhere):**
```bash
python3 start.py
```

### Step 3: Open Your Browser
The website will automatically start at:
```
http://localhost:5000
```

That's it! 🎉

---

## What Happens Automatically?

✅ Checks if Python is installed  
✅ Installs Flask if needed  
✅ Starts the web server  
✅ Creates sample data on first run  

**No manual installation required!**

---

## Troubleshooting

**"Python not found"**
- Install Python 3.6+ from [python.org](https://www.python.org/downloads/)

**"Permission denied" (macOS/Linux)**
```bash
chmod +x start.sh
./start.sh
```

**Port 5000 already in use**
- The script will show an error
- Close other applications using port 5000
- Or edit `app.py` to use a different port

---

## Need Help?

See the full [README.md](README.md) for detailed documentation.

