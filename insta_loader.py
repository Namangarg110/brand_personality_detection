# import os
# import instaloader
# import pandas as pd

# # Login 
# L = instaloader.Instaloader()
# username = 'testing_brand_api'
# password = 'PROGmanNAmus1@2'
# L.login(username, password)  
# target_profile = "apple"
# download_dir = target_profile + "__"
# os.makedirs(download_dir, exist_ok=True)
# posts_data = []

# # Get profile and download posts
# profile = instaloader.Profile.from_username(L.context, target_profile)
# for i, post in enumerate(profile.get_posts()):
#     L.download_post(post, target=download_dir)

#     image_files = [os.path.join(download_dir, file) for file in os.listdir(download_dir) if file.endswith(('.jpg', '.mp4')) and str(post.date_utc).replace(":","-").replace(" ","_") in file]

#     post_data = {
#         'Image File Path': image_files,
#         'Caption': post.caption,
#         'Post Date': post.date_utc,
#         'Post Time': post.date_utc.time()
#     }
#     posts_data.append(post_data)
#     if i > 100:
#         break

# df = pd.DataFrame(posts_data)

# # Save 
# csv_file_path = f"./{target_profile}_instagram_posts.csv"
# df.to_csv(csv_file_path, index=False)

# print(f"Data saved to {csv_file_path}")



import os
import instaloader
import pandas as pd
from itertools import cycle

# Your proxy list
proxies = [
    'http://72.10.160.172:5507',
    'http://64.225.8.203:10000',
    'http://64.225.8.132:10000',
    'http://196.74.46.134:8080',
    'http://64.225.8.179:10005',
    'http://103.152.112.145:80',
    'http://50.200.12.87:80',
]
proxy_cycle = cycle(proxies)

# Function to rotate proxy
def rotate_proxy(loader):
    proxy = next(proxy_cycle)
    loader.context.proxy = proxy
    print(f"Rotating proxy, now using: {proxy}")

# Initialize Instaloader with the first proxy
L = instaloader.Instaloader()
rotate_proxy(L)

# Function to safely perform an Instaloader action with proxy rotation
def safe_instaloader_action(action, *args, **kwargs):
    while True:
        try:
            return action(*args, **kwargs)
        except instaloader.exceptions.ConnectionException as e:
            print(f"Connection error: {e}. Rotating proxy.")
            rotate_proxy(L)
        except Exception as e:
            print(f"An error occurred: {e}. Rotating proxy.")
            rotate_proxy(L)

# Login to Instagram
username = 'testing_brand_api'
password = 'PROGmanNAmus1@2'
safe_instaloader_action(L.login, username, password)

# Specify the target profile and directory for downloads
target_profile = "statefarm"
download_dir = target_profile
os.makedirs(download_dir, exist_ok=True)

# List to hold all post information
posts_data = []

# Get profile and iterate over posts
profile = safe_instaloader_action(instaloader.Profile.from_username, L.context, target_profile)

for post in safe_instaloader_action(profile.get_posts):
    # Download the image
    if safe_instaloader_action(L.download_post, post, target=download_dir):
        # Retrieve the image file path
        image_files = [os.path.join(download_dir, file) for file in os.listdir(download_dir) if file.endswith(('.jpg', '.mp4')) and str(post.date_utc).replace(":","-").replace(" ","_") in file]

        # Collect post data
        post_data = {
            'Image File Path': image_files,
            'Caption': post.caption,
            'Post Date': post.date_utc,
            'Post Time': post.date_utc.time()
        }
        posts_data.append(post_data)

# Convert the list of dictionaries into a pandas DataFrame
df = pd.DataFrame(posts_data)

# Save the DataFrame to a CSV file
csv_file_path =  f'{target_profile}.csv'
df.to_csv(csv_file_path, index=False)

print(f"Data saved to {csv_file_path}")