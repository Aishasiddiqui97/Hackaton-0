# WhatsApp Bot - Quick Start Guide (Urdu)

## 🚀 Fixed Version - Ab Sab Kaam Karega!

### Pehle Kya Problem Thi?
```
❌ Message box detect nahi hota tha
❌ Messages read nahi hote the  
❌ Kabhi kabhi chat open fail ho jati thi
```

### Ab Kya Fix Kiya Hai?
```
✅ Message box selector fix kiya (footer wala use karte hain)
✅ Message bubble selector simple kar diya
✅ Chat opening ke liye fallback xpath add kiya
```

---

## 📝 Step-by-Step Setup

### Step 1: Test Selectors (Pehle Verify Karo)
```bash
test_whatsapp_selectors.bat
```

**Ye kya karega:**
- WhatsApp Web open karega
- QR code scan karne dega
- Test karega ke selectors kaam kar rahe hain
- Batayega kon sa element detect ho raha hai

**Expected Output:**
```
✅ Chat list loaded!
✅ Found 3 unread chat(s)
✅ Footer input box found!
✅ Found 15 message bubble(s)
```

---

### Step 2: First Run (QR Scan Ke Saath)
```bash
python whatsapp_agent.py --headful
```

**Kya Hoga:**
1. Browser window dikhai dega
2. WhatsApp Web ka QR code aayega
3. Apne phone se scan karo
4. Bot chats check karega
5. Agar koi unread chat hai to reply karega

**Important:**
- Pehli baar mein yehi command use karein
- QR scan karne ke baad session save ho jata hai
- Agli baar browser headless (bina window) chalega

---

### Step 3: Continuous Mode (Loop)
```bash
python whatsapp_agent.py --loop --interval 120
```

**Options:**
- `--loop` : Bot continuously chalta rahega
- `--interval 120` : Har 2 minute baad naye chats check karega

**Background Mein Kaam:**
```
Scan → Find Unread → Open → Read → Reply → Log → Wait 2min → Repeat
```

---

## 🎯 Expected Logs (Success)

Jab sab sahi chal raha ho:

```
============================================================
  WhatsApp Business Agent – Digital FTE
  Mode: HEADLESS  |  Loop: True  |  Interval: 120s
  Session started: 2026-03-13 10:30:00
============================================================

──── SCAN CYCLE #1 ────
✅ WhatsApp Web is ready.
Found 2 unread chat(s). Processing…

━━━ [1] Opening chat: Ahmed Khan
  Read 3 message(s).
  📊 Category: Lead  🔥 HOT LEAD
  📤 Sending reply to Ahmed Khan…
  ✅ Reply sent successfully.
  📝 Conversation logged to vault

━━━ [2] Opening chat: Fatima Co.
  Read 7 message(s).
  📊 Category: Existing Client
  📤 Sending reply to Fatima Co.…
  ✅ Reply sent successfully.
  📝 Conversation logged to vault

Plan.md updated (2 total chats logged).
  Sleeping 120s before next scan…

──── SCAN CYCLE #2 ────
No unread chats found in this scan.
  Sleeping 120s before next scan…
```

---

## ❌ Error Logs (Problem Indicators)

Agar kuch galat ho:

```
❌ QR code not scanned in time
   Solution: Run with --headful and scan manually

❌ No readable messages found
   Solution: Check if chat has text messages (not just images)

❌ Input box not found in footer
   Solution: Wait for chat to fully load, increase timeout

❌ Playwright timeout error
   Solution: Internet connection check, WhatsApp server issue
```

---

## 🔧 Commands Cheat Sheet

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `test_whatsapp_selectors.bat` | Test selectors | Debugging ke liye |
| `python whatsapp_agent.py --headful` | First run + QR scan | Pehli baar setup |
| `python whatsapp_agent.py --loop` | Continuous mode | Daily use |
| `python whatsapp_agent.py --loop --interval 60` | Fast scanning | Har 1 minute mein check |
| `python whatsapp_agent.py` | Single pass | Test ke liye ek baar |

---

## 📂 Files Structure

```
Hackaton 0/
├── whatsapp_agent.py              # Main bot (FIXED ✅)
├── test_whatsapp_selectors.py     # Selector tester
├── test_whatsapp_selectors.bat    # Easy test runner
├── WHATSAPP_FIXES_SUMMARY.md      # Detailed fixes
├── whatsapp_session/              # Saved login (auto-created)
└── logs/
    └── whatsapp_agent.log         # Detailed logs
```

---

## 🎯 Troubleshooting Tips

### Problem: QR Code Scan Nahi Ho Raha
```bash
# Solution: Headful mode mein manually scan karo
python whatsapp_agent.py --headful
```

### Problem: Bot Reply Nahi Bhej Raha
```bash
# Solution: Logs check karo, dekho kahan fail ho raha hai
tail -f logs/whatsapp_agent.log
```

### Problem: Session Expired Ho Gaya
```bash
# Solution: Session folder delete karke dobara scan karo
rmdir /s whatsapp_session
python whatsapp_agent.py --headful
```

### Problem: Selectors Kaam Nahi Kar Rahe
```bash
# Solution: Test script se verify karo
test_whatsapp_selectors.bat
```

---

## 💡 Pro Tips

1. **First Time Setup:**
   - Hamesha `--headful` use karein
   - "Keep me logged in" tick karein
   - Session save ho jayega

2. **Daily Usage:**
   - `--loop --interval 120` best hai
   - Headless mode mein chalega
   - Background mein quietly kaam karega

3. **Debugging:**
   - Test script use karein regularly
   - Logs check karte rahein
   - Errors ko ignore na karein

4. **Performance:**
   - Interval kam = Zyada responsive (but heavy)
   - Interval zyada = Kam resource usage
   - 120 seconds sweet spot hai

---

## 🎉 Success Checklist

Bot tab successfully kaam kar raha hai jab:

- ✅ WhatsApp Web load ho jaye
- ✅ QR code scan ho jaye (first time)
- ✅ Unread chats detect ho jaaye
- ✅ Chat successfully open ho jaye
- ✅ Messages read ho jaaye
- ✅ AI reply generate ho
- ✅ Reply send ho jaye
- ✅ Conversation log ho jaye
- ✅ Next cycle automatically shuru ho

**Agar sab ticks ✅ hain, to MUBARAK HO! 🎊**

---

## 📞 Support

Agar abhi bhi issue ho to:

1. Logs check karein: `logs/whatsapp_agent.log`
2. Test script chalayein: `test_whatsapp_selectors.bat`
3. Error message note karein
4. Screenshot lein (agar headful mode mein hai)

**Fixed version should work 99% of the time!** 🚀
