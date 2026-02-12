# News AI - URL Handling Guide

## Overview
Your News AI system now includes enhanced URL validation and error handling to provide clear feedback when URLs can't be processed.

## ✅ Supported URL Types

### News Websites
- ✅ **BBC, CNN, Reuters, AP News, NPR**: `https://www.bbc.com/news/article-123`
- ✅ **Most news websites**: Standard news articles work well

### YouTube Videos
- ✅ **Valid format**: `https://www.youtube.com/watch?v=VIDEO_ID` (where VIDEO_ID is 11 characters)
- ✅ **Short format**: `https://youtu.be/VIDEO_ID`
- ❌ **Invalid**: `https://www.youtube.com/watch?v=watch` (missing actual video ID)

### Social Media (Limited Support)
- ⚠️ **Twitter/X**: May be blocked due to bot protection
- ⚠️ **Facebook, Instagram, TikTok**: Often require special authentication

## 🔧 New Features

### URL Validation Endpoint
Before processing any URL, you can validate it first:

```bash
POST http://localhost:8000/api/validate-url
{
  "url": "https://example.com/article"
}
```

**Response:**
```json
{
  "success": true/false,
  "data": {
    "is_valid": true/false,
    "issues": ["list of issues"],
    "suggestions": ["helpful suggestions"],
    "url_type": "youtube|twitter|news|general"
  }
}
```

### Enhanced Error Messages
When URLs fail, you now get:
1. **Clear error descriptions**
2. **Specific suggestions for fixes**
3. **URL type identification**
4. **Validation warnings**

## 🚫 Common URL Issues & Solutions

### 1. YouTube URL Problems

**❌ Problem**: `https://www.youtube.com/watch?v=watch`
- **Issue**: Missing actual video ID
- **Solution**: Get the complete URL like `https://www.youtube.com/watch?v=dQw4w9WgXcQ`

**❌ Problem**: Video is private/deleted
- **Issue**: "This video isn't available anymore"
- **Solution**: Use a different, publicly available video

### 2. Twitter/X Access Issues

**❌ Problem**: `https://x.com/user/status/123` → "JavaScript is not available"
- **Issue**: Twitter blocks automated access
- **Solutions**:
  1. Copy the tweet text manually and use summarization directly
  2. Use Twitter's official API (requires authentication)
  3. Try alternative news sources covering the same topic

### 3. Social Media Restrictions

**❌ Problem**: Facebook/Instagram/TikTok URLs blocked
- **Issue**: Social platforms have strict bot protection
- **Solutions**:
  1. Use news articles about the social media content
  2. Copy the text content directly for analysis
  3. Use official platform APIs

## 📊 Usage Examples

### Valid URLs
```python
# ✅ Good news article
"https://www.bbc.com/news/world-asia-12345678"

# ✅ Valid YouTube video  
"https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# ✅ News website
"https://www.reuters.com/world/breaking-news-story"
```

### Invalid URLs (will be caught by validation)
```python
# ❌ Malformed YouTube
"https://www.youtube.com/watch?v=watch"

# ❌ Incomplete URL
"https://youtube.com/watch"

# ⚠️ Social media (will show warnings)
"https://x.com/user/status/123456"
```

## 🔍 Testing Your URLs

### Method 1: Use Validation Endpoint
```bash
curl -X POST http://localhost:8000/api/validate-url \
  -H "Content-Type: application/json" \
  -d '{"url": "YOUR_URL_HERE"}'
```

### Method 2: Try Direct Scraping
```bash  
curl -X POST http://localhost:8000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "YOUR_URL_HERE"}'
```

### Method 3: Use the Test Script
```bash
cd unified_tools_backend
python test_url_issues.py
```

## 💡 Pro Tips

1. **Always validate URLs first** using the `/api/validate-url` endpoint
2. **For YouTube**: Make sure you have the complete video URL with a valid 11-character video ID
3. **For Twitter/X**: Consider copying the tweet text directly instead of scraping
4. **For news**: Stick to major news websites for best results
5. **Check error messages**: They now provide specific guidance on fixing issues

## 🆘 Troubleshooting

If you encounter issues:

1. **Check the validation endpoint** first to understand the problem
2. **Look at error messages** - they now provide specific suggestions
3. **Try alternative sources** for the same information
4. **Copy content directly** if automated scraping fails

Your News AI system now handles URL issues gracefully and provides clear feedback to help you get the best results!