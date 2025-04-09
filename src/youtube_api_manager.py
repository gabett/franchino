from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union


class YouTubeAPIManager:
    """
    Manager class to interact with YouTube API using googleapiclient.
    Provides methods to get channel information and list all videos from a channel.
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize the YouTube API Manager.
        
        Args:
            api_key: YouTube Data API v3 key. If None, tries to get it from environment variable.
        """
        if api_key is None:
            api_key = os.environ.get('YOUTUBE_API_KEY')
            if api_key is None:
                raise ValueError("API key not provided and YOUTUBE_API_KEY environment variable not set")
        
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
    
    def get_channel_info(self, channel_id: str = None, username: str = None) -> Dict[str, Any]:
        """
        Get information about a YouTube channel.
        
        Args:
            channel_id: The ID of the channel to retrieve info for (preferred).
            username: The username of the channel to retrieve info for.
            
        Returns:
            Dictionary containing channel information.
            
        Raises:
            ValueError: If neither channel_id nor username is provided.
            HttpError: If the API request fails.
        """
        if not channel_id and not username:
            raise ValueError("Either channel_id or username must be provided")
        
        try:
            if channel_id:
                request = self.youtube.channels().list(
                    part="snippet,contentDetails,statistics",
                    id=channel_id
                )
            else:
                request = self.youtube.channels().list(
                    part="snippet,contentDetails,statistics",
                    forUsername=username
                )
                
            response = request.execute()
            
            if not response.get('items'):
                return {"error": "Channel not found"}
            
            channel_data = response['items'][0]
            
            return {
                "id": channel_data['id'],
                "title": channel_data['snippet']['title'],
                "description": channel_data['snippet']['description'],
                "customUrl": channel_data['snippet'].get('customUrl', ''),
                "publishedAt": channel_data['snippet']['publishedAt'],
                "thumbnails": channel_data['snippet']['thumbnails'],
                "country": channel_data['snippet'].get('country', ''),
                "viewCount": channel_data['statistics'].get('viewCount', 0),
                "subscriberCount": channel_data['statistics'].get('subscriberCount', 0),
                "hiddenSubscriberCount": channel_data['statistics'].get('hiddenSubscriberCount', False),
                "videoCount": channel_data['statistics'].get('videoCount', 0),
                "uploads_playlist": channel_data['contentDetails']['relatedPlaylists']['uploads']
            }
            
        except HttpError as e:
            error_details = json.loads(e.content.decode('utf-8'))
            return {"error": f"API Error: {error_details['error']['message']}"}
    
    def get_all_videos(self, channel_id: str = None, username: str = None, 
                       max_results: int = 50, published_after: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Get all videos from a channel.
        
        Args:
            channel_id: The ID of the channel.
            username: The username of the channel.
            max_results: Maximum number of videos to retrieve (default: 50).
            published_after: Filter videos published after this datetime.
            
        Returns:
            List of dictionaries containing video information.
            
        Raises:
            ValueError: If neither channel_id nor username is provided.
            HttpError: If the API request fails.
        """
        if not channel_id and not username:
            raise ValueError("Either channel_id or username must be provided")
        
        try:
            # First, get the channel info to get the uploads playlist ID
            if username and not channel_id:
                channel_info = self.get_channel_info(username=username)
                if "error" in channel_info:
                    return [{"error": channel_info["error"]}]
                channel_id = channel_info["id"]
            else:
                channel_info = self.get_channel_info(channel_id=channel_id)
                if "error" in channel_info:
                    return [{"error": channel_info["error"]}]
            
            uploads_playlist_id = channel_info["uploads_playlist"]
            
            # Now get the videos from the uploads playlist
            videos = []
            next_page_token = None
            
            while True:
                # Break if we've reached the max results
                if max_results and len(videos) >= max_results:
                    break
                
                request = self.youtube.playlistItems().list(
                    part="snippet,contentDetails",
                    playlistId=uploads_playlist_id,
                    maxResults=min(50, max_results - len(videos) if max_results else 50),
                    pageToken=next_page_token
                )
                
                response = request.execute()
                
                for item in response['items']:
                    # Skip if the video was published before our filter date
                    if published_after:
                        published_at = datetime.strptime(
                            item['snippet']['publishedAt'], 
                            '%Y-%m-%dT%H:%M:%SZ'
                        )
                        if published_at < published_after:
                            continue
                    
                    video_data = {
                        "id": item['contentDetails']['videoId'],
                        "title": item['snippet']['title'],
                        "description": item['snippet']['description'],
                        "publishedAt": item['snippet']['publishedAt'],
                        "thumbnails": item['snippet']['thumbnails'],
                        "channelId": item['snippet']['channelId'],
                        "channelTitle": item['snippet']['channelTitle'],
                        "url": f"https://www.youtube.com/watch?v={item['contentDetails']['videoId']}"
                    }
                    
                    videos.append(video_data)
                
                # Check if there are more pages
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
            
            return videos
            
        except HttpError as e:
            error_details = json.loads(e.content.decode('utf-8'))
            return [{"error": f"API Error: {error_details['error']['message']}"}]
    
    def get_video_details(self, video_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific video.
        
        Args:
            video_id: The ID of the video.
            
        Returns:
            Dictionary containing video information.
            
        Raises:
            HttpError: If the API request fails.
        """
        try:
            request = self.youtube.videos().list(
                part="snippet,contentDetails,statistics",
                id=video_id
            )
            
            response = request.execute()
            
            if not response.get('items'):
                return {"error": "Video not found"}
            
            video_data = response['items'][0]
            
            return {
                "id": video_data['id'],
                "title": video_data['snippet']['title'],
                "description": video_data['snippet']['description'],
                "publishedAt": video_data['snippet']['publishedAt'],
                "thumbnails": video_data['snippet']['thumbnails'],
                "channelId": video_data['snippet']['channelId'],
                "channelTitle": video_data['snippet']['channelTitle'],
                "tags": video_data['snippet'].get('tags', []),
                "categoryId": video_data['snippet'].get('categoryId', ''),
                "duration": video_data['contentDetails']['duration'],
                "viewCount": video_data['statistics'].get('viewCount', 0),
                "likeCount": video_data['statistics'].get('likeCount', 0),
                "commentCount": video_data['statistics'].get('commentCount', 0),
                "url": f"https://www.youtube.com/watch?v={video_data['id']}"
            }
            
        except HttpError as e:
            error_details = json.loads(e.content.decode('utf-8'))
            return {"error": f"API Error: {error_details['error']['message']}"}
