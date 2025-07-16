import cloudscraper, requests, hashlib, os

api_url = 'https://api.iwara.tv'
file_url = 'https://files.iwara.tv'

class BearerAuth(requests.auth.AuthBase):
    """Bearer Authentication"""
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers['Authorization'] = 'Bearer ' + self.token
        return r

class ApiClient:
    def __init__(self, email, password):
        self.scraper = cloudscraper.create_scraper()
        self.email = email
        self.password = password
        self.api_url = api_url
        self.file_url = file_url
        self.token = None

    def login(self) -> requests.Response:
        url = self.api_url + '/user/login'
        json = {'email': self.email, 'password': self.password}
        r = self.scraper.post(
            url, 
            json=json,
            )
        
        #Debug
        print("[DEBUG] login response:", r)

        try:
            self.token = r.json().get('token')
            print('API Login success')
        except:
            print('API Login failed')
        return r

    # limit query is not working
    def get_videos(self, sort = 'date', rating = 'all', page = 0, limit = 32, subscribed = False) -> requests.Response:
        """# Get new videos from iwara.tv
        - sort: date, trending, popularity, views, likes
        - rating: all, general, ecchi
        """
        url = self.api_url + '/videos'
        params = {'sort': sort, 
                  'rating': rating, 
                  'page': page, 
                  'limit': limit,
                  'subscribed': 'true' if subscribed else 'false',
                  }
        if self.token is None:
            r = self.scraper.get(url, params=params)
        else:
            r = self.scraper.get(url, params=params, auth=BearerAuth(self.token))

        #Debug
        print("[DEBUG] get_videos response:", r)

        return r
    
    def get_video(self, video_id) -> requests.Response:
        """# Get video info from iwara.tv
        """
        url = self.api_url + '/video/' + video_id

        if self.token is None:
            r = self.scraper.get(url)
        else:
            r = self.scraper.get(url, auth=BearerAuth(self.token))

        #Debug
        print("[DEBUG] get_video response:", r)

        return r
    
    def download_video_thumbnail(self, video_id) -> str:
        """# Download video thumbnail from iwara.tv
        """
        video = self.get_video(video_id).json()

        file_id = video['file']['id']
        thumbnail_id = video['thumbnail']
        
        url = self.file_url + '/image/original/' + file_id + '/thumbnail-{:02d}.jpg'.format(thumbnail_id)

        thumbnail_file_name = video_id + '.jpg'

        if (os.path.exists(thumbnail_file_name)):
            print(f"Video ID {video_id} thumbnail already downloaded, skipped downloading. ")
            return thumbnail_file_name
        
        print(f"Downloading thumbnail for video ID: {video_id} ...")
        with open(thumbnail_file_name, "wb") as f:
            for chunk in self.scraper.get(url).iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    f.flush()

        return thumbnail_file_name

    def download_video(self, video_id) -> str:
        """# Download video from iwara.tv
        """
        try:
            video = self.get_video(video_id).json()
        except Exception as e:
            raise Exception(f"Failed to get video info for video ID: {video_id}, error: {e}")

        url = video['fileUrl']
        file_id = video['file']['id']
        expires = url.split('/')[4].split('?')[1].split('&')[0].split('=')[1]

        # IMPORTANT: This might change in the future.
        SHA_postfix = "_5nFp9kmbNnHdAFhaqMvt"

        SHA_key = file_id + "_" + expires + SHA_postfix
        hash = hashlib.sha1(SHA_key.encode('utf-8')).hexdigest()

        headers = {"X-Version": hash}

        resources = self.scraper.get(url, headers=headers, auth=BearerAuth(self.token)).json()

        resources_by_quality = [None for i in range(10)]

        for resource in resources:
            if resource['name'] == 'Source':
                resources_by_quality[0] = resource

        for resource in resources_by_quality:
            if resource is not None:
                download_link = "https:" + resource['src']['download']
                file_type = resource['type'].split('/')[1]

                video_file_name = video_id + '.' + file_type

                if (os.path.exists(video_file_name)):
                    print(f"Video ID {video_id} Already downloaded, skipped downloading. ")
                    return video_file_name

                print(f"Downloading video ID: {video_id} ...")
                try:
                    with open(video_file_name, "wb") as f:
                        for chunk in self.scraper.get(download_link).iter_content(chunk_size=1024):
                            if chunk:
                                f.write(chunk)
                                f.flush()
                    return video_file_name
                except Exception as e:
                    os.remove(video_file_name)
                    raise Exception(f"Failed to download video ID: {video_id}, error: {e}")

            
        raise Exception("No video with Source quality found")