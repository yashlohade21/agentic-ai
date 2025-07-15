# AI Agent System Frontend

A modern React frontend for the AI Agent System, built with Vite and featuring real-time chat interface, agent management, and comprehensive user experience.

## Features

- **Real-time Chat Interface**: Interactive chat with the AI agent system
- **Agent Status Monitoring**: Live view of active agents and their status
- **Message History**: Persistent conversation history with search and replay
- **Markdown Support**: Rich text rendering with syntax highlighting for code
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **WebSocket Integration**: Real-time updates and notifications
- **Modern UI**: Clean, intuitive interface with smooth animations

## Tech Stack

- **React 18** - Modern React with hooks
- **Vite** - Fast build tool and dev server
- **Axios** - HTTP client for API communication
- **Lucide React** - Beautiful icon library
- **React Markdown** - Markdown rendering with syntax highlighting
- **CSS3** - Modern styling with flexbox and grid

## Getting Started

### Prerequisites

- Node.js 16+ 
- npm or yarn
- Running AI Agent System backend

### Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create environment file:
```bash
cp .env.example .env
```

4. Configure environment variables in `.env`:
```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
```

5. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable React components
│   │   ├── AgentStatus.jsx  # Agent monitoring component
│   │   ├── ChatInput.jsx    # Chat input component
│   │   ├── MessageRenderer.jsx # Message display component
│   │   └── WelcomeMessage.jsx  # Welcome screen component
│   ├── api/                 # API service layer
│   │   └── agentApi.js      # Agent system API client
│   ├── App.jsx              # Main application component
│   ├── App.css              # Application styles
│   └── main.jsx             # Application entry point
├── public/                  # Static assets
├── .env                     # Environment variables
├── package.json             # Dependencies and scripts
└── README.md               # This file
```

## Components

### App.jsx
Main application component that orchestrates the entire frontend:
- Manages global state (messages, system status, UI state)
- Handles API communication
- Coordinates between child components

### MessageRenderer.jsx
Renders individual chat messages with:
- Markdown support with syntax highlighting
- Agent metadata display
- Different styling for user vs bot messages
- Code block rendering

### ChatInput.jsx
Handles user input with:
- Multi-line text support
- Keyboard shortcuts (Enter to send)
- Loading states
- Input validation

### AgentStatus.jsx
Displays real-time agent information:
- System status overview
- Individual agent metrics
- Activity indicators
- Performance statistics

### WelcomeMessage.jsx
Initial screen with:
- Welcome message
- Example prompts
- Quick start options

## API Integration

The frontend communicates with the backend through:

### REST API (`agentApi.js`)
- `processRequest()` - Send user requests
- `getSystemStatus()` - Get system health
- `getHistory()` - Retrieve conversation history
- `clearHistory()` - Clear conversation data
- `getAgentDetails()` - Get specific agent info

### WebSocket Connection
- Real-time status updates
- Live agent activity monitoring
- Instant notifications

## Styling

The application uses modern CSS with:
- CSS Grid and Flexbox for layouts
- CSS Variables for theming
- Smooth animations and transitions
- Responsive design patterns
- Custom scrollbars
- Focus states for accessibility

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### Environment Variables

- `VITE_API_URL` - Backend API URL (default: http://localhost:8000)
- `VITE_WS_URL` - WebSocket URL (default: ws://localhost:8000/ws)

### Code Style

- Use functional components with hooks
- Follow React best practices
- Maintain component separation of concerns
- Use descriptive variable and function names
- Add comments for complex logic

## Deployment

### Production Build

```bash
npm run build
```

This creates a `dist/` directory with optimized production files.

### Deployment Options

- **Static Hosting**: Deploy `dist/` to Netlify, Vercel, or GitHub Pages
- **Docker**: Use the included Dockerfile for containerized deployment
- **Traditional Hosting**: Upload `dist/` contents to any web server

### Environment Configuration

For production, update environment variables:
```env
VITE_API_URL=https://your-api-domain.com
VITE_WS_URL=wss://your-api-domain.com/ws
```

## Features in Detail

### Chat Interface
- Real-time messaging with the AI agent system
- Support for complex multi-agent workflows
- Message history with timestamps
- Loading indicators and error handling

### Agent Management
- Live status monitoring for all agents
- Performance metrics and activity tracking
- Visual indicators for agent states
- Detailed agent information

### User Experience
- Responsive design for all screen sizes
- Keyboard shortcuts and accessibility
- Smooth animations and transitions
- Intuitive navigation and controls

### Technical Features
- WebSocket integration for real-time updates
- Markdown rendering with syntax highlighting
- Error handling and retry mechanisms
- Optimized performance and loading

## Troubleshooting

### Common Issues

**Frontend won't start:**
- Check Node.js version (16+)
- Run `npm install` to ensure dependencies
- Verify `.env` file exists and is configured

**Can't connect to backend:**
- Ensure backend is running on correct port
- Check `VITE_API_URL` in `.env`
- Verify CORS settings in backend

**WebSocket connection fails:**
- Check `VITE_WS_URL` configuration
- Ensure backend WebSocket endpoint is available
- Check browser console for connection errors

### Development Tips

- Use browser dev tools for debugging
- Check network tab for API call issues
- Monitor console for JavaScript errors
- Use React Developer Tools extension

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of the AI Agent System and follows the same license terms.
