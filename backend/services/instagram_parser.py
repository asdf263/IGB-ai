"""
Instagram Data Export Parser
Parses Instagram ZIP exports and extracts messages from HTML files
"""
import zipfile
import io
import re
import logging
from typing import List, Dict, Any, Optional, Tuple, BinaryIO
from datetime import datetime
from collections import Counter
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class InstagramParser:
    """Parser for Instagram data export ZIP files"""
    
    # Regex pattern for Instagram message HTML files
    MESSAGE_FILE_PATTERN = re.compile(
        r'your_instagram_activity/messages/inbox/[^/]+/message_\d+\.html$'
    )
    
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
                # Find all message HTML files
                message_files = [
                    name for name in zf.namelist()
                    if self.MESSAGE_FILE_PATTERN.match(name)
                ]
                
                if not message_files:
                    logger.warning("No message files found in ZIP")
                    raise ValueError("No Instagram message files found in the ZIP archive")
                
                logger.info(f"Found {len(message_files)} message files in ZIP")
                
                # Parse each message file
                for file_path in message_files:
                    try:
                        with zf.open(file_path) as f:
                            html_content = f.read().decode('utf-8')
                            messages = self._parse_html_messages(html_content)
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

