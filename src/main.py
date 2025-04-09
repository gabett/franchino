from youtube_api_manager import YouTubeAPIManager

if __name__ == "__main__":
    manager = YouTubeAPIManager()
    
    channel_info = manager.get_channel_info(channel_id="UC_x5XG1OV2P6uZZ5FSM9Ttw")  # Google Developers
    print(f"Nome del canale: {channel_info['title']}")
    print(f"Iscritti: {channel_info['subscriberCount']}")
    print(f"Video totali: {channel_info['videoCount']}")
    
    videos = manager.get_all_videos(channel_id="UC_x5XG1OV2P6uZZ5FSM9Ttw", max_results=10)
    
    print("\Latest 10 videos:")
    for video in videos:
        print(f"- {video['title']} ({video['url']})")
    
    # Details of a specific video
    if videos:
        video_details = manager.get_video_details(videos[0]['id'])
        print(f"\nDettagli del video: {video_details['title']}")
        print(f"Visualizzazioni: {video_details['viewCount']}")
        print(f"Mi piace: {video_details['likeCount']}")
        print(f"Commenti: {video_details['commentCount']}")