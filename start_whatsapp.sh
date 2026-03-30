#!/bin/bash
# Quick launcher for WhatsApp Agent - All modes (Linux/Mac/Git Bash)

show_menu() {
    clear
    echo "========================================"
    echo "WhatsApp Autonomous Agent - Launcher"
    echo "========================================"
    echo ""
    echo "Select Mode:"
    echo ""
    echo "1. Test Input Box (Recommended First)"
    echo "2. First Time Setup (QR Scan)"
    echo "3. Run Once (Single Scan)"
    echo "4. Autonomous Mode (Continuous)"
    echo "5. Loop Mode (Custom Interval)"
    echo "6. Force GPU Mode (If input box fails)"
    echo "7. Clear Session and Restart"
    echo "8. View Logs"
    echo "9. Exit"
    echo ""
}

while true; do
    show_menu
    read -p "Enter choice (1-9): " choice

    case $choice in
        1)
            echo ""
            echo "Testing input box rendering..."
            python test_input_box.py
            read -p "Press Enter to continue..."
            ;;
        2)
            echo ""
            echo "First time setup - QR scan required"
            echo "Browser will open, please scan QR code"
            python whatsapp_agent.py --headful
            read -p "Press Enter to continue..."
            ;;
        3)
            echo ""
            echo "Running single scan..."
            python whatsapp_agent.py --headful
            read -p "Press Enter to continue..."
            ;;
        4)
            echo ""
            echo "Starting autonomous mode (continuous)..."
            echo "Press Ctrl+C to stop"
            python autonomous_whatsapp_agent.py
            read -p "Press Enter to continue..."
            ;;
        5)
            echo ""
            read -p "Enter scan interval in seconds (default 120): " interval
            interval=${interval:-120}
            echo "Starting loop mode (scanning every $interval seconds)..."
            echo "Press Ctrl+C to stop"
            python whatsapp_agent.py --loop --interval $interval --headful
            read -p "Press Enter to continue..."
            ;;
        6)
            echo ""
            echo "Starting with FORCE GPU rendering..."
            python whatsapp_agent_force_gpu.py
            read -p "Press Enter to continue..."
            ;;
        7)
            echo ""
            echo "WARNING: This will delete your WhatsApp session"
            echo "You will need to scan QR code again"
            read -p "Are you sure? (y/n): " confirm
            if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
                rm -rf whatsapp_session
                echo "Session cleared!"
                echo "Run option 2 to setup again"
            else
                echo "Cancelled"
            fi
            read -p "Press Enter to continue..."
            ;;
        8)
            echo ""
            echo "Recent logs:"
            echo "========================================"
            if [ -f logs/whatsapp_agent.log ]; then
                tail -n 30 logs/whatsapp_agent.log
            else
                echo "No logs found yet"
            fi
            echo "========================================"
            read -p "Press Enter to continue..."
            ;;
        9)
            echo ""
            echo "Goodbye!"
            exit 0
            ;;
        *)
            echo "Invalid choice"
            sleep 2
            ;;
    esac
done
