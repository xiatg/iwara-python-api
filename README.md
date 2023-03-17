# Python API Client for [iwara.tv](https://iwara.tv)

## Getting Started

Below is an example on how to login and download a video using the video ID:

```python
from api_client import ApiClient

# Step 1: Initialize an API client with your credentials
client = ApiClient(email="email", password="password")

# Step 2: Login to get the access token
client.login()

# Step 3: Download a video using the video ID
client.download_video(video_id="video_id")
```

## Features

  * Login
  * Get video information
    * sort by: date, trending, popularity, views, likes
    * filter by rating: all, general, ecchi
    * get from a specific page
    * limit the number of videos returned
    * get from subscribed creators
  * Get video information by video ID
  * Download video by video ID
  * Download video thumbnail by video ID