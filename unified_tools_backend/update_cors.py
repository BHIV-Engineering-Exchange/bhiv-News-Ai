"""
Script to update CORS settings for production deployment
Run this after you know your Render frontend URL
"""

import sys

def update_cors(frontend_url):
    """Update CORS settings in main.py with the production frontend URL"""
    
    main_py_path = "main.py"
    
    try:
        with open(main_py_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the CORS middleware section
        cors_start = content.find('app.add_middleware(\n    CORSMiddleware,')
        if cors_start == -1:
            cors_start = content.find('app.add_middleware(\r\n    CORSMiddleware,')
        
        if cors_start == -1:
            print("❌ Could not find CORS middleware section in main.py")
            return False
        
        # Find the allow_origins list
        origins_start = content.find('allow_origins=[', cors_start)
        origins_end = content.find('],', origins_start)
        
        if origins_start == -1 or origins_end == -1:
            print("❌ Could not find allow_origins list")
            return False
        
        # Extract current origins
        current_origins = content[origins_start:origins_end + 2]
        
        # Check if URL already exists
        if frontend_url in current_origins:
            print(f"✅ {frontend_url} already in CORS allowed origins")
            return True
        
        # Add the new origin
        new_origin_line = f'        "{frontend_url}",  # Production frontend\n'
        insert_pos = origins_end
        
        # Insert before the closing bracket
        new_content = content[:insert_pos] + f',\n{new_origin_line}        ' + content[insert_pos:]
        
        # Write back
        with open(main_py_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ Added {frontend_url} to CORS allowed origins")
        print("\n📝 Next steps:")
        print("1. Review the changes in main.py")
        print("2. Commit: git add main.py")
        print("3. Commit: git commit -m 'Update CORS for production'")
        print("4. Push: git push")
        print("5. Render will automatically redeploy the backend")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating CORS: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python update_cors.py <frontend_url>")
        print("Example: python update_cors.py https://news-ai-frontend.onrender.com")
        sys.exit(1)
    
    frontend_url = sys.argv[1].rstrip('/')
    
    if not frontend_url.startswith('http'):
        print("❌ URL must start with http:// or https://")
        sys.exit(1)
    
    success = update_cors(frontend_url)
    sys.exit(0 if success else 1)
