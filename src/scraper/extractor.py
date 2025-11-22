"""Data extractor for TikTok metadata."""

from playwright.async_api import Page
from src.types import VideoMetadata, ProfileData, ExtractionError
import re
import random


class DataExtractor:
    """Extracts metadata from TikTok video pages."""
    
    def __init__(self, skip_profiles: bool = False):
        """Initialize extractor with optional profile skipping for speed."""
        self.skip_profiles = skip_profiles
    
    async def extract_profile_only(self, page: Page, url: str) -> VideoMetadata:
        """
        Extract profile data only (for profile URLs without video).
        
        Args:
            page: Playwright page object
            url: Profile URL
            
        Returns:
            VideoMetadata object with profile data only (video fields empty)
        """
        try:
            # Extract username from URL
            username = url.split('@')[-1].split('/')[0] if '@' in url else 'unknown'
            
            # Navigate to profile (ultra fast)
            await page.goto(url, timeout=8000, wait_until='domcontentloaded')
            await page.wait_for_timeout(random.randint(250, 400))  # Random human-like delay
            
            # Extract profile data
            profile_data = await self.extract_profile_data(page, username)
            
            # Return VideoMetadata with only profile data filled
            return VideoMetadata(
                video_url=url,
                caption="PROFILE",
                hashtags="PROFILE",
                likes=0,
                comments_count=0,
                share_count=0,
                username=username,
                upload_date="PROFILE",
                thumbnail_url="PROFILE",
                bio=profile_data.bio,
                email=profile_data.email,
                instagram_link=profile_data.instagram_link,
                youtube_link=profile_data.youtube_link,
                twitter_link=profile_data.twitter_link,
                other_links=profile_data.other_links
            )
        except Exception as e:
            raise ExtractionError(f"Failed to extract profile: {e}")
    
    async def extract_metadata(self, page: Page, url: str, skip_profile: bool = False) -> VideoMetadata:
        """
        Extract metadata from TikTok page.
        
        Args:
            page: Playwright page object
            url: Video URL
            
        Returns:
            VideoMetadata object with extracted data
            
        Raises:
            ExtractionError: If extraction fails
        """
        try:
            # Minimal wait for page to load - JSON is already there
            await page.wait_for_timeout(random.randint(400, 650))  # Random human-like delay
            
            # Extract data from __UNIVERSAL_DATA_FOR_REHYDRATION__ JSON
            json_data = await page.evaluate('''() => {
                const script = document.querySelector('#__UNIVERSAL_DATA_FOR_REHYDRATION__');
                if (script) {
                    return JSON.parse(script.textContent);
                }
                return null;
            }''')
            
            if json_data:
                # Navigate to video detail data
                try:
                    video_detail = json_data['__DEFAULT_SCOPE__']['webapp.video-detail']['itemInfo']['itemStruct']
                    
                    # Extract all fields
                    caption = video_detail.get('desc', '')
                    likes = video_detail.get('stats', {}).get('diggCount', 0)
                    comments_count = video_detail.get('stats', {}).get('commentCount', 0)
                    share_count = video_detail.get('stats', {}).get('shareCount', 0)
                    username = video_detail.get('author', {}).get('uniqueId', 'unknown')
                    upload_date = video_detail.get('createTime', '')
                    thumbnail_url = video_detail.get('video', {}).get('cover', '')
                    
                    # Extract hashtags
                    hashtags_list = [tag.get('title', '') for tag in video_detail.get('challenges', [])]
                    hashtags = ';'.join([f"#{tag}" for tag in hashtags_list if tag])
                    
                    # Extract profile data (optional for speed)
                    if self.skip_profiles:
                        profile_data = ProfileData(
                            bio="Profile scraping skipped",
                            email="Profile scraping skipped",
                            instagram_link="Profile scraping skipped",
                            youtube_link="Profile scraping skipped",
                            twitter_link="Profile scraping skipped",
                            other_links="Profile scraping skipped"
                        )
                    else:
                        profile_data = await self.extract_profile_data(page, username)
                    
                    return VideoMetadata(
                        video_url=url,
                        caption=caption,
                        hashtags=hashtags,
                        likes=likes,
                        comments_count=comments_count,
                        share_count=share_count,
                        username=username,
                        upload_date=str(upload_date),
                        thumbnail_url=thumbnail_url,
                        bio=profile_data.bio,
                        email=profile_data.email,
                        instagram_link=profile_data.instagram_link,
                        youtube_link=profile_data.youtube_link,
                        twitter_link=profile_data.twitter_link,
                        other_links=profile_data.other_links
                    )
                except (KeyError, TypeError) as e:
                    raise ExtractionError(f"Failed to parse JSON data: {e}")
            
            # Fallback to DOM scraping if JSON not available
            # Extract caption
            caption = await self._extract_text(page, '[data-e2e="video-desc"], [data-e2e="browse-video-desc"]')
            
            # Extract hashtags from caption
            hashtags = self._extract_hashtags(caption)
            
            # Extract stats
            likes = await self._extract_number(page, '[data-e2e="like-count"], [data-e2e="browse-like-count"]')
            comments_count = await self._extract_number(page, '[data-e2e="comment-count"], [data-e2e="browse-comment-count"]')
            share_count = await self._extract_number(page, '[data-e2e="share-count"], [data-e2e="undefined-count"]')
            
            # Extract username
            username = await self._extract_text(page, '[data-e2e="video-author-uniqueid"], [data-e2e="browse-username"]')
            
            # Extract upload date (try multiple selectors)
            upload_date = await self._extract_text(page, '[data-e2e="browser-nickname"] + span, time')
            
            # Extract thumbnail
            thumbnail_url = await self._extract_attribute(page, 'video, img[alt*="video"]', 'poster', 'src')
            
            # Extract profile data (optional for speed)
            if self.skip_profiles:
                profile_data = ProfileData(
                    bio="Profile scraping skipped",
                    email="Profile scraping skipped",
                    instagram_link="Profile scraping skipped",
                    youtube_link="Profile scraping skipped",
                    twitter_link="Profile scraping skipped",
                    other_links="Profile scraping skipped"
                )
            else:
                profile_data = await self.extract_profile_data(page, username or "unknown")
            
            return VideoMetadata(
                video_url=url,
                caption=caption or "",
                hashtags=hashtags,
                likes=likes,
                comments_count=comments_count,
                share_count=share_count,
                username=username or "unknown",
                upload_date=upload_date or "",
                thumbnail_url=thumbnail_url or "",
                bio=profile_data.bio,
                email=profile_data.email,
                instagram_link=profile_data.instagram_link,
                youtube_link=profile_data.youtube_link,
                twitter_link=profile_data.twitter_link,
                other_links=profile_data.other_links
            )
            
        except Exception as e:
            raise ExtractionError(f"Failed to extract metadata: {e}")
    
    async def _extract_text(self, page: Page, selector: str) -> str:
        """Extract text from element."""
        try:
            element = await page.query_selector(selector)
            if element:
                return await element.inner_text()
        except:
            pass
        return ""
    
    async def _extract_number(self, page: Page, selector: str) -> int:
        """Extract number from element."""
        try:
            text = await self._extract_text(page, selector)
            # Remove non-numeric characters except K, M, B
            text = text.strip().upper()
            
            # Handle K, M, B suffixes
            multiplier = 1
            if 'K' in text:
                multiplier = 1000
                text = text.replace('K', '')
            elif 'M' in text:
                multiplier = 1000000
                text = text.replace('M', '')
            elif 'B' in text:
                multiplier = 1000000000
                text = text.replace('B', '')
            
            # Extract number
            number_str = re.sub(r'[^\d.]', '', text)
            if number_str:
                return int(float(number_str) * multiplier)
        except:
            pass
        return 0
    
    async def _extract_attribute(self, page: Page, selector: str, *attributes: str) -> str:
        """Extract attribute from element."""
        try:
            element = await page.query_selector(selector)
            if element:
                for attr in attributes:
                    value = await element.get_attribute(attr)
                    if value:
                        return value
        except:
            pass
        return ""
    
    def _extract_hashtags(self, text: str) -> str:
        """Extract hashtags from text and format with semicolons."""
        if not text:
            return ""
        
        # Find all hashtags
        hashtags = re.findall(r'#\w+', text)
        
        # Join with semicolons
        return ';'.join(hashtags) if hashtags else ""
    
    async def extract_profile_data(self, page: Page, username: str) -> ProfileData:
        """
        Extract profile data from user's TikTok profile.
        
        Args:
            page: Playwright page object (currently on video page)
            username: TikTok username
            
        Returns:
            ProfileData object with contact info and social links
        """
        profile_data = ProfileData()
        
        if not username or username == "unknown":
            return profile_data
        
        try:
            # Navigate to profile page (ultra fast)
            profile_url = f"https://www.tiktok.com/@{username}"
            await page.goto(profile_url, timeout=8000, wait_until='domcontentloaded')
            await page.wait_for_timeout(random.randint(250, 400))  # Random human-like delay
            
            # Extract bio/description text
            bio_text = ""
            try:
                # Try multiple selectors for bio
                bio_selectors = [
                    '[data-e2e="user-bio"]',
                    'h2[data-e2e="user-subtitle"]',
                    '[class*="bio"]',
                    '[class*="description"]'
                ]
                
                for selector in bio_selectors:
                    bio_element = await page.query_selector(selector)
                    if bio_element:
                        bio_text = await bio_element.inner_text()
                        if bio_text:
                            break
            except:
                pass
            
            # Save bio text (set default message if empty)
            profile_data.bio = bio_text if bio_text else "Bio is empty"
            
            # Extract email from bio using regex
            if bio_text:
                email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
                email_matches = re.findall(email_pattern, bio_text)
                if email_matches:
                    profile_data.email = email_matches[0]
                
                # Extract Instagram handle from bio text (e.g., "insta: username" or "instagram: @username")
                instagram_patterns = [
                    r'(?:insta|instagram|ig)[\s:]+@?([a-zA-Z0-9._]+)',
                    r'@([a-zA-Z0-9._]+)(?:\s+on\s+(?:insta|instagram))',
                ]
                
                for pattern in instagram_patterns:
                    matches = re.findall(pattern, bio_text, re.IGNORECASE)
                    if matches:
                        # Build Instagram URL from username
                        instagram_username = matches[0].strip()
                        if not profile_data.instagram_link:  # Only if we haven't found a link yet
                            profile_data.instagram_link = f"https://instagram.com/{instagram_username}"
                        break
                
                # Extract Twitch handle from bio text (e.g., "twitch: username" or "twitch.tv/username")
                twitch_patterns = [
                    r'(?:twitch|ttv)[\s:]+@?([a-zA-Z0-9._]+)',
                    r'twitch\.tv/([a-zA-Z0-9._]+)',
                ]
                
                twitch_links = []
                for pattern in twitch_patterns:
                    matches = re.findall(pattern, bio_text, re.IGNORECASE)
                    if matches:
                        # Build Twitch URL from username
                        twitch_username = matches[0].strip()
                        twitch_url = f"https://twitch.tv/{twitch_username}"
                        if twitch_url not in twitch_links:
                            twitch_links.append(twitch_url)
                        break
            
            # Extract social media links
            try:
                # Get all anchor tags
                links = await page.query_selector_all('a[href]')
                
                instagram_links = []
                youtube_links = []
                twitter_links = []
                other_social_links = []
                
                for link in links:
                    href = await link.get_attribute('href')
                    if not href:
                        continue
                    
                    href = href.lower()
                    
                    # Categorize social media links
                    if 'instagram.com' in href:
                        instagram_links.append(href)
                    elif 'youtube.com' in href or 'youtu.be' in href:
                        youtube_links.append(href)
                    elif 'twitter.com' in href or 'x.com' in href:
                        twitter_links.append(href)
                    elif any(domain in href for domain in [
                        'facebook.com', 'linkedin.com', 'snapchat.com',
                        'twitch.tv', 'discord.gg', 'reddit.com',
                        'pinterest.com', 'tumblr.com', 'github.com'
                    ]):
                        other_social_links.append(href)
                
                # Take first link of each type
                if instagram_links:
                    profile_data.instagram_link = instagram_links[0]
                if youtube_links:
                    profile_data.youtube_link = youtube_links[0]
                if twitter_links:
                    profile_data.twitter_link = twitter_links[0]
                
                # Add Twitch links from bio to other_links
                if twitch_links:
                    other_social_links.extend(twitch_links)
                
                if other_social_links:
                    profile_data.other_links = ';'.join(other_social_links)
                    
            except Exception as e:
                # If link extraction fails, continue with empty values
                pass
            
        except Exception as e:
            # If profile navigation or extraction fails, return empty profile data
            # This is graceful failure - we continue with video metadata
            pass
        
        return profile_data
