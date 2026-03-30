#!/usr/bin/env python3
"""
Instagram HITL Approval Tool - Gold Tier
CLI tool for reviewing and approving Instagram posts and comment replies
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Vault paths
VAULT_ROOT = Path(__file__).parent / "AI_Employee_Vault"
PENDING_DIR = VAULT_ROOT / "Pending_Approval" / "social"
APPROVED_DIR = VAULT_ROOT / "Approved"
REJECTED_DIR = VAULT_ROOT / "Rejected"
DONE_DIR = VAULT_ROOT / "Done"
LOGS_DIR = VAULT_ROOT / "Logs"

# Create directories
for dir_path in [PENDING_DIR, APPROVED_DIR, REJECTED_DIR, DONE_DIR, LOGS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)


class InstagramApprovalTool:
    """CLI tool for approving Instagram content."""

    def __init__(self):
        self.pending_dir = PENDING_DIR
        self.approved_dir = APPROVED_DIR
        self.rejected_dir = REJECTED_DIR
        self.done_dir = DONE_DIR

    def _parse_frontmatter(self, content: str) -> Dict[str, Any]:
        """Parse YAML frontmatter from markdown file."""
        if not content.startswith('---'):
            return {}

        parts = content.split('---', 2)
        if len(parts) < 3:
            return {}

        frontmatter = parts[1].strip()
        metadata = {}

        for line in frontmatter.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip()

        return metadata

    def _get_pending_items(self) -> List[Dict[str, Any]]:
        """Get all pending Instagram items."""
        items = []

        # Check pending approval directory
        if self.pending_dir.exists():
            for file_path in self.pending_dir.glob("IG_*.md"):
                try:
                    content = file_path.read_text(encoding='utf-8')
                    metadata = self._parse_frontmatter(content)

                    items.append({
                        'filename': file_path.name,
                        'filepath': file_path,
                        'type': metadata.get('type', 'unknown'),
                        'status': metadata.get('status', 'pending'),
                        'content': content,
                        'metadata': metadata
                    })
                except Exception as e:
                    print(f"Warning: Could not read {file_path.name}: {e}")

        # Also check Needs_Action for comment replies
        needs_action_dir = VAULT_ROOT / "Needs_Action"
        if needs_action_dir.exists():
            for file_path in needs_action_dir.glob("INSTAGRAM_comment_*.md"):
                try:
                    content = file_path.read_text(encoding='utf-8')
                    metadata = self._parse_frontmatter(content)

                    if metadata.get('status') == 'pending':
                        items.append({
                            'filename': file_path.name,
                            'filepath': file_path,
                            'type': 'instagram_comment_reply',
                            'status': 'pending',
                            'content': content,
                            'metadata': metadata
                        })
                except Exception as e:
                    print(f"Warning: Could not read {file_path.name}: {e}")

        return items

    def list_pending(self):
        """List all pending Instagram approvals."""
        items = self._get_pending_items()

        if not items:
            print("✅ No pending Instagram approvals")
            return

        print(f"\n📋 Pending Instagram Approvals ({len(items)})\n")
        print("=" * 80)

        for i, item in enumerate(items, 1):
            print(f"\n{i}. {item['filename']}")
            print(f"   Type: {item['type']}")

            if item['type'] == 'instagram_draft':
                # Show draft preview
                metadata = item['metadata']
                print(f"   Scheduled: {metadata.get('scheduled_time', 'Not set')}")
                print(f"   Image needed: {metadata.get('image_needed', 'Unknown')}")

                # Extract caption
                content = item['content']
                if '## Caption' in content:
                    caption_section = content.split('## Caption')[1].split('##')[0].strip()
                    preview = caption_section[:100] + "..." if len(caption_section) > 100 else caption_section
                    print(f"   Caption: {preview}")

            elif item['type'] == 'instagram_comment_reply':
                # Show comment reply preview
                metadata = item['metadata']
                print(f"   From: @{metadata.get('from', 'Unknown')}")
                print(f"   Keyword: {metadata.get('keyword_matched', 'N/A')}")

                # Extract suggested reply
                content = item['content']
                if '## Suggested Reply' in content:
                    reply_section = content.split('## Suggested Reply')[1].split('##')[0].strip()
                    print(f"   Reply: {reply_section[:80]}")

        print("\n" + "=" * 80)
        print(f"\nTo approve: python approve_instagram.py --approve <filename>")
        print(f"To reject:  python approve_instagram.py --reject <filename>")

    def show_preview(self, filename: str) -> Dict[str, Any]:
        """Show full preview of an item."""
        items = self._get_pending_items()
        item = next((i for i in items if i['filename'] == filename), None)

        if not item:
            print(f"❌ Error: {filename} not found in pending approvals")
            return None

        print("\n" + "=" * 80)
        print(f"📄 Preview: {filename}")
        print("=" * 80)

        content = item['content']

        # Remove frontmatter for display
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                content = parts[2].strip()

        print(content)
        print("=" * 80)

        return item

    def approve(self, filename: str):
        """Approve an Instagram item."""
        item = self.show_preview(filename)

        if not item:
            return

        # Ask for confirmation
        print("\n⚠️  This will publish to Instagram (or queue for posting)")
        confirm = input("Approve and publish? (yes/no): ").strip().lower()

        if confirm != 'yes':
            print("❌ Approval cancelled")
            return

        item_type = item['type']

        if item_type == 'instagram_draft':
            self._approve_draft(item)
        elif item_type == 'instagram_comment_reply':
            self._approve_comment_reply(item)
        else:
            print(f"❌ Unknown item type: {item_type}")

    def _approve_draft(self, item: Dict[str, Any]):
        """Approve and post an Instagram draft."""
        metadata = item['metadata']
        content = item['content']

        # Check if image is needed
        image_needed = metadata.get('image_needed', 'false').lower() == 'true'

        if image_needed:
            print("\n📸 This post requires an image")
            image_path = input("Enter full path to image file: ").strip()

            if not Path(image_path).exists():
                print(f"❌ Error: Image not found at {image_path}")
                return

            # Extract caption
            if '## Caption' in content:
                caption = content.split('## Caption')[1].split('##')[0].strip()
            else:
                print("❌ Error: Could not extract caption from draft")
                return

            # Call MCP server to post
            print("\n🚀 Posting to Instagram...")
            result = self._call_mcp_post_image(image_path, caption)

            if result.get('success'):
                print(f"✅ Posted successfully!")
                if result.get('dry_run'):
                    print("   (DRY_RUN mode - not actually posted)")
                else:
                    print(f"   Post ID: {result.get('post_id')}")
                    print(f"   URL: {result.get('post_url')}")

                # Move to Done
                done_path = self.done_dir / item['filename']
                item['filepath'].rename(done_path)
                print(f"   Moved to: {done_path}")
            else:
                print(f"❌ Error posting: {result.get('error')}")
        else:
            print("❌ Error: Posts without images not yet supported")

    def _approve_comment_reply(self, item: Dict[str, Any]):
        """Approve and post a comment reply."""
        metadata = item['metadata']
        content = item['content']

        # Extract suggested reply
        if '## Suggested Reply' in content:
            reply_text = content.split('## Suggested Reply')[1].split('##')[0].strip()
        else:
            print("❌ Error: Could not extract reply text")
            return

        # Allow editing
        print("\n✏️  Edit reply if needed (or press Enter to use as-is):")
        print(f"Current: {reply_text}")
        edited = input("New reply: ").strip()

        if edited:
            reply_text = edited

        comment_id = metadata.get('comment_id')

        if not comment_id:
            print("❌ Error: Missing comment_id in metadata")
            return

        # Call MCP server to reply
        print("\n💬 Posting reply...")
        result = self._call_mcp_reply_comment(comment_id, reply_text)

        if result.get('success'):
            print(f"✅ Reply posted successfully!")
            if result.get('dry_run'):
                print("   (DRY_RUN mode - not actually posted)")

            # Move to Done
            done_path = self.done_dir / item['filename']
            item['filepath'].rename(done_path)
            print(f"   Moved to: {done_path}")
        else:
            print(f"❌ Error posting reply: {result.get('error')}")

    def _call_mcp_post_image(self, image_path: str, caption: str) -> Dict[str, Any]:
        """Call Instagram MCP server to post image."""
        try:
            # Import the MCP server
            sys.path.insert(0, str(Path(__file__).parent / "mcp_servers"))
            from instagram_mcp_server import InstagramMCPServer

            server = InstagramMCPServer()
            return server.post_image(image_path, caption)

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _call_mcp_reply_comment(self, comment_id: str, reply_text: str) -> Dict[str, Any]:
        """Call Instagram MCP server to reply to comment."""
        try:
            # Import the MCP server
            sys.path.insert(0, str(Path(__file__).parent / "mcp_servers"))
            from instagram_mcp_server import InstagramMCPServer

            server = InstagramMCPServer()
            return server.reply_to_comment(comment_id, reply_text)

        except Exception as e:
            return {"success": False, "error": str(e)}

    def reject(self, filename: str, reason: str = None):
        """Reject an Instagram item."""
        items = self._get_pending_items()
        item = next((i for i in items if i['filename'] == filename), None)

        if not item:
            print(f"❌ Error: {filename} not found in pending approvals")
            return

        # Show preview
        self.show_preview(filename)

        # Ask for confirmation
        print("\n⚠️  This will reject and archive this item")
        confirm = input("Reject? (yes/no): ").strip().lower()

        if confirm != 'yes':
            print("❌ Rejection cancelled")
            return

        # Add rejection reason to file
        if reason:
            content = item['content']
            content += f"\n\n---\n## Rejection Reason\n{reason}\nRejected: {datetime.now().isoformat()}\n"
            item['filepath'].write_text(content, encoding='utf-8')

        # Move to Rejected
        rejected_path = self.rejected_dir / item['filename']
        item['filepath'].rename(rejected_path)

        print(f"✅ Rejected and moved to: {rejected_path}")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Instagram HITL Approval Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python approve_instagram.py --list
  python approve_instagram.py --approve IG_DRAFT_2026-03-29_topic
  python approve_instagram.py --reject IG_DRAFT_2026-03-29_topic --reason "Not aligned with brand"
        """
    )

    parser.add_argument('--list', action='store_true',
                       help='List all pending Instagram approvals')
    parser.add_argument('--approve', metavar='FILENAME',
                       help='Approve and publish an item')
    parser.add_argument('--reject', metavar='FILENAME',
                       help='Reject an item')
    parser.add_argument('--reason', metavar='TEXT',
                       help='Rejection reason (optional)')
    parser.add_argument('--preview', metavar='FILENAME',
                       help='Show full preview of an item')

    args = parser.parse_args()

    tool = InstagramApprovalTool()

    if args.list:
        tool.list_pending()

    elif args.approve:
        tool.approve(args.approve)

    elif args.reject:
        tool.reject(args.reject, args.reason)

    elif args.preview:
        tool.show_preview(args.preview)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
