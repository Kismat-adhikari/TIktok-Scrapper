"""CSV writer for output data."""

import csv
from pathlib import Path
from src.types import VideoMetadata


class CSVWriter:
    """Writes video metadata to CSV file."""
    
    COLUMNS = [
        'video_url', 'caption', 'hashtags', 'likes', 'comments_count',
        'share_count', 'username', 'upload_date', 'thumbnail_url',
        'bio', 'email', 'instagram_link', 'youtube_link', 'twitter_link', 'other_links'
    ]
    
    def __init__(self, file_path: str):
        """
        Initialize CSV writer.
        
        Args:
            file_path: Path to output CSV file
        """
        self.file_path = Path(file_path)
        self.file = None
        self.writer = None
    
    async def write_header(self) -> None:
        """Write CSV header."""
        self.file = open(self.file_path, 'w', newline='', encoding='utf-8')
        self.writer = csv.DictWriter(self.file, fieldnames=self.COLUMNS)
        self.writer.writeheader()
    
    async def write_row(self, data: VideoMetadata) -> None:
        """
        Write data row to CSV.
        
        Args:
            data: Video metadata to write
        """
        if not self.writer:
            await self.write_header()
        
        row = {
            'video_url': data.video_url,
            'caption': data.caption,
            'hashtags': data.hashtags,
            'likes': data.likes,
            'comments_count': data.comments_count,
            'share_count': data.share_count,
            'username': data.username,
            'upload_date': data.upload_date,
            'thumbnail_url': data.thumbnail_url,
            'bio': data.bio,
            'email': data.email,
            'instagram_link': data.instagram_link,
            'youtube_link': data.youtube_link,
            'twitter_link': data.twitter_link,
            'other_links': data.other_links
        }
        
        self.writer.writerow(row)
        self.file.flush()  # Ensure data is written immediately
    
    async def close(self) -> None:
        """Close CSV file."""
        if self.file:
            self.file.close()
