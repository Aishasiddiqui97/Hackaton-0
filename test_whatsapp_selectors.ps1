# PowerShell script to test WhatsApp selectors
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Testing Fixed WhatsApp Selectors" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

try {
    & python test_whatsapp_selectors.py
    Write-Host ""
    Write-Host "Test completed!" -ForegroundColor Green
} catch {
    Write-Host ""
    Write-Host "Test failed: $_" -ForegroundColor Red
    exit 1
}
