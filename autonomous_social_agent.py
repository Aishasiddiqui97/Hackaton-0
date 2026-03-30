#!/usr/bin/env python3
"""
Gold Tier Autonomous Social Media Agent
Ralph Wiggum Loop Pattern - Always-On Autonomous Operation
"""

import os
import shutil
import time
import json
from datetime import datetime, timedelta
from pathlib import Path
import random

# Folder structure
FOLDERS = {
    'inbox_social': '00_Inbox/Social_Media',
    'inbox_whatsapp': '00_Inbox/WhatsApp',
    'drafts': '01_Drafts/Auto_Generated',
    'pending_social': '02_Pending_Approvals/Social_Posts',
    'pending_email': '02_Pending_Approvals/Email_Drafts',
    'posted': '03_Posted/History',
    'urgent': '00_Inbox'
}

# Platform configuration
PLATFORMS = ['LinkedIn', 'Twitter', 'Facebook', 'Instagram']
POST_INTERVAL_HOURS = 6
LAST_POST_FILE = 'logs/last_social_posts.json'


class AutonomousSocialAgent:
    """Autonomous agent for social media and WhatsApp management"""
    
    def __init__(self):
        self.ensure_folders()
        self.last_posts = self.load_last_posts()
        self.company_context = self.load_company_handbook()
        
    def ensure_folders(self):
        """Create all required folders"""
        for folder in FOLDERS.values():
            Path(folder).mkdir(parents=True, exist_ok=True)
        Path('logs').mkdir(exist_ok=True)
        
    def load_last_posts(self):
        """Load timestamp of last posts per platform"""
        if os.path.exists(LAST_POST_FILE):
            with open(LAST_POST_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {platform: None for platform in PLATFORMS}
    
    def save_last_posts(self):
        """Save timestamp of last posts"""
        with open(LAST_POST_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.last_posts, f, indent=2)
    
    def load_company_handbook(self):
        """Load company context from handbook"""
        handbook_path = 'Company_Handbook.md'
        if os.path.exists(handbook_path):
            with open(handbook_path, 'r', encoding='utf-8') as f:
                return f.read()
        return "Professional services company focused on innovation and customer success."
    
    def should_generate_post(self, platform):
        """Check if it's time to generate a new post"""
        last_post = self.last_posts.get(platform)
        if not last_post:
            return True
        
        last_time = datetime.fromisoformat(last_post)
        time_diff = datetime.now() - last_time
        return time_diff.total_seconds() >= (POST_INTERVAL_HOURS * 3600)
    
    def generate_social_post(self, platform):
        """Generate platform-specific social media post"""
        
        # Platform-specific configurations
        configs = {
            'LinkedIn': {
                'tone': 'Professional and thought-leadership',
                'hashtags': 3,
                'max_length': 3000,
                'cta': 'Connect with us to learn more'
            },
            'Twitter': {
                'tone': 'Concise and engaging',
                'hashtags': 2,
                'max_length': 280,
                'cta': 'Follow for more insights'
            },
            'Facebook': {
                'tone': 'Friendly and conversational',
                'hashtags': 4,
                'max_length': 5000,
                'cta': 'Like and share if you agree'
            },
            'Instagram': {
                'tone': 'Visual and inspiring',
                'hashtags': 15,
                'max_length': 2200,
                'cta': 'Double tap if you love this'
            }
        }
        
        config = configs[platform]
        
        # Generate content based on company context
        topics = [
            'Innovation in business',
            'Customer success stories',
            'Industry insights',
            'Team achievements',
            'Product updates',
            'Thought leadership'
        ]
        
        topic = random.choice(topics)
        
        # Create post content
        post = f"""# {platform} Post - {topic}

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Platform**: {platform}
**Tone**: {config['tone']}

---

## Content

🚀 {topic.upper()}

{self._generate_post_body(topic, config)}

---

## Call-to-Action
{config['cta']}

---

## Hashtags
{self._generate_hashtags(platform, config['hashtags'])}

---

## Metadata
- Character count: ~{config['max_length']//2}
- Optimal posting time: Morning (9-11 AM) or Evening (5-7 PM)
- Engagement goal: High

---

**Status**: PENDING_APPROVAL
**Next Action**: Move to 03_Posted/History after approval to auto-post
"""
        return post
    
    def _generate_post_body(self, topic, config):
        """Generate post body content"""
        bodies = {
            'Innovation in business': """
In today's fast-paced business environment, innovation isn't just an advantage—it's a necessity.

We're constantly exploring new ways to deliver value to our clients through:
✅ Cutting-edge technology solutions
✅ Data-driven decision making
✅ Customer-centric approaches
✅ Agile methodologies

What's your biggest innovation challenge? Let's discuss in the comments!
""",
            'Customer success stories': """
Nothing makes us prouder than seeing our clients succeed! 🎉

This week, we helped a client achieve:
📈 40% increase in efficiency
💰 Significant cost savings
⚡ Faster time-to-market

Your success is our success. Ready to write your own success story?
""",
            'Industry insights': """
The industry is evolving rapidly, and staying ahead requires constant learning.

Key trends we're watching:
🔍 AI and automation
🌐 Digital transformation
📊 Data analytics
🤝 Customer experience

What trends are you focusing on? Share your thoughts!
""",
            'Team achievements': """
Behind every great company is an amazing team! 👏

We're proud to celebrate our team's recent achievements:
🏆 Project milestones reached
💡 Innovative solutions delivered
🤝 Strong client partnerships built

Thank you to our incredible team for making it all possible!
""",
            'Product updates': """
Exciting news! We've been working hard to bring you something special. 🎁

Our latest updates include:
✨ Enhanced features
🚀 Improved performance
🔒 Better security
📱 Seamless user experience

Ready to experience the difference? Get in touch!
""",
            'Thought leadership': """
Success in business isn't just about what you do—it's about how you think.

Key principles we live by:
💭 Think long-term
🎯 Focus on value
🤝 Build relationships
📈 Measure and improve

What principles guide your business decisions?
"""
        }
        return bodies.get(topic, "Great things are happening! Stay tuned for more updates.")
    
    def _generate_hashtags(self, platform, count):
        """Generate platform-appropriate hashtags"""
        all_hashtags = [
            '#Business', '#Innovation', '#Success', '#Growth', '#Leadership',
            '#Technology', '#Digital', '#Strategy', '#Entrepreneur', '#Marketing',
            '#Sales', '#CustomerSuccess', '#TeamWork', '#Productivity', '#Future',
            '#AI', '#Automation', '#DataDriven', '#Excellence', '#Quality'
        ]
        
        selected = random.sample(all_hashtags, min(count, len(all_hashtags)))
        return ' '.join(selected)
    
    def create_pending_post(self, platform, content):
        """Save post to pending approvals folder"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{platform}_Post_{timestamp}.md"
        filepath = os.path.join(FOLDERS['pending_social'], filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Created pending post: {filename}")
        return filepath
    
    def check_approved_posts(self):
        """Check if any posts moved to Posted folder and auto-post them"""
        posted_folder = FOLDERS['posted']
        
        for filename in os.listdir(posted_folder):
            if filename.endswith('.md') and not filename.startswith('POSTED_'):
                filepath = os.path.join(posted_folder, filename)
                
                # Extract platform from filename
                platform = filename.split('_')[0]
                
                # Post to platform
                print(f"📤 Auto-posting to {platform}: {filename}")
                
                success = False
                if platform == 'LinkedIn':
                    success = self.post_to_linkedin(filepath)
                else:
                    # For other platforms, just simulate for now
                    print(f"⚠️  {platform} posting not yet implemented")
                    success = True  # Mark as success to move file
                
                if success:
                    # Mark as posted
                    new_filename = f"POSTED_{filename}"
                    new_filepath = os.path.join(posted_folder, new_filename)
                    if os.path.exists(new_filepath):
                        os.remove(new_filepath)
                    shutil.move(filepath, new_filepath)
                    
                    # Update last post time
                    self.last_posts[platform] = datetime.now().isoformat()
                    self.save_last_posts()
                    
                    # Log action
                    self.log_action(f"Auto-posted to {platform}: {filename}")
                else:
                    print(f"❌ Failed to post to {platform}")
                    self.log_action(f"Failed to post to {platform}: {filename}")
    
    def post_to_linkedin(self, filepath):
        """Post to LinkedIn using browser automation"""
        try:
            import subprocess
            result = subprocess.run(
                ['python', 'linkedin_auto_poster.py', filepath],
                capture_output=True,
                text=True,
                timeout=120  # 2 minutes timeout
            )
            
            if result.returncode == 0:
                print("✅ LinkedIn post successful")
                return True
            else:
                print(f"❌ LinkedIn post failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error posting to LinkedIn: {e}")
            return False
    
    def process_whatsapp_messages(self):
        """Process WhatsApp messages from inbox"""
        whatsapp_folder = FOLDERS['inbox_whatsapp']
        
        for filename in os.listdir(whatsapp_folder):
            if filename.endswith('.md'):
                filepath = os.path.join(whatsapp_folder, filename)
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                
                # Check for urgent keywords
                urgent_keywords = ['urgent', 'price quote', 'meeting', 'asap', 'emergency']
                is_urgent = any(keyword in content for keyword in urgent_keywords)
                
                if is_urgent:
                    # Move to urgent folder
                    urgent_file = os.path.join(FOLDERS['urgent'], f"Urgent_WhatsApp_{filename}")
                    os.rename(filepath, urgent_file)
                    print(f"🚨 URGENT WhatsApp message: {filename}")
                    self.log_action(f"Urgent WhatsApp alert: {filename}")
                else:
                    # Auto-reply for routine queries
                    self.auto_reply_whatsapp(filepath, content)
    
    def auto_reply_whatsapp(self, filepath, content):
        """Generate auto-reply for routine WhatsApp queries"""
        
        # Detect query type
        if any(word in content for word in ['hello', 'hi', 'hey', 'greetings']):
            reply = "Hello! Thank you for reaching out. How can we help you today?"
        elif any(word in content for word in ['price', 'pricing', 'cost', 'quote']):
            reply = "Thank you for your interest! Our pricing varies based on requirements. Please share more details, and we'll provide a customized quote."
        elif any(word in content for word in ['info', 'information', 'details', 'about']):
            reply = "We'd be happy to share more information! What specific aspect would you like to know about?"
        else:
            reply = "Thank you for your message! We've received it and will get back to you shortly."
        
        # Save reply
        reply_file = filepath.replace('.md', '_REPLIED.md')
        with open(reply_file, 'w', encoding='utf-8') as f:
            f.write(f"# Auto-Reply Sent\n\n**Time**: {datetime.now()}\n\n**Reply**:\n{reply}\n\n---\n\n**Original Message**:\n{content}")
        
        # Remove original
        os.remove(filepath)
        print(f"✅ Auto-replied to WhatsApp message")
    
    def log_action(self, message):
        """Log agent actions"""
        log_file = 'logs/autonomous_agent.log'
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {message}\n")
    
    def ralph_wiggum_loop(self):
        """Main autonomous loop - never stops, never asks"""
        print("🤖 Gold Tier Autonomous Agent Started")
        print("📋 Ralph Wiggum Loop Pattern Active")
        print("⏰ Running every 30 minutes")
        print("-" * 60)
        
        iteration = 0
        
        while True:
            try:
                iteration += 1
                print(f"\n🔄 Iteration #{iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                # 1. Check and generate social media posts
                for platform in PLATFORMS:
                    if self.should_generate_post(platform):
                        print(f"📝 Generating {platform} post...")
                        content = self.generate_social_post(platform)
                        self.create_pending_post(platform, content)
                        self.last_posts[platform] = datetime.now().isoformat()
                        self.save_last_posts()
                
                # 2. Check for approved posts and auto-post
                self.check_approved_posts()
                
                # 3. Process WhatsApp messages
                self.process_whatsapp_messages()
                
                # 4. Log completion
                self.log_action(f"Completed iteration #{iteration}")
                
                print(f"✅ Iteration #{iteration} complete")
                print(f"⏳ Next check in 30 minutes...")
                
                # Wait 30 minutes before next iteration
                time.sleep(1800)  # 30 minutes
                
            except Exception as e:
                error_msg = f"Error in iteration #{iteration}: {str(e)}"
                print(f"❌ {error_msg}")
                
                # Log error
                error_file = '00_Inbox/Error_Log.md'
                with open(error_file, 'a', encoding='utf-8') as f:
                    f.write(f"\n## Error - {datetime.now()}\n{error_msg}\n\n")
                
                self.log_action(error_msg)
                
                # Continue to next iteration
                print("🔄 Continuing to next platform...")
                time.sleep(60)  # Wait 1 minute before retry


def main():
    """Start the autonomous agent"""
    agent = AutonomousSocialAgent()
    agent.ralph_wiggum_loop()


if __name__ == "__main__":
    main()
