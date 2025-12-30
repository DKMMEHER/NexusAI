#!/usr/bin/env python3
"""Fix Docker image names to be lowercase"""

file_path = r".github\workflows\ci-cd.yml"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the build step
old_build = '''    - name: Build and Push Docker Image
      timeout-minutes: 15
      run: |
        IMAGE_NAME="${{ env.REGION }}-docker.pkg.dev/${{ env.PROJECT_ID }}/nexusai/${{ matrix.service }}:${{ github.sha }}"
        IMAGE_LATEST="${{ env.REGION }}-docker.pkg.dev/${{ env.PROJECT_ID }}/nexusai/${{ matrix.service }}:latest"
        
        docker build -t $IMAGE_NAME -t $IMAGE_LATEST -f ${{ matrix.service }}/Dockerfile .
        docker push $IMAGE_NAME
        docker push $IMAGE_LATEST
        
        echo "✅ Built and pushed: ${{ matrix.service }}"'''

new_build = '''    - name: Build and Push Docker Image
      timeout-minutes: 15
      run: |
        SERVICE_LOWER=$(echo "${{ matrix.service }}" | tr '[:upper:]' '[:lower:]')
        IMAGE_NAME="${{ env.REGION }}-docker.pkg.dev/${{ env.PROJECT_ID }}/nexusai/${SERVICE_LOWER}:${{ github.sha }}"
        IMAGE_LATEST="${{ env.REGION }}-docker.pkg.dev/${{ env.PROJECT_ID }}/nexusai/${SERVICE_LOWER}:latest"
        
        echo "Building ${{ matrix.service }}..."
        docker build -t $IMAGE_NAME -t $IMAGE_LATEST -f ${{ matrix.service }}/Dockerfile .
        
        echo "Pushing ${{ matrix.service }}..."
        docker push $IMAGE_NAME
        docker push $IMAGE_LATEST
        
        echo "✅ Built and pushed: ${{ matrix.service }}"'''

content = content.replace(old_build, new_build)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed Docker image names to use lowercase")
print("   - Added SERVICE_LOWER variable")
print("   - Converts matrix.service to lowercase")
print("   - Docker tags will now be: imagegeneration, chat, director, etc.")
