"""
Autonomous WhatsApp Business Agent - Playwright MCP Style
Follows exact 7-step process with professional auto-replying
"""

import time
from pathlib import Path
from playwright.sync_api import sync_playwright
from datetime import datetime
from whatsapp_logger import log_conversation
from whatsapp_classifier import classify, is_hot_lead, is_sensitive
from whatsapp_reply_engine import generate_reply

# Configuration
SESSION_DIR = Path(__file__).parent / "whatsapp_session"
CHECK_INTERVAL = 15  # seconds between scan cycles
CHAT_LOAD_WAIT = 6   # seconds for virtual scroll to render
MSG_LOAD_WAIT = 3    # seconds for messages to load after opening chat
# Reduce console noise: block WhatsApp crash-log upload (400 errors)
SUPPRESS_CRASHLOG_REQUESTS = True
# Extra wait after WA loads so IndexedDB races settle (reduces "Key already exists" errors)
POST_LOAD_SETTLE_SEC = 5
# If "Key already exists in object store" keeps happening: clear site data for web.whatsapp.com and re-scan QR.


def log(message: str):
    """Simple logging with timestamp."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")


# Removed local simple generate_reply to use the professional whatsapp_reply_engine.generate_reply


def main():
    """Main autonomous agent loop."""
    
    with sync_playwright() as pw:
        # Launch browser with persistent session (FORCE GPU MODE for input box)
        browser = pw.chromium.launch_persistent_context(
            user_data_dir=str(SESSION_DIR),
            headless=False,
            channel="chrome",
            args=[
                # Anti-detection
                "--disable-blink-features=AutomationControlled",

                # Sandbox bypass (required for containers/root)
                "--no-sandbox",
                "--disable-setuid-sandbox",

                # FORCE GPU rendering (fixes input box rendering issue)
                "--use-gl=desktop",
                "--enable-gpu-rasterization",
                "--enable-native-gpu-memory-buffers",
                "--enable-accelerated-2d-canvas",
                "--enable-accelerated-video-decode",
                "--ignore-gpu-blocklist",

                # Memory & stability
                "--disable-dev-shm-usage",
                "--disable-software-rasterizer",

                # Network & rendering
                "--enable-features=NetworkService,NetworkServiceInProcess",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",

                # Extra rendering hints
                "--force-device-scale-factor=1",
            ],
            ignore_default_args=["--enable-automation"],
        )
        
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.set_viewport_size({"width": 1280, "height": 900})
        
        # Block WhatsApp crash-log upload to avoid 400 console errors
        if SUPPRESS_CRASHLOG_REQUESTS:
            page.route("**/crashlogs.whatsapp.net/**", lambda route: route.abort())
        
        log("=" * 70)
        log("AUTONOMOUS WHATSAPP BUSINESS AGENT - STARTED")
        log("=" * 70)
        log("💡 Browser console may show WA internal errors (IndexedDB/crashlog). They are usually non-fatal.")
        log("   Use only ONE WhatsApp Web tab; avoid opening WA elsewhere to reduce them.")
        
        # ═══════════════════════════════════════════════════
        # STEP 1: Navigate to WhatsApp Web
        # ═══════════════════════════════════════════════════
        log("STEP 1: Navigating to https://web.whatsapp.com")
        page.goto("https://web.whatsapp.com", wait_until="domcontentloaded")
        
        # ═══════════════════════════════════════════════════
        # STEP 2: Wait for page to load + QR code handling
        # ═══════════════════════════════════════════════════
        log("STEP 2: Waiting for WhatsApp Web to load...")
        
        wa_ready = False
        selectors_to_try = [
            '#pane-side', 
            'div[data-testid="chat-list"]', 
            'div[aria-label="Chat list"]',
            'div[role="navigation"]'
        ]
        
        # Check for QR code container
        try:
            # Wait a few seconds for QR or Chat list to appear
            page.wait_for_selector('canvas, #pane-side', timeout=10_000)
            if page.is_visible('canvas') or page.is_visible('div[data-testid="qr-container"]'):
                log("⚠️ QR CODE SCAN KARO - Please scan QR code in the browser window")
                log("Waiting up to 120s for scan...")
        except:
            pass

        # Robust wait loop
        start_time = time.time()
        timeout = 120  # seconds
        
        while time.time() - start_time < timeout:
            for sel in selectors_to_try:
                if page.is_visible(sel):
                    log(f"✅ WhatsApp Web loaded successfully (detected via {sel})")
                    wa_ready = True
                    break
            if wa_ready:
                break
            
            # Check if still on landing page/QR
            if page.is_visible('canvas'):
                # Still waiting for scan...
                pass
            elif page.is_visible('div[data-testid="landing-main"]'):
                # Landing page but maybe no QR? Just wait.
                pass
                
            time.sleep(2)
        
        if not wa_ready:
            log("❌ Error: WhatsApp Web did not load in time.")
            log("💡 Try these steps:")
            log("   1. Click 'Refresh' (F5) in the browser window.")
            log("   2. If the QR code is showing, please scan it.")
            log("   3. Check if your phone is connected to the internet.")
            input("Press Enter to continue after fixing (or Ctrl+C to stop)...")
            # Final check
            try:
                page.wait_for_selector('#pane-side', timeout=30_000)
                log("✅ Resumed successfully!")
            except:
                log("❌ Still failing. Exiting.")
                return

        # Let WhatsApp's IndexedDB/storage settle
        if POST_LOAD_SETTLE_SEC > 0:
            log(f"   Waiting {POST_LOAD_SETTLE_SEC}s for WA storage to settle...")
            page.wait_for_timeout(POST_LOAD_SETTLE_SEC * 1000)
        
        # ═══════════════════════════════════════════════════
        # MAIN LOOP - Steps 4-7
        # ═══════════════════════════════════════════════════
        cycle_count = 0
        
        while True:
            cycle_count += 1
            log("\n" + "=" * 70)
            log(f"CYCLE #{cycle_count} - Scanning for unread chats")
            log("=" * 70)
            
            # ═══════════════════════════════════════════════
            # STEP 3: Wait for virtual scroll to render
            # ═══════════════════════════════════════════════
            log("STEP 3: Waiting for chat list to fully render...")
            page.wait_for_timeout(CHAT_LOAD_WAIT * 1000)
            
            # ═══════════════════════════════════════════════
            # STEP 4: Find all chat rows
            # ═══════════════════════════════════════════════
            log("STEP 4: Finding all chat rows...")
            
            try:
                # Get chat list container
                chat_list = page.locator("#pane-side")
                
                # Dynamically detect correct chat row selector (WhatsApp Web changes often)
                log("🔍 Detecting working chat row selector via JavaScript...")
                selector_result = page.evaluate("""
                    () => {
                        const container = document.querySelector('#pane-side');
                        if (!container) {
                            return { selector: null, count: 0 };
                        }
                        const selectors = [
                            'div[aria-label][role="listitem"]', // FIX 1: Primary 2025 selector
                            'div[role=\"listitem\"]',
                            'div[data-testid=\"cell-frame-container\"]',
                            'div[tabindex=\"-1\"]',
                            'div._ak72',
                        ];
                        for (const sel of selectors) {
                            const els = container.querySelectorAll(sel);
                            if (els && els.length > 0) {
                                return { selector: sel, count: els.length };
                            }
                        }
                        return { selector: null, count: 0 };
                    }
                """)
                
                detected_selector = selector_result.get("selector") if selector_result else None
                detected_count = selector_result.get("count") if selector_result else 0
                
                if not detected_selector:
                    log("❌ No working chat row selector detected. WhatsApp DOM may have changed.")
                    log("💡 Please share this log so we can add the new selector.")
                    time.sleep(CHECK_INTERVAL)
                    continue
                
                log(f"✅ Using selector: '{detected_selector}' (found {detected_count} elements via JS)")
                
                # Use the detected selector inside the chat list
                chat_rows = chat_list.locator(detected_selector).all()
                
                total_chats = len(chat_rows)
                log(f"✅ Found {total_chats} total chats in list (Playwright locator)")
                
            except Exception as e:
                log(f"❌ Error finding chat rows: {e}")
                log("⏭️ Skipping to next cycle...")
                time.sleep(CHECK_INTERVAL)
                continue
            
            # ═══════════════════════════════════════════════
            # STEP 5: Check for unread badges
            # ═══════════════════════════════════════════════
            log("STEP 5: Checking for unread chats...")
            
            unread_chats = []
            
            for i, chat_row in enumerate(chat_rows):
                try:
                    # Check if this chat has unread badge using robust DOM inspection
                    has_unread = chat_row.evaluate(
                        """(el) => {
                            const selectors = [
                                '[data-testid="icon-unread-count"]',
                                'span[aria-label*="unread"]',
                                'span[aria-label*="new message"]',
                                'div[aria-label*="unread"]',
                                'span[data-testid*=\"unread\"]',
                                'div[data-testid*=\"unread\"]',
                                '[data-icon*=\"unread\"]'
                            ];
                            for (const sel of selectors) {
                                const found = el.querySelector(sel);
                                if (found) return true;
                            }
                            return false;
                        }"""
                    )
                    
                    if has_unread:
                        # Extract contact name with multiple fallbacks
                        contact_name = None
                        try:
                            name_locator = chat_row.locator('div[data-testid="cell-frame-title"] span')
                            if name_locator.count() > 0:
                                contact_name = name_locator.first.inner_text().strip()
                        except Exception:
                            contact_name = None
                        
                        if not contact_name:
                            try:
                                # Fallback: first span with dir="auto" inside the row
                                alt_name_locator = chat_row.locator('span[dir="auto"]').first
                                contact_name = alt_name_locator.inner_text().strip()
                            except Exception:
                                contact_name = None
                        
                        if not contact_name:
                            contact_name = f"Contact #{i+1}"
                        
                        unread_chats.append({
                            'row': chat_row,
                            'name': contact_name,
                            'index': i
                        })
                        log(f"  🔔 UNREAD found: {contact_name}")
                    
                except Exception as e:
                    log(f"  ⚠️ Error checking chat {i+1}: {e}")
            
            if not unread_chats:
                log("✅ No unread chats found. All caught up!")
            else:
                log(f"\n🔥 Found {len(unread_chats)} unread chat(s) to process")
            
            # ═══════════════════════════════════════════════
            # STEP 6: Process each UNREAD chat
            # ═══════════════════════════════════════════════
            for idx, chat_info in enumerate(unread_chats, 1):
                contact_name = chat_info['name']
                chat_row = chat_info['row']

                log(f"\n{'─' * 70}")
                log(f"Processing [{idx}/{len(unread_chats)}] - Contact: {contact_name}")
                log('─' * 70)

                try:
                    # STEP 6a: Click chat row to open
                    log(f"STEP 6a: Opening chat: {contact_name}")

                    # Add timeout protection
                    try:
                        log(f"   🔍 Scrolling chat into view...")
                        chat_row.scroll_into_view_if_needed(timeout=5000)
                        page.wait_for_timeout(500)

                        log(f"   🔍 Clicking chat row...")
                        chat_row.click(force=True, timeout=5000)
                        log(f"   ✅ Chat clicked successfully")
                    except Exception as click_error:
                        log(f"   ⚠️ Click failed: {click_error}")
                        log(f"   🔄 Trying alternative click method...")
                        try:
                            # Alternative: JavaScript click
                            page.evaluate("""(name) => {
                                const rows = document.querySelectorAll('#pane-side div[tabindex="-1"]');
                                for (const row of rows) {
                                    if (row.innerText.includes(name)) {
                                        row.click();
                                        return true;
                                    }
                                }
                                return false;
                            }""", contact_name)
                            log(f"   ✅ JavaScript click succeeded")
                        except Exception as js_error:
                            log(f"   ❌ JavaScript click also failed: {js_error}")
                            log(f"   ⏭️ Skipping this chat...")
                            continue
                    
                    # STEP 6b: Wait for messages to load
                    log("STEP 6b: Waiting for messages to load...")
                    # Increased wait time for 2025 WhatsApp Web structure
                    page.wait_for_timeout(3000)
                    page.wait_for_timeout(MSG_LOAD_WAIT * 1000)

                    # Verify we're in a chat - Improved robust check
                    log("   🔍 Checking for message container...")
                    msg_container = None
                    try:
                        msg_container = page.wait_for_selector('div[data-testid="msg-container"]', timeout=5000)
                        log("   ✅ Primary message container found")
                    except:
                        log("   ⚠️ Primary message container not found, checking fallback...")
                        try:
                            msg_container = page.wait_for_selector('div.copyable-area', timeout=3000)
                            log("   ✅ Fallback container found")
                        except:
                            log("   ❌ No message container found")

                    if not msg_container:
                        log("⚠️ Message container not found, skipping this chat...")
                        # Go back to chat list
                        page.keyboard.press("Escape")
                        page.wait_for_timeout(1000)
                        continue

                    log("✅ Chat opened, messages loaded")
                    
                    # STEP 6c: Read ONLY incoming messages (UPDATED 2025 SELECTORS)
                    log("STEP 6c: Reading incoming messages...")

                    incoming_messages = []
                    try:
                        # FAST METHOD: Use JavaScript to extract all messages at once
                        log("   🔍 Using fast JavaScript extraction with 2025 selectors...")

                        js_result = page.evaluate("""() => {
                            const messages = [];

                            // Method 1: Classic message-in divs (still works in 2025)
                            const incomingDivs = document.querySelectorAll('div.message-in');
                            for (const div of incomingDivs) {
                                const textSpan = div.querySelector('span.selectable-text');
                                if (textSpan && textSpan.innerText) {
                                    messages.push(textSpan.innerText.trim());
                                }
                            }

                            // Method 2: data-id attribute with class patterns (2024-2025 structure)
                            if (messages.length === 0) {
                                const allRows = document.querySelectorAll(
                                    'div[data-id][class*="_amk6"], ' +
                                    'div[data-id][class*="_akbu"], ' +
                                    'div[data-id][class*="message"]'
                                );
                                for (const row of allRows) {
                                    // Skip outgoing messages
                                    if (row.querySelector('div[class*="message-out"]')) continue;

                                    const spans = row.querySelectorAll(
                                        'span[class*="selectable-text"], ' +
                                        'span[dir="ltr"], ' +
                                        'span[dir="rtl"]'
                                    );
                                    for (const span of spans) {
                                        const txt = span.innerText ? span.innerText.trim() : '';
                                        if (txt.length > 1) {
                                            messages.push(txt);
                                            break;
                                        }
                                    }
                                }
                            }

                            // Method 3: role="row" structure (newer WhatsApp Web)
                            if (messages.length === 0) {
                                const rows = document.querySelectorAll('div[role="row"]');
                                for (const row of rows) {
                                    // Skip outgoing messages
                                    if (row.querySelector('div[class*="message-out"]')) continue;

                                    const textSpans = row.querySelectorAll('span.selectable-text, span[dir]');
                                    for (const span of textSpans) {
                                        const txt = span.innerText ? span.innerText.trim() : '';
                                        if (txt.length > 1) {
                                            messages.push(txt);
                                            break;
                                        }
                                    }
                                }
                            }

                            // Method 4: Group chat messages (all messages, filter out own)
                            if (messages.length === 0) {
                                const allMsgContainers = document.querySelectorAll('div[data-testid="msg-container"]');
                                for (const container of allMsgContainers) {
                                    // Skip outgoing messages
                                    if (container.querySelector('div.message-out, div[class*="message-out"]')) {
                                        continue;
                                    }
                                    const textSpan = container.querySelector('span.selectable-text');
                                    if (textSpan && textSpan.innerText) {
                                        messages.push(textSpan.innerText.trim());
                                    }
                                }
                            }

                            // Method 5: Broad fallback - last resort
                            if (messages.length === 0) {
                                const allSpans = document.querySelectorAll(
                                    'div[data-testid="msg-container"] span[dir="ltr"], ' +
                                    'div[data-testid="msg-container"] span[dir="rtl"]'
                                );
                                for (const span of allSpans) {
                                    const msgOut = span.closest('div.message-out, div[class*="message-out"]');
                                    if (msgOut) continue;
                                    const txt = span.innerText ? span.innerText.trim() : '';
                                    if (txt.length > 1 && !messages.includes(txt)) {
                                        messages.push(txt);
                                    }
                                }
                            }

                            // Remove duplicates
                            const unique = [...new Set(messages)];
                            return {
                                count: unique.length,
                                messages: unique
                            };
                        }""")

                        if js_result and js_result.get('messages'):
                            incoming_messages = js_result['messages']
                            log(f"   ✅ Extracted {len(incoming_messages)} messages via JavaScript")
                        else:
                            log(f"   ⚠️ JavaScript extraction returned 0 messages")

                            # DEBUG: DOM snapshot to help identify new selectors
                            try:
                                dom_snapshot = page.evaluate("""() => {
                                    const el = document.querySelector('div[data-testid="msg-container"]');
                                    if (el) {
                                        return el.innerHTML.substring(0, 2000);
                                    }
                                    return 'msg-container not found';
                                }""")
                                log(f"   🔍 DOM Snapshot (first 500 chars): {str(dom_snapshot)[:500]}")
                            except:
                                log("   ⚠️ Could not capture DOM snapshot")

                    except Exception as e:
                        log(f"⚠️ Error reading messages: {e}")
                        import traceback
                        log(f"   Traceback: {traceback.format_exc()}")
                    
                    if not incoming_messages:
                        log("⚠️ No incoming messages found, skipping...")
                        # Go back to chat list
                        page.keyboard.press("Escape")
                        page.wait_for_timeout(1000)
                        continue
                    
                    # STEP 6d: Take last incoming message
                    last_message = incoming_messages[-1]
                    log(f"STEP 6d: Latest message: '{last_message[:50]}...'")
                    
                    # STEP 6e: Generate reply via external engine
                    log("STEP 6e: Generating AI reply (categorizing)...")
                    category = classify(contact_name, [last_message])
                    reply = generate_reply(category, contact_name, [last_message])
                    log(f"✅ Reply generated [Category: {category}] ({len(reply)} chars)")
                    
                    # STEP 6f: Find and Activate Message Input Box (Force Focus)
                    log("STEP 6f: Targeting message input box (Force Focus Mode)...")
                    
                    input_box = None
                    try:
                        # User's highly reliable selector
                        selector = 'div[contenteditable="true"][role="textbox"]'
                        
                        # Wait for it to be present in DOM
                        page.wait_for_selector(selector, timeout=5000)
                        
                        # Use JavaScript to force scroll and focus/click
                        page.evaluate(f"""() => {{
                            const el = document.querySelector('{selector}');
                            if (el) {{
                                el.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                                setTimeout(() => {{
                                    el.focus();
                                    el.click();
                                }}, 500);
                            }}
                        }}""")
                        
                        page.wait_for_timeout(1000) # Wait for animation/focus
                        input_box = page.locator(selector).first
                        log("✅ Force Focus applied to input box")
                    except Exception as e:
                        log(f"⚠️ Primary Force Focus failed: {e}. Trying standard fallbacks...")
                    
                    if not input_box or input_box.count() == 0:
                        try:
                            input_box = page.wait_for_selector(
                                "div[data-testid='conversation-compose-box-input']",
                                timeout=5000
                            )
                        except:
                            input_box = None
                    
                    if input_box:
                        input_box.click(force=True)
                        page.wait_for_timeout(300)
                        log("✅ Input box activated")
                    else:
                        log("❌ Could not find or activate input box, skipping...")
                        page.keyboard.press("Escape")
                        page.wait_for_timeout(1000)
                        continue
                    
                    # STEP 6g: Type reply
                    log(f"STEP 6g: Typing reply...")
                    
                    # Human-like typing
                    typing_delay = max(50 // max(len(reply), 1), 30)
                    input_box.type(reply, delay=typing_delay)
                    page.wait_for_timeout(200)
                    
                    # STEP 6h: Send message
                    log("STEP 6h: Sending message...")
                    
                    # Try send button first
                    try:
                        send_btn = page.wait_for_selector(
                            "button[data-testid='send']",
                            timeout=3_000
                        )
                        if send_btn:
                            send_btn.click()
                            log("✅ Sent via button click")
                        else:
                            raise Exception("Send button not found")
                    except:
                        # Fallback: Press Enter
                        page.keyboard.press("Enter")
                        log("✅ Sent via Enter key")
                    
                    page.wait_for_timeout(1000)
                    
                    # STEP 6i: Log the interaction
                    log("=" * 70)
                    
                    # STEP 6k: Log conversation to Obsidian
                    log("STEP 6k: Logging conversation to Obsidian...")
                    category = classify(contact_name, [last_message])
                    hot = is_hot_lead([last_message])
                    sens = is_sensitive([last_message])
                    log_conversation(
                        sender_name=contact_name,
                        category=category,
                        messages=[last_message],
                        reply_sent=reply,
                        hot=hot,
                        sensitive=sens,
                        approved=True
                    )
                    log("✅ Logged to Obsidian")
                    
                    # STEP 6j: Go back to chat list
                    log("STEP 6j: Going back to chat list...")
                    page.keyboard.press("Escape")
                    page.wait_for_timeout(1500)
                    log("✅ Back to chat list")
                    
                    
                except Exception as e:
                    log(f"❌ Error processing chat {contact_name}: {e}")
                    # Try to go back
                    try:
                        page.keyboard.press("Escape")
                        page.wait_for_timeout(1000)
                    except:
                        pass
            
            # ═══════════════════════════════════════════════
            # STEP 7: Wait and repeat
            # ═══════════════════════════════════════════════
            log(f"\n⏳ Waiting {CHECK_INTERVAL} seconds before next scan...")
            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("\n\n⚠️ Agent stopped by user")
    except Exception as e:
        log(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
