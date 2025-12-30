#!/usr/bin/env python3
"""Fix Docker build in CI/CD workflow"""

file_path = r".github\workflows\ci-cd.yml"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the buildx setup line and add timeout
old_section = """    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
    
    - name: Authenticate to Google Cloud"""

new_section = """    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Authenticate to Google Cloud"""

content = content.replace(old_section, new_section)

# Add timeout to build step
old_build = """    - name: Build and Push Docker Image
      run: |"""

new_build = """    - name: Build and Push Docker Image
      timeout-minutes: 15
      run: |"""

content = content.replace(old_build, new_build)

# Add setup-gcloud action
old_auth = """    - name: Authenticate to Google Cloud
      uses: google-github-actions/auth@v2
      with:
        credentials_json: ${{ secrets.GCP_SA_KEY }}
    
    - name: Configure Docker for Artifact Registry"""

new_auth = """    - name: Authenticate to Google Cloud
      uses: google-github-actions/auth@v2
      with:
        credentials_json: ${{ secrets.GCP_SA_KEY }}
    
    - name: Set up Cloud SDK
      uses: google-github-actions/setup-gcloud@v2
    
    - name: Configure Docker for Artifact Registry"""

content = content.replace(old_auth, new_auth)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed CI/CD workflow:")
print("  - Removed Docker Buildx setup (causing timeout)")
print("  - Added setup-gcloud action")
print("  - Added 15-minute timeout to build step")
print("  - Using standard docker build instead")
