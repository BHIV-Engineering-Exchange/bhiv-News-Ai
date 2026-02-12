# ⚡ Quick Start Guide - News AI Frontend

Get up and running in 5 minutes!

---

## 🎯 Prerequisites

- **Node.js** 18+ installed
- **npm** or **yarn** package manager
- **Git** for cloning
- Text editor (VS Code recommended)

Check versions:
```bash
node --version  # Should be 18.x or higher
npm --version   # Should be 9.x or higher
```

---

## 🚀 Installation (3 Steps)

### Step 1: Clone and Install

```bash
# Clone the repository
git clone <repository-url>
cd blackhole-frontend

# Install dependencies
npm install
```

### Step 2: Configure Environment

```bash
# Create environment file
cp .env.example .env.local
```

Edit `.env.local`:
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### Step 3: Run

```bash
# Start development server
npm run dev
```

Open http://localhost:3000 🎉

---

## 📱 Navigation Guide

### Available Pages

| Page | URL | Description |
|------|-----|-------------|
| **Home** | `/` | Main news analysis interface |
| **Live Dashboard** | `/live` | Real-time processing pipeline |
| **News Feed** | `/feed` | Browse curated news articles |
| **Analytics** | `/dashboard` | System statistics and monitoring |
| **Advanced** | `/advanced` | Advanced analysis tools |

---

## 🎮 Using the Application

### 1. Analyze News (Home Page)

1. Go to http://localhost:3000
2. Enter a news URL (or use the default)
3. Click "Start Analysis"
4. Watch the pipeline process:
   - 🌐 Fetching content
   - 🔍 Filtering data
   - 📝 Generating summary
   - ✓ Verifying authenticity
   - 📄 Creating script
   - 🔊 Generating audio

### 2. Live Dashboard Experience

1. Navigate to http://localhost:3000/live
2. View real-time news feed on the left
3. Click any news item to see:
   - Article details
   - Processing pipeline
   - TTS audio player
   - AI insights
   - Feedback options

### 3. Browse News Feed

1. Go to http://localhost:3000/feed
2. Search articles or filter by category
3. Click "Analyze with AI" on any article
4. Redirected to home with URL pre-filled

---

## 🔧 Common Tasks

### Toggle Mock Data

Edit `services/api.js`:
```javascript
// Use mock data (default)
apiService.setMockDataMode(true)

// Use real backend API
apiService.setMockDataMode(false)
```

### Add New News Categories

Edit `services/api.js`:
```javascript
const MOCK_CATEGORIES = [
  { id: 'technology', name: 'Technology', count: 45 },
  { id: 'your-category', name: 'Your Category', count: 10 }, // Add here
]
```

### Customize Theme Colors

Edit `app/globals.css`:
```css
:root {
  --primary-color: #a855f7;  /* Purple */
  --secondary-color: #ec4899; /* Pink */
}
```

---

## 🎨 Key Features to Try

### 1. TTS Audio Player
- Play/Pause audio summaries
- Adjust volume
- Seek through timeline
- Download audio
- Share functionality

### 2. AI Insights
- View sentiment analysis
- Check credibility scores
- See bias detection
- Explore keywords & entities

### 3. Feedback System
- Like quality content
- Skip irrelevant articles
- Approve verified news
- Flag problematic content

### 4. Pipeline Tracking
- Real-time status updates
- Visual progress indicators
- Timestamp tracking
- Error state handling

---

## 📊 Demo Data

The application includes rich demo data by default:
- 5 sample news articles
- Complete pipeline states
- AI insights and analytics
- Audio samples
- Feedback examples

Perfect for testing and demo purposes!

---

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Kill process on port 3000
npx kill-port 3000

# Or use different port
npm run dev -- -p 3001
```

### Module Not Found

```bash
# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

### Build Errors

```bash
# Clear Next.js cache
rm -rf .next
npm run dev
```

### Backend Connection Failed

The app will automatically use mock data if backend is unavailable. No action needed for testing!

---

## 💡 Tips & Tricks

### 1. Hot Reload
- Save any file to see changes instantly
- No need to restart server

### 2. Developer Tools
- Open browser DevTools (F12)
- Check Console for detailed logs
- Network tab shows API calls

### 3. Mock Data
- Perfect for frontend development
- No backend required
- Instant response times

### 4. Local Storage
- Feedback history stored locally
- Clear with: `localStorage.clear()`

---

## 📚 Next Steps

### Learn More
- Read [README.md](./README.md) for full documentation
- Check [FLOW_DIAGRAM.md](./FLOW_DIAGRAM.md) for architecture
- See [DEPLOYMENT.md](./DEPLOYMENT.md) for production setup

### Customize
- Modify components in `/components`
- Add pages in `/app`
- Update API service in `/services`

### Deploy
- Use Vercel for instant deployment
- Follow [DEPLOYMENT.md](./DEPLOYMENT.md) guide

---

## 🎯 Quick Commands Reference

```bash
# Development
npm run dev          # Start dev server
npm run build        # Build for production
npm start            # Run production build

# Quality
npm run lint         # Check code quality
npm run format       # Format code

# Utilities
npm run clean        # Clean build artifacts
npm run analyze      # Analyze bundle size
```

---

## ✨ Feature Highlights

### What Makes This Special?

1. **Zero Backend Required**
   - Works with mock data out of the box
   - Perfect for demos and development

2. **Real-Time Updates**
   - Live pipeline visualization
   - Instant feedback
   - Dynamic content loading

3. **AI-Powered**
   - Sentiment analysis
   - Credibility scoring
   - Bias detection
   - Entity recognition

4. **Beautiful UI**
   - Glass-morphism effects
   - Smooth animations
   - Responsive design
   - Dark mode optimized

5. **Interactive**
   - TTS audio player
   - Feedback system
   - Live feed updates
   - Category filtering

---

## 🎪 Demo Scenarios

### Scenario 1: News Analysis Demo
1. Open home page
2. Use default URL or paste your own
3. Click "Start Analysis"
4. Show pipeline stages
5. Play TTS audio
6. Review AI insights
7. Submit feedback

### Scenario 2: Live Dashboard Demo
1. Navigate to `/live`
2. Show live feed with multiple items
3. Filter by category
4. Click different news items
5. Demonstrate real-time updates
6. Play audio from different articles

### Scenario 3: News Feed Demo
1. Go to `/feed`
2. Search for topics
3. Filter by categories
4. Click "Analyze with AI"
5. Show seamless integration with analysis

---

## 🆘 Need Help?

### Resources
- 📖 [Full Documentation](./README.md)
- 🔄 [Flow Diagrams](./FLOW_DIAGRAM.md)
- 🚀 [Deployment Guide](./DEPLOYMENT.md)
- 🐛 [Issue Tracker](https://github.com/your-repo/issues)

### Support
- Email: support@blackholeinfiverse.com
- Discord: [Join Community](#)
- GitHub: [Create Issue](#)

---

## 🎉 You're Ready!

You now have a fully functional News AI Frontend running locally. Explore the features, customize as needed, and enjoy building!

**Happy Coding! 🚀**

---

*Quick Start Guide - Last Updated: November 2024*

