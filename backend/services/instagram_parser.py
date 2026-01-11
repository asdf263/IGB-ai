"""
Instagram Data Export Parser
Parses Instagram ZIP exports and extracts messages from HTML or JSON files.
Supports both export formats that Instagram provides.
"""
import zipfile
import io
import re
import json
import logging
from typing import List, Dict, Any, Optional, Tuple, BinaryIO
from datetime import datetime
from collections import Counter
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class InstagramParser:
    """Parser for Instagram data export ZIP files (supports both HTML and JSON formats)"""
    
    # Regex patterns for Instagram message files
    MESSAGE_FILE_PATTERN_HTML = re.compile(
        r'your_instagram_activity/messages/inbox/[^/]+/message_\d+\.html$'
    )
    MESSAGE_FILE_PATTERN_JSON = re.compile(
        r'your_instagram_activity/messages/inbox/[^/]+/message_\d+\.json$'
    )
    
    # Legacy pattern for backwards compatibility
    MESSAGE_FILE_PATTERN = MESSAGE_FILE_PATTERN_HTML
    
    # Date formats Instagram uses
    DATE_FORMATS = [
        "%b %d, %Y %I:%M %p",  # "Dec 30, 2025 12:18 pm"
        "%b %d, %Y, %I:%M %p",  # "Dec 30, 2025, 12:18 pm"
        "%B %d, %Y %I:%M %p",  # "December 30, 2025 12:18 pm"
        "%B %d, %Y, %I:%M %p",  # "December 30, 2025, 12:18 pm"
    ]
    
    def __init__(self):
        self.owner_name: Optional[str] = None
    
    def parse_zip(self, file_content: bytes) -> Tuple[List[Dict[str, Any]], str]:
        """
        Parse Instagram ZIP export and extract all messages.
        Supports both HTML and JSON export formats.
        
        Args:
            file_content: Raw bytes of the ZIP file
            
        Returns:
            Tuple of (messages_list, owner_name)
            messages_list: List of message dicts with 'sender', 'text', 'timestamp'
            owner_name: Detected owner of the export (most frequent sender)
        """
        all_messages = []
        sender_counts = Counter()
        
        try:
            with zipfile.ZipFile(io.BytesIO(file_content), 'r') as zf:
                # Find all message files (both HTML and JSON formats)
                html_files = [
                    name for name in zf.namelist()
                    if self.MESSAGE_FILE_PATTERN_HTML.match(name)
                ]
                json_files = [
                    name for name in zf.namelist()
                    if self.MESSAGE_FILE_PATTERN_JSON.match(name)
                ]
                
                # Determine which format to use
                if json_files:
                    message_files = json_files
                    file_format = 'json'
                    logger.info(f"Detected JSON format export with {len(json_files)} message files")
                elif html_files:
                    message_files = html_files
                    file_format = 'html'
                    logger.info(f"Detected HTML format export with {len(html_files)} message files")
                else:
                    logger.warning("No message files found in ZIP")
                    raise ValueError("No Instagram message files found in the ZIP archive. Expected message_X.html or message_X.json files in your_instagram_activity/messages/inbox/")
                
                # Parse each message file
                for file_path in message_files:
                    try:
                        with zf.open(file_path) as f:
                            content = f.read().decode('utf-8')
                            
                            if file_format == 'json':
                                messages = self._parse_json_messages(content)
                            else:
                                messages = self._parse_html_messages(content)
                            
                            all_messages.extend(messages)
                            
                            # Count senders
                            for msg in messages:
                                sender_counts[msg['sender']] += 1
                                
                    except Exception as e:
                        logger.warning(f"Error parsing {file_path}: {e}")
                        continue
                
        except zipfile.BadZipFile:
            raise ValueError("Invalid ZIP file format")
        
        if not all_messages:
            raise ValueError("No messages could be extracted from the ZIP file")
        
        # Identify the owner (most frequent sender across all conversations)
        if sender_counts:
            self.owner_name = sender_counts.most_common(1)[0][0]
        else:
            self.owner_name = "unknown"
        
        # Sort messages by timestamp
        all_messages.sort(key=lambda x: x['timestamp'])
        
        # Remove duplicates (same sender, text, timestamp)
        unique_messages = self._deduplicate_messages(all_messages)
        
        logger.info(f"Extracted {len(unique_messages)} unique messages, owner: {self.owner_name}")
        
        return unique_messages, self.owner_name
    
    def _parse_html_messages(self, html_content: str) -> List[Dict[str, Any]]:
        """
        Parse messages from Instagram HTML content.
        
        Args:
            html_content: Raw HTML string
            
        Returns:
            List of message dicts
        """
        messages = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all message blocks (each message is in a div with class containing "uiBoxWhite")
        # The structure is: div.pam._3-95._2ph-._a6-g.uiBoxWhite.noborder
        message_blocks = soup.find_all('div', class_='uiBoxWhite')
        
        for block in message_blocks:
            try:
                # Extract sender from h2 with class _a6-h
                sender_elem = block.find('h2', class_='_a6-h')
                if not sender_elem:
                    continue
                sender = sender_elem.get_text(strip=True)
                
                # Extract message text from div with class _a6-p
                text_elem = block.find('div', class_='_a6-p')
                if not text_elem:
                    continue
                
                # Get all text content, handling nested divs
                text = self._extract_message_text(text_elem)
                
                # Skip empty messages or system messages
                if not text or text in ['Liked a message', 'sent an attachment.']:
                    continue
                
                # Skip messages that are just attachments
                if ' sent an attachment.' in text:
                    text = text.replace(' sent an attachment.', '').strip()
                    if not text:
                        continue
                
                # Extract timestamp from div with class _a6-o
                timestamp_elem = block.find('div', class_='_a6-o')
                if not timestamp_elem:
                    continue
                timestamp_str = timestamp_elem.get_text(strip=True)
                timestamp = self._parse_timestamp(timestamp_str)
                
                if timestamp is None:
                    continue
                
                messages.append({
                    'sender': sender,
                    'text': text,
                    'timestamp': timestamp
                })
                
            except Exception as e:
                logger.debug(f"Error parsing message block: {e}")
                continue
        
        return messages
    
    def _parse_json_messages(self, json_content: str) -> List[Dict[str, Any]]:
        """
        Parse messages from Instagram JSON content.
        
        Args:
            json_content: Raw JSON string
            
        Returns:
            List of message dicts
        """
        messages = []
        
        try:
            data = json.loads(json_content)
        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON content: {e}")
            return messages
        
        # Get messages array from JSON
        raw_messages = data.get('messages', [])
        
        for msg in raw_messages:
            try:
                # Extract sender name
                sender = msg.get('sender_name', '')
                if not sender:
                    continue
                
                # Fix encoding issues (Instagram uses latin-1 encoded UTF-8)
                sender = self._fix_instagram_encoding(sender)
                
                # Extract message content
                content = msg.get('content', '')
                if content:
                    content = self._fix_instagram_encoding(content)
                
                # Skip empty messages, reactions, or system messages
                if not content:
                    # Check if it's a share/link/photo - skip these for text analysis
                    if msg.get('share') or msg.get('photos') or msg.get('videos') or msg.get('audio_files'):
                        continue
                    continue
                
                # Skip "Reacted X to your message" notifications
                if content.startswith('Reacted ') and ' to your message' in content:
                    continue
                
                # Skip "Liked a message" notifications
                if content == 'Liked a message':
                    continue
                
                # Extract timestamp (in milliseconds)
                timestamp_ms = msg.get('timestamp_ms', 0)
                if not timestamp_ms:
                    continue
                
                # Convert to seconds
                timestamp = timestamp_ms // 1000
                
                messages.append({
                    'sender': sender,
                    'text': content,
                    'timestamp': timestamp
                })
                
            except Exception as e:
                logger.debug(f"Error parsing JSON message: {e}")
                continue
        
        return messages
    
    def _fix_instagram_encoding(self, text: str) -> str:
        """
        Fix Instagram's encoding issues where UTF-8 is stored as latin-1.
        Instagram exports sometimes have mojibake (UTF-8 bytes interpreted as latin-1).
        
        Args:
            text: Text string that may have encoding issues
            
        Returns:
            Properly decoded text
        """
        try:
            # Try to fix mojibake by encoding as latin-1 and decoding as UTF-8
            return text.encode('latin-1').decode('utf-8')
        except (UnicodeDecodeError, UnicodeEncodeError):
            # If that fails, return original text
            return text
    
    def _extract_message_text(self, text_elem) -> str:
        """
        Extract clean message text from the text element.
        Handles nested divs and filters out reactions/attachments.
        
        Args:
            text_elem: BeautifulSoup element containing message text
            
        Returns:
            Clean message text string
        """
        # Find direct text-containing div children
        text_parts = []
        
        for child in text_elem.children:
            if hasattr(child, 'name') and child.name == 'div':
                # Check for nested structure
                inner_divs = child.find_all('div', recursive=False)
                if inner_divs:
                    for inner in inner_divs:
                        # Skip divs that are links/attachments/reactions
                        if inner.find('a') or inner.find('ul') or inner.find('img'):
                            continue
                        text = inner.get_text(strip=True)
                        if text and not text.startswith('❤') and not text.startswith('http'):
                            text_parts.append(text)
                else:
                    text = child.get_text(strip=True)
                    # Skip reactions (start with emoji) and URLs
                    if text and not text.startswith('❤') and not text.startswith('http'):
                        text_parts.append(text)
        
        # Join and clean up
        result = ' '.join(text_parts).strip()
        
        # Remove "X sent an attachment." prefix if present
        if result and ' sent an attachment.' in result:
            result = result.split(' sent an attachment.')[-1].strip()
        
        return result
    
    def _parse_timestamp(self, timestamp_str: str) -> Optional[int]:
        """
        Parse Instagram timestamp string to Unix timestamp.
        
        Args:
            timestamp_str: Timestamp string like "Dec 30, 2025 12:18 pm"
            
        Returns:
            Unix timestamp as integer, or None if parsing fails
        """
        # Clean up the string
        timestamp_str = timestamp_str.strip()
        
        # Try each date format
        for fmt in self.DATE_FORMATS:
            try:
                dt = datetime.strptime(timestamp_str, fmt)
                return int(dt.timestamp())
            except ValueError:
                continue
        
        # Try to handle variations with case insensitivity
        timestamp_lower = timestamp_str.lower()
        for fmt in self.DATE_FORMATS:
            try:
                # Convert to title case for month names
                parts = timestamp_str.split()
                if parts:
                    parts[0] = parts[0].capitalize()
                    if len(parts) > 4:
                        parts[-1] = parts[-1].upper()  # AM/PM
                    normalized = ' '.join(parts)
                    dt = datetime.strptime(normalized, fmt)
                    return int(dt.timestamp())
            except ValueError:
                continue
        
        logger.debug(f"Could not parse timestamp: {timestamp_str}")
        return None
    
    def _deduplicate_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate messages based on sender, text, and timestamp.
        
        Args:
            messages: List of message dicts
            
        Returns:
            Deduplicated list of messages
        """
        seen = set()
        unique = []
        
        for msg in messages:
            key = (msg['sender'], msg['text'], msg['timestamp'])
            if key not in seen:
                seen.add(key)
                unique.append(msg)
        
        return unique
    
    def get_owner_messages(self, messages: List[Dict[str, Any]], owner_name: str) -> List[Dict[str, Any]]:
        """
        Filter messages to only those sent by the owner.
        
        Args:
            messages: All messages
            owner_name: Name of the owner to filter by
            
        Returns:
            Filtered list of messages from the owner
        """
        return [msg for msg in messages if msg['sender'] == owner_name]


def parse_instagram_zip(file_content: bytes, owner_only: bool = True) -> Tuple[List[Dict[str, Any]], str]:
    """
    Convenience function to parse Instagram ZIP export.
    
    Args:
        file_content: Raw bytes of the ZIP file
        owner_only: If True, only return messages sent by the owner (default: True)
        
    Returns:
        Tuple of (messages_list, owner_name)
        messages_list: Messages from the owner only (if owner_only=True) or all messages
        owner_name: Detected owner of the export
    """
    parser = InstagramParser()
    all_messages, owner_name = parser.parse_zip(file_content)
    
    if owner_only:
        owner_messages = parser.get_owner_messages(all_messages, owner_name)
        logger.info(f"Filtered to {len(owner_messages)} messages from owner '{owner_name}' (out of {len(all_messages)} total)")
        return owner_messages, owner_name
    
    return all_messages, owner_name

