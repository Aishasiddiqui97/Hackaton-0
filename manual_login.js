#!/usr/bin/env node
/**
 * Manual Login Helper
 * Opens browser, lets you login manually, saves session
 */

const { chromium } = require('playwright-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const path = require('path');

chromium.use(StealthPlugin());

const SESSION_DIR = path.join(__dirname, 'sessions/twitter');

async function manualLogin() {
    console.log('========================================');
    console.log('  Twitter Manual Login Helper');
    console.log('========================================');
    console.log();
    console.log('This will:');
    console.log('1. Open Chrome browser');
    console.log('2. Go to Twitter login page');
    console.log('3. Let YOU login manually');
    console.log('4. Save the session');
    console.log('5. Future logins will be automatic!');
    console.log();
    console.log('========================================');
    console.log();

    try {
        console.log('🌐 Opening browser...');
        const browser = await chromium.launch({
            headless: false,
            args: ['--start-maximized']
        });

        const context = await browser.newContext({
            userDataDir: SESSION_DIR,
            viewport: { width: 1920, height: 1080 },
            userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        });

        const page = await context.newPage();

        console.log('✅ Browser opened');
        console.log();
        console.log('📍 Navigating to Twitter login...');
        await page.goto('https://x.com/i/flow/login');
        await page.waitForTimeout(3000);

        console.log();
        console.log('========================================');
        console.log('  YOUR TURN!');
        console.log('========================================');
        console.log();
        console.log('In the browser window:');
        console.log('1. Enter your username: @AISHA726035158');
        console.log('2. Click Next');
        console.log('3. Enter your password: Aisha97@');
        console.log('4. Click Log in');
        console.log('5. Complete any 2FA or verification');
        console.log('6. Wait until you see your Twitter home page');
        console.log();
        console.log('⏳ Waiting for you to login...');
        console.log('   (I\'ll detect when you reach the home page)');
        console.log();

        // Wait for user to login (check every 5 seconds)
        let loggedIn = false;
        let attempts = 0;
        const maxAttempts = 60; // 5 minutes

        while (!loggedIn && attempts < maxAttempts) {
            await page.waitForTimeout(5000);
            attempts++;

            const currentUrl = page.url();

            if (currentUrl.includes('/home')) {
                // Double-check by looking for compose button
                const composeButton = await page.locator('[data-testid="SideNav_NewTweet_Button"]').count();
                if (composeButton > 0) {
                    loggedIn = true;
                    break;
                }
            }

            // Show progress
            if (attempts % 6 === 0) {
                console.log(`   Still waiting... (${attempts * 5} seconds elapsed)`);
            }
        }

        if (loggedIn) {
            console.log();
            console.log('========================================');
            console.log('  ✅ SUCCESS!');
            console.log('========================================');
            console.log();
            console.log('✅ Login detected!');
            console.log('💾 Session saved to:', SESSION_DIR);
            console.log();
            console.log('Next time you start the server:');
            console.log('  - Login will be INSTANT');
            console.log('  - No browser needed');
            console.log('  - Fully automatic!');
            console.log();
            console.log('Closing browser in 5 seconds...');
            await page.waitForTimeout(5000);
        } else {
            console.log();
            console.log('⚠️  Timeout - Login not detected');
            console.log('   But session might still be saved!');
            console.log('   Try starting the server and see if it works.');
            console.log();
        }

        await browser.close();

        console.log();
        console.log('========================================');
        console.log('  NEXT STEPS');
        console.log('========================================');
        console.log();
        console.log('1. Start the server:');
        console.log('   .\\start_twitter_autonomous.bat');
        console.log();
        console.log('2. Test it:');
        console.log('   python test_autonomous_login.py');
        console.log();
        console.log('Login should now be automatic! 🎉');
        console.log();

    } catch (error) {
        console.error('❌ Error:', error.message);
        console.log();
        console.log('Try again or check:');
        console.log('  - Playwright installed: npx playwright install chromium');
        console.log('  - Internet connection working');
    }
}

manualLogin();
