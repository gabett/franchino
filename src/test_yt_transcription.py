import os
from youtube_transcript_api import YouTubeTranscriptApi
from typing import List

class YoutubeTranscriptor:

    def transcript(self, video_id : str, languages : List[str]):
        ytt_api = YouTubeTranscriptApi()
        fetched_transcript = ytt_api.fetch(video_id,
                                        languages=languages,
                                        preserve_formatting=True)

        caption = " ".join(snippet.text for snippet in fetched_transcript)

        if os.path.isdir("./transcriptions") == False:
            os.mkdir("./transcriptions")

        with open(f"./transcriptions/{video_id}.txt", "w") as f:
            f.write(caption)