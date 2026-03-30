#!/usr/bin/env node
/**
 * Twitter/X MCP Server - Gold Tier 2026
 * Ultimate Stealth + Robust Login Fix + Full Autonomous Integration
 * Port: 3006
 */

require('dotenv').config();
const express = require('express');
const { chromium } = require('playwright-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const fs = require('fs').promises;
const path = require('path');
const speakeasy = require('speakeasy');

// Add stealth plugin
chromium.use(StealthPlugin());

const app = express();
app.use(express.json());

const PORT = 3006;
const SESSION_DIR = path.join(__dirname, '../sessions/twitter');
const STORAGE_STATE_PATH = path.join(SESSION_DIR, 'storageState.json');
const VAULT_DIR = path.join(__dirname, '../AI_Employee_Vault');
const LOGS_DIR = path.join(VAULT_DIR, 'Logs');
const NEEDS_ACTION_DIR = path.join(VAULT_DIR, 'Needs_Action');

// Ensure directories exist
async function ensureDirectories() {
    await fs.mkdir(SESSION_DIR, { recursive: true });
    await fs.mkdir(LOGS_DIR, { recursive: true });
    await fs.mkdir(NEEDS_ACTION_DIR, { recursive: true });
}

// Logging utility
async function log(level, message) {
    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] [TWITTER_MCP] [${level}] ${message}`;
    console.log(logMessage);

    const logPath = path.join(LOGS_DIR, 'Twitter_Log.md');
    const logEntry = `\n---\n**${timestamp}** - ${level}: ${message}\n`;
    await fs.appendFile(logPath, logEntry).catch(err => console.error('Log write failed:', err));
}

class TwitterAgent {
    constructor() {
        this.browser = null;
        this.context = null;
        this.page = null;
        this.isLoggedIn = false;
    }

    async initialize() {
        try {
            log('INFO', 'Initializing stealth browser with persistent session');

            this.browser = await chromium.launch({
                headless: false, // Must be false for first run/login
                slowMo: 80,
                args: [
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-infobars',
                    '--start-maximized',
                    '--disable-dev-shm-usage'
                ]
            });

            // Load existing session if available
            let storageState = null;
            try {
                await fs.access(STORAGE_STATE_PATH);
                storageState = STORAGE_STATE_PATH;
                log('INFO', 'Loading existing session from storageState.json');
            } catch (e) {
                log('INFO', 'No existing session found. Manual login required for first run.');
            }

            this.context = await this.browser.newContext({
                storageState: storageState,
                viewport: { width: 1280, height: 720 },
                deviceScaleFactor: 1,
                userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
                locale: 'en-US',
                timezoneId: 'America/New_York'
            });

            this.page = await this.context.newPage();

            // Extra Stealth: Hide automation
            await this.page.addInitScript(() => {
                Object.defineProperty(navigator, 'webdriver', { get: () => false });
                window.chrome = { runtime: {} };
                Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
                Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            });

            // Extra Stealth: Override permissions and webgl
            await this.page.addInitScript(() => {
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
            });

            log('INFO', 'Browser initialized successfully');
            
            // Auto-check if logged in
            if (storageState) {
                this.isLoggedIn = await this.checkSession();
            }
            
            return true;
        } catch (error) {
            log('ERROR', `Initialization failed: ${error.message}`);
            return false;
        }
    }

    async login(username, password, twoFactorSecret = null) {
        try {
            log('INFO', `Starting robust login for user: ${username}`);
            await this.page.goto('https://x.com/i/flow/login', { waitUntil: 'networkidle', timeout: 60000 });
            await this.page.waitForTimeout(3000);

            // 1. Enter Username
            log('INFO', 'Entering username');
            const cleanUsername = username.startsWith('@') ? username.substring(1) : username;
            
            const userSelector = 'input[autocomplete="username"]';
            const userSelectorAlt = 'input[name="text"]';
            await this.page.waitForSelector(`${userSelector}, ${userSelectorAlt}`, { timeout: 30000 });
            const actualUserSelector = await this.page.locator(userSelectorAlt).isVisible() ? userSelectorAlt : userSelector;
            
            await this.page.click(actualUserSelector);
            await this.page.waitForTimeout(1000);
            await this.page.type(actualUserSelector, cleanUsername, { delay: 300 }); 
            await this.page.waitForTimeout(2000);
            
            log('INFO', 'Pressing Enter...');
            await this.page.keyboard.press('Enter');
            
            // 2. Wait for Password field
            log('INFO', 'Waiting for password screen (handling potential loading spinner)...');
            const passSelector = 'input[name="password"]';
            const passSelectorAlt = 'input[type="password"]';
            
            try {
                await this.page.waitForSelector(`${passSelector}, ${passSelectorAlt}`, { timeout: 30000 });
                log('INFO', 'Entering password');
                const actualPassSelector = await this.page.locator(passSelector).isVisible() ? passSelector : passSelectorAlt;
                await this.page.fill(actualPassSelector, password);
                await this.page.keyboard.press('Enter');
                await this.page.waitForTimeout(5000);
            } catch (e) {
                log('WARN', 'Autonomous login stuck on loading spinner or verification. Please handle manually in the browser window.');
                const screenshotPath = path.join(LOGS_DIR, `Login_Stuck_${Date.now()}.png`);
                await this.page.screenshot({ path: screenshotPath });
                log('IMPORTANT', 'Waiting for you to finish login manually in the window...');
                await this.page.waitForURL('**/home', { timeout: 300000 });
            }

            // 3. Verify landing
            if (this.page.url().includes('/home') || await this.page.locator('nav').isVisible()) {
                this.isLoggedIn = true;
                log('SUCCESS', 'Login successful - saving session state');
                await this.context.storageState({ path: STORAGE_STATE_PATH });
                return { success: true };
            }
            throw new Error('Failed to reach home page');
        } catch (error) {
            log('ERROR', `Login failed: ${error.message}`);
            return { success: false, error: error.message };
        }
    }

    async checkSession() {
        try {
            await this.page.goto('https://x.com/home', { waitUntil: 'networkidle', timeout: 15000 });
            if (this.page.url().includes('/home')) {
                log('INFO', 'Session active and valid');
                return true;
            }
            return false;
        } catch (e) {
            return false;
        }
    }

    async postTweet(text) {
        try {
            if (!this.isLoggedIn) throw new Error('Not logged in');
            log('INFO', `Posting tweet: ${text.substring(0, 50)}...`);

            await this.page.goto('https://x.com/compose/post', { waitUntil: 'networkidle' });
            await this.page.waitForTimeout(2000);

            const editorSelector = '[data-testid="tweetTextarea_0"]';
            await this.page.waitForSelector(editorSelector);
            await this.page.click(editorSelector);
            await this.page.fill(editorSelector, text);
            await this.page.waitForTimeout(1000);

            await this.page.click('[data-testid="tweetButton"]');
            await this.page.waitForTimeout(5000);

            log('SUCCESS', 'Tweet posted successfully');
            await this.generateSummary(`Posted Tweet: ${text}`);
            return { success: true };
        } catch (error) {
            log('ERROR', `Post failed: ${error.message}`);
            return { success: false, error: error.message };
        }
    }

    async getMentionsSummary() {
        try {
            if (!this.isLoggedIn) throw new Error('Not logged in');
            log('INFO', 'Scraping mentions summary');

            await this.page.goto('https://x.com/notifications/mentions', { waitUntil: 'networkidle' });
            await this.page.waitForTimeout(3000);

            const mentionCount = await this.page.locator('article').count();
            const summaryText = `Found ${mentionCount} current mentions in notifications.`;
            
            log('SUCCESS', summaryText);
            await this.generateSummary(`Mentions Check: ${summaryText}`);
            return { success: true, count: mentionCount };
        } catch (error) {
            log('ERROR', `Mentions check failed: ${error.message}`);
            return { success: false, error: error.message };
        }
    }

    async generateSummary(details) {
        const timestamp = new Date().toISOString();
        const summary = `
# 🐦 Twitter Action Summary
Date: ${timestamp}
Action: ${details}
Status: Completed ✅
---
Generated by Twitter MCP Server
`;
        const summaryPath = path.join(NEEDS_ACTION_DIR, `Twitter_Summary_${Date.now()}.md`);
        await fs.writeFile(summaryPath, summary);
        log('INFO', `Summary generated: ${summaryPath}`);
    }

    async close() {
        if (this.browser) await this.browser.close();
    }
}

let agent = null;

// API Endpoints
app.post('/login', async (req, res) => {
    const { username, password, twoFactorSecret } = req.body;
    if (!agent) {
        agent = new TwitterAgent();
        await agent.initialize();
    }
    const result = await agent.login(username || process.env.TWITTER_USERNAME, password || process.env.TWITTER_PASSWORD, twoFactorSecret || process.env.TWITTER_2_FA_SECRET);
    res.json(result);
});

app.post('/post_tweet', async (req, res) => {
    if (!agent || !agent.isLoggedIn) return res.status(401).json({ success: false, error: 'Not logged in' });
    const result = await agent.postTweet(req.body.text);
    res.json(result);
});

app.get('/mentions', async (req, res) => {
    if (!agent || !agent.isLoggedIn) return res.status(401).json({ success: false, error: 'Not logged in' });
    const result = await agent.getMentionsSummary();
    res.json(result);
});

app.get('/health', (req, res) => {
    res.json({
        status: 'running',
        loggedIn: agent ? agent.isLoggedIn : false,
        timestamp: new Date().toISOString()
    });
});

async function start() {
    await ensureDirectories();
    app.listen(PORT, async () => {
        log('INFO', `Twitter MCP Server running on port ${PORT}`);
        // Optional auto-init if credentials exist
        if (process.env.TWITTER_USERNAME && process.env.TWITTER_PASSWORD) {
            log('INFO', 'Auto-initializing agent...');
            agent = new TwitterAgent();
            await agent.initialize();
            if (agent.isLoggedIn) {
                log('SUCCESS', 'Auto-login successful using saved session');
            } else {
                log('INFO', 'Session not found or expired. Triggering login flow...');
                await agent.login(process.env.TWITTER_USERNAME, process.env.TWITTER_PASSWORD, process.env.TWITTER_2FA_SECRET);
            }
        }
    });
}

start();
