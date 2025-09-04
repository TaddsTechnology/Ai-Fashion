#!/usr/bin/env python3
"""
Script to deploy AI Fashion app to Hugging Face Spaces
"""
import os
import shutil
from huggingface_hub import HfApi, create_repo, upload_file, upload_folder
from pathlib import Path

def main():
    # Set up HF token
    hf_token = "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"
    github_token = "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"
    
    api = HfApi(token=hf_token)
    
    # Repository details
    repo_id = "TaddsTeam/Ai-Fashion"  # Correct space name
    repo_type = "space"
    
    print(f"🚀 Deploying AI Fashion app to Hugging Face Space: {repo_id}")
    
    try:
        # Check if the space already exists
        try:
            api.repo_info(repo_id=repo_id, repo_type=repo_type)
            print(f"✅ Space {repo_id} already exists, updating files...")
        except Exception:
            try:
                # Create the space if it doesn't exist
                print(f"📝 Creating new Hugging Face Space: {repo_id}")
                create_repo(
                    repo_id=repo_id,
                    repo_type=repo_type,
                    space_sdk="gradio",
                    token=hf_token,
                    private=False  # Make it public
                )
                print(f"✅ Created space: {repo_id}")
            except Exception as create_error:
                if "already created" in str(create_error).lower():
                    print(f"✅ Space {repo_id} already exists (from error), proceeding with upload...")
                else:
                    raise create_error
        
        # Get current directory
        current_dir = Path.cwd()
        
        # Files to upload to HF Space
        files_to_upload = [
            "app.py",
            "requirements.txt", 
            "README.md"
        ]
        
        # Folders to upload
        folders_to_upload = [
            "backend"
        ]
        
        print("📤 Uploading files to Hugging Face Space...")
        
        # Upload individual files
        for file_name in files_to_upload:
            file_path = current_dir / file_name
            if file_path.exists():
                print(f"   Uploading {file_name}...")
                api.upload_file(
                    path_or_fileobj=str(file_path),
                    path_in_repo=file_name,
                    repo_id=repo_id,
                    repo_type=repo_type,
                    token=hf_token,
                    commit_message=f"Update {file_name}"
                )
                print(f"   ✅ {file_name} uploaded")
            else:
                print(f"   ⚠️  {file_name} not found, skipping")
        
        # Upload backend folder
        print("📁 Uploading backend folder...")
        for folder_name in folders_to_upload:
            folder_path = current_dir / folder_name
            if folder_path.exists():
                print(f"   Uploading {folder_name}/ directory...")
                api.upload_folder(
                    folder_path=str(folder_path),
                    path_in_repo=folder_name,
                    repo_id=repo_id,
                    repo_type=repo_type,
                    token=hf_token,
                    commit_message=f"Update {folder_name} directory"
                )
                print(f"   ✅ {folder_name}/ uploaded")
            else:
                print(f"   ⚠️  {folder_name}/ not found, skipping")
        
        print(f"""
🎉 Deployment Complete!
        
Your AI Fashion app is now available at:
https://huggingface.co/spaces/{repo_id}

The app should build and deploy automatically within a few minutes.
        """)
        
    except Exception as e:
        print(f"❌ Error during deployment: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
