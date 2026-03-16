import os
import json
import requests
from config import GITEA_URL, HEADERS

def get_all_users():
    """
    Fetches all users from the Gitea API.
    Handles pagination. Note: Requires the token to have Admin privileges 
    if using the /admin/users endpoint.
    """
    users = []
    page = 1
    limit = 50
    
    print(f"Fetching users from {GITEA_URL}...")
    
    while True:
        # Using the admin endpoints gives us more detail (like email, 2fa status).
        # If your token is not an admin, you might need to use /api/v1/users/search instead.
        url = f"{GITEA_URL}/api/v1/admin/users?page={page}&limit={limit}"
        
        response = requests.get(url, headers=HEADERS)
        
        if response.status_code != 200:
            print(f"Error fetching users: HTTP {response.status_code}")
            print(response.text)
            break
            
        page_users = response.json()
        
        if not page_users:
            break  # No more users
            
        users.extend(page_users)
        page += 1
        
    return users

if __name__ == "__main__":
    all_users = get_all_users()
    
    if all_users:
        print(f"Successfully retrieved {len(all_users)} users.")
        
        # Determine the absolute path for the output directory
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_dir = os.path.join(base_dir, "output", "inventory")
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, "users.json")
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(all_users, f, indent=4, ensure_ascii=False)
            
        print(f"Data saved to {output_file}")
