#!/usr/bin/env node
/**
 * Twitter API MCP Server - No Browser Needed!
 * Uses Twitter API v2 with OAuth 1.0a (User Context)
 */

const express = require('express');
const { TwitterApi } = require('twitter-api-v2');
require('dotenv').config();

const app = express();
app.use(express.json());

const PORT = 3007; // Different port from browser version

// API credentials from .env (OAuth 1.0a)
const API_KEY = process.env.TWITTER_API_KEY;
const API_SECRET = process.env.TWITTER_API_SECRET;
const ACCESS_TOKEN = process.env.TWITTER_ACCESS_TOKEN;
const ACCESS_TOKEN_SECRET = process.env.TWITTER_ACCESS_TOKEN_SECRET;

// Initialize Twitter client with OAuth 1.0a
const twitterClient = new TwitterApi({
    appKey: API_KEY,
    appSecret: API_SECRET,
    accessToken: ACCESS_TOKEN,
    accessSecret: ACCESS_TOKEN_SECRET,
});

// Simple logging
function log(message) {
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] ${message}`);
}

// Health check
app.get('/health', (req, res) => {
    res.json({
        status: 'running',
        port: PORT,
        method: 'Twitter API v2 (OAuth 1.0a)',
        authenticated: !!(API_KEY && API_SECRET && ACCESS_TOKEN && ACCESS_TOKEN_SECRET)
    });
});

// Post tweet
app.post('/post_tweet', async (req, res) => {
    try {
        const { text } = req.body;

        if (!text) {
            return res.status(400).json({ success: false, error: 'Tweet text required' });
        }

        if (!API_KEY || !ACCESS_TOKEN) {
            return res.status(401).json({ success: false, error: 'Twitter API credentials not configured' });
        }

        log(`Posting tweet: ${text.substring(0, 50)}...`);

        const tweet = await twitterClient.v2.tweet(text);

        log(`Tweet posted successfully! ID: ${tweet.data.id}`);

        res.json({
            success: true,
            tweetId: tweet.data.id,
            tweetUrl: `https://x.com/i/web/status/${tweet.data.id}`,
            message: 'Tweet posted successfully via API'
        });

    } catch (error) {
        log(`Error posting tweet: ${error.message}`);
        res.status(500).json({ success: false, error: error.message });
    }
});

// Get user info
app.get('/me', async (req, res) => {
    try {
        const user = await twitterClient.v2.me({
            'user.fields': ['created_at', 'description', 'public_metrics']
        });

        res.json({ success: true, user: user.data });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// Get mentions
app.get('/mentions', async (req, res) => {
    try {
        // Get current user
        const me = await twitterClient.v2.me();
        const userId = me.data.id;

        // Get mentions
        const mentions = await twitterClient.v2.userMentionTimeline(userId, {
            max_results: 10
        });

        res.json({
            success: true,
            mentionsCount: mentions.data.data ? mentions.data.data.length : 0,
            mentions: mentions.data.data || []
        });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// Start server
app.listen(PORT, () => {
    log(`Twitter API MCP Server running on port ${PORT}`);
    console.log(`\n🚀 Twitter API Server Started`);
    console.log(`📡 Listening on: http://localhost:${PORT}`);
    console.log(`🔑 Method: Twitter API v2 (No browser needed!)`);
    console.log(`✅ No login issues`);
    console.log(`✅ No automation detection`);
    console.log(`✅ Fast and reliable\n`);

    // Test credentials on startup
    if (API_KEY && ACCESS_TOKEN) {
        twitterClient.v2.me()
            .then(response => {
                console.log(`✅ Authenticated as: @${response.data.username}`);
                console.log(`   Name: ${response.data.name}`);
                console.log(`   ID: ${response.data.id}`);
                console.log(`✨ Server ready for requests\n`);
            })
            .catch(error => {
                console.log(`⚠️  API credentials might be invalid: ${error.message}`);
                console.log(`   Check your .env file (need OAuth 1.0a credentials)\n`);
            });
    } else {
        console.log(`⚠️  Twitter OAuth 1.0a credentials not found in .env`);
        console.log(`   Need: TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET`);
        console.log(`   Server running but API calls will fail\n`);
    }
});
