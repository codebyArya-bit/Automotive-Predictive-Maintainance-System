"""
Patch to integrate extended API endpoints into main api_server.py
Run this to add the new endpoints to your API server
"""

import os

# Content to add to api_server.py after the existing imports
IMPORT_ADDITIONS = """
# Extended features imports
from api_endpoints_extended import router as extended_router
"""

# Content to add after app initialization (after CORS middleware)
APP_INTEGRATION = """
# Include extended API endpoints
app.include_router(extended_router)
"""

def patch_api_server():
    """Add extended endpoints to api_server.py"""

    file_path = "api_server.py"

    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found!")
        return False

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if already patched
    if "api_endpoints_extended" in content:
        print("API server already patched with extended endpoints!")
        return True

    # Add import after database imports
    import_marker = "from database_manager import DatabaseManager"
    if import_marker in content:
        content = content.replace(
            import_marker,
            import_marker + "\n" + IMPORT_ADDITIONS
        )
        print("✓ Added extended imports")

    # Add router inclusion after CORS middleware
    cors_marker = "allow_headers=[\"*\"],\n)"
    if cors_marker in content:
        content = content.replace(
            cors_marker,
            cors_marker + "\n" + APP_INTEGRATION
        )
        print("✓ Integrated extended router")

    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("\n✅ API server successfully patched!")
    print("   New endpoints available:")
    print("   - /api/v1/auth/*")
    print("   - /api/v1/demand-forecast")
    print("   - /api/v1/rca-reports")
    print("   - /api/v1/edge-cases/*")
    print("   - /api/v1/voice-agent/*")
    print("   - /api/v1/dashboard/*")
    print("\n   Restart the API server to apply changes.")

    return True

if __name__ == "__main__":
    patch_api_server()
