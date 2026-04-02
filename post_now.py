"""
Post to Instagram - Real Posting
"""
import sys
import os
from pathlib import Path

# Add AI_Employee_Vault and instagram directory to path
vault_path = Path(__file__).parent / "AI_Employee_Vault"
instagram_path = vault_path / "instagram"
sys.path.insert(0, str(vault_path))
sys.path.insert(0, str(instagram_path))

# Temporarily disable DRY_RUN for this post
os.environ["DRY_RUN"] = "false"

from instagram_actions import InstagramActions

def post_now():
    """Post the approved image to Instagram"""

    print("=" * 70)
    print("POSTING TO INSTAGRAM - REAL POST")
    print("=" * 70)
    print()

    # Image details
    image_path = "AI_Employee_Vault/test_image.jpg"
    caption = "I love this picture"
    hashtags = ["fashion", "style", "clothing", "pakistan"]

    print(f"Image: {image_path}")
    print(f"Caption: {caption}")
    print(f"Hashtags: {', '.join(hashtags)}")
    print()
    print("Starting post process...")
    print()

    # Create actions instance
    actions = InstagramActions()

    # Post the photo
    result = actions.post_photo(
        image_path=image_path,
        caption=caption,
        hashtags=hashtags
    )

    print()
    print("=" * 70)
    print("POST COMPLETE!")
    print("=" * 70)
    print()
    print(f"Result: {result}")

    return result

if __name__ == "__main__":
    try:
        result = post_now()

        if result.get("success"):
            print()
            print("[SUCCESS] Your post is now live on Instagram!")
            print()
            if "screenshot" in result:
                print(f"Screenshot saved: {result['screenshot']}")
            print(f"Posted at: {result['timestamp']}")

    except Exception as e:
        print()
        print("[FAILED] POSTING FAILED")
        print(f"Error: {e}")
        print()
        print("Check AI_Employee_Vault/Logs/ for screenshots")
        print("Check AI_Employee_Vault/Signals/ for error details")
