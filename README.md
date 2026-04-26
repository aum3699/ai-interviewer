# AI Interviewer - Modern SaaS Frontend

A modern, professional web application frontend for an AI-powered interview platform with a sleek gradient design and glassmorphism UI.

## 🎨 Design Features

- **Theme**: Soft purple + blue gradient color scheme
- **Style**: Modern SaaS dashboard with glassmorphism effects
- **Typography**: Clean sans-serif fonts (Inter/Poppins)
- **Components**: Cards, buttons, toggles, charts, progress bars
- **Responsive**: Fully responsive design for all screen sizes
- **Animations**: Subtle hover effects and entrance animations

## 📁 Project Structure

```
.
├── index.html          # Landing page with hero section
├── dashboard.html      # Main dashboard with stats and charts
├── interview.html      # Live interview room interface
├── results.html        # Interview results and feedback
├── myinterviews.html   # User's interview history
├── profile.html        # User profile and settings
├── css/
│   └── styles.css      # Main stylesheet with glassmorphism
└── js/
    └── script.js       # Interactive JavaScript functionality
```

## 🌟 Key Components

### Landing Page (`index.html`)
- Hero section with AI robot illustration
- Feature cards with icons
- CTA buttons and smooth scrolling navigation

### Dashboard (`dashboard.html`)
- Stats cards with gradient numbers
- Performance chart (canvas-based)
- Recent interviews table
- Quick action buttons

### Interview Room (`interview.html`)
- Dark mode interface
- Video panels for candidates
- Audio waveform visualization
- Progress circle indicator
- Control buttons (mic, camera, end call)

### Results Page (`results.html`)
- Score circle visualization
- Star rating display
- Detailed breakdown bars
- Strengths and areas to improve
- Download report functionality

### My Interviews (`myinterviews.html`)
- Filterable interview table
- Sort by role and time period
- View report actions

### Profile Settings (`profile.html`)
- Personal information form
- Toggle switches for preferences
- Password change section

## 🎯 Technologies Used

- **HTML5**: Semantic structure and accessibility
- **CSS3**: 
  - CSS Grid and Flexbox layouts
  - Gradient backgrounds
  - Backdrop blur effects (glassmorphism)
  - Custom properties (CSS variables)
  - Responsive design with media queries
- **JavaScript**: 
  - DOM manipulation
  - Event handling
  - Canvas API for charts
  - Smooth animations
- **Font Awesome**: Icons for UI elements

## 📱 Responsive Design

- Mobile-first approach
- Flexible grid layouts
- Collapsible navigation menu
- Touch-friendly controls
- Optimized for all screen sizes

## 🎨 Design System

### Color Palette
- **Primary**: Purple (#7b4bdb) to Blue (#2563eb) gradient
- **Background**: Light gradient (#f8f9fa → #e6ddf7 → #d0e8ff)
- **Cards**: Semi-transparent white with blur effect
- **Text**: Dark primary with secondary gray tones

### Spacing System
- Container max-width: 1200px
- Section padding: 4rem vertical
- Card padding: 2rem
- Border radius: var(--radius-sm to --radius-xl)

## 🚀 Getting Started

1. Clone or download the project files
2. Open `index.html` in a web browser
3. Navigate through pages using the navigation menu
4. Test interactive elements and animations

## 🛠️ Customization

### Colors
Modify the CSS variables in `css/styles.css`:
```css
:root {
    --purple-dark: #7b4bdb;
    --blue-dark: #2563eb;
    --bg-primary: #f8f9fa;
}
```

### Typography
- Primary: Inter (fallback: system sans-serif)
- Headings: Bold weight (700)
- Body: Regular weight (400)

### Components
- Adjust card shadows with `--shadow` variables
- Modify border radius values
- Customize animation timing

## 🌈 Features

- **Modern UI**: Glassmorphism cards with subtle shadows
- **Smooth Animations**: Fade-in effects on scroll
- **Interactive Elements**: Hover states and transitions
- **Chart Visualization**: Canvas-based performance charts
- **Form Controls**: Styled inputs and toggles
- **Video Interface**: Mock camera/video panels
- **Accessibility**: Semantic HTML structure

## 📊 Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## 💡 Pro Tips

1. **Performance**: Canvas charts are optimized for smooth rendering
2. **Accessibility**: Semantic HTML structure for screen readers
3. **Maintainability**: CSS variables for easy theming
4. **Scalability**: Component-based structure for easy expansion

## 📝 Future Enhancements

- Integrate with backend API
- Add real-time video streaming
- Implement actual AI feedback system
- User authentication flow
- Mobile app version

## 🔗 Resources

- Font Awesome Icons: https://fontawesome.com
- CSS Variables: https://developer.mozilla.org/en-US/docs/Web/CSS/Using_CSS_custom_properties
- CSS Backdrop Filter: https://developer.mozilla.org/en-US/docs/Web/CSS/backdrop_filter

## ⚠️ Notes

- This is a frontend-only implementation
- JavaScript functionality includes basic interactivity
- Charts are rendered using HTML5 Canvas
- All data is mock/sample data for demonstration
- To connect to backend, API endpoints need to be configured