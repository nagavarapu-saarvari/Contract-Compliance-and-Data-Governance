# React Frontend for Contract Compliance & Data Governance

This is the React-based user interface for the Contract Compliance & Data Governance application built with FastAPI.

## Project Structure

```
frontend/
├── public/
│   └── index.html       # Main HTML template
├── src/
│   ├── components/      # React components
│   │   ├── PdfUpload.js         # PDF rule generation
│   │   ├── PythonCheck.js       # Python compliance checking
│   │   └── RulesView.js         # View stored rules
│   ├── services/
│   │   └── apiService.js        # API communication
│   ├── App.js           # Main App component
│   ├── App.css          # Styling
│   ├── index.js         # React entry point
│   └── index.css        # Global styles
├── package.json         # Dependencies
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## Features

✨ **Three Main React Components:**

1. **PdfUpload.js** - Upload and process contract PDFs
2. **PythonCheck.js** - Check Python files for compliance
3. **RulesView.js** - View all generated rules from database

## Prerequisites

- Node.js 14+ and npm (or yarn)
- FastAPI backend running on `http://localhost:8000`

## Installation

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure API URL (Optional)

By default, the app connects to `http://localhost:8000/api`. To use a different URL:

Create a `.env` file in the frontend directory:
```env
REACT_APP_API_URL=http://your-api-url:8000/api
```

## Development

### Start Development Server

```bash
npm start
```

The app will open at `http://localhost:3000` with hot reload enabled.

### Build for Production

```bash
npm run build
```

This creates an optimized build in the `build/` directory, which FastAPI will serve.

## Usage

### Three Tabs

1. **Generate Rules (PDF)**
   - Drag and drop or click to select a PDF file
   - System processes the contract and extracts rules
   - Rules are automatically stored in the database
   - Results displayed in a formatted list

2. **Check Compliance (Python)**
   - Upload a Python file
   - System scans for suspicious patterns
   - Checks against stored governance rules
   - Shows violations and warnings

3. **View Rules**
   - Displays all rules stored in the database
   - Click "Refresh Rules" to reload
   - Shows complete rule details

## Component Details

### PdfUpload.js
- Handles PDF file uploads
- Drag-and-drop support
- Calls `/api/process-pdf` endpoint
- Displays generated rules

### PythonCheck.js
- Handles Python file uploads
- Analyzes code for compliance
- Calls `/api/check-compliance` endpoint
- Shows suspicious blocks and violations

### RulesView.js
- Fetches all rules on mount
- Calls `/api/rules` endpoint
- Displays rules in formatted cards
- Refresh functionality

### apiService.js
- Centralized API communication
- Uses Axios for HTTP requests
- Handles multipart form data for file uploads
- All endpoint methods:
  - `health()` - Health check
  - `processPdf(file)` - Process PDF
  - `checkCompliance(file)` - Check Python file
  - `getRules()` - Get all rules

## Styling

The application uses:
- CSS3 with CSS Variables for theming
- Responsive design for mobile/tablet/desktop
- Smooth animations and transitions
- Color scheme:
  - Primary: #0066cc (Blue)
  - Success: #28a745 (Green)
  - Error: #dc3545 (Red)
  - Warning: #ffc107 (Yellow)

### Responsive Breakpoints
- Tablet: 768px
- Mobile: 480px

## Backend Integration

The React app communicates with FastAPI at `/api/`:

```javascript
// API Service
const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Endpoints
POST /api/process-pdf       // Process PDF contracts
POST /api/check-compliance  // Check Python files
GET /api/rules              // Retrieve all rules
GET /api/health             // Health check
```

## Building and Deployment

### Development Build
```bash
npm start
```

### Production Build
```bash
npm run build
```

The build output goes to the `frontend/build` directory. FastAPI will serve these files automatically.

### Full Stack With FastAPI

1. Build the React app:
```bash
cd frontend
npm run build
cd ..
```

2. Run FastAPI server:
```bash
python app.py
```

3. Access at `http://localhost:8000`

## Environment Variables

Create `.env` file in the frontend directory:

```env
# API URL (optional, defaults to http://localhost:8000/api)
REACT_APP_API_URL=http://localhost:8000/api
```

## Available Scripts

### `npm start`
Runs the app in development mode at http://localhost:3000

### `npm run build`
Builds the app for production to the `build` folder

### `npm test`
Runs the test suite (if tests are added)

### `npm run eject`
Exposes all configuration (one-way operation, not recommended)

## Troubleshooting

### Module Not Found
```bash
npm install
```

### Port 3000 Already in Use
```bash
# Use a different port
PORT=3001 npm start
```

### API Connection Error
1. Ensure FastAPI server is running on `http://localhost:8000`
2. Check `.env` for correct `REACT_APP_API_URL`
3. Verify CORS is enabled in FastAPI app

### Build Fails
```bash
# Clear dependencies and reinstall
rm -rf node_modules
npm install
npm run build
```

## Performance Optimizations

- Code splitting for faster initial load
- Lazy loading of components
- Optimized CSS with variables
- Efficient state management
- Memoized components where applicable

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Modern browsers with ES6 support

## Development Tips

1. **Component Structure**: Each component is self-contained with its own state
2. **API Calls**: Use centralized `apiService.js` for all API communication
3. **Error Handling**: All components handle errors gracefully
4. **Loading States**: Visual feedback during API calls
5. **Responsive Design**: Mobile-first approach

## Future Enhancements

- Add authentication/login
- User dashboard with history
- Real-time file analysis
- Advanced filtering and search
- Export compliance reports
- Notifications/alerts
- Theme switching (light/dark mode)
- Multi-language support

## Dependencies

- **react**: ^18.2.0 - UI library
- **react-dom**: ^18.2.0 - React DOM rendering
- **axios**: ^1.6.0 - HTTP client
- **react-scripts**: 5.0.1 - Build tools

## Learn More

- [Create React App Documentation](https://create-react-app.dev)
- [React Documentation](https://react.dev)
- [Axios Documentation](https://axios-http.com)
- [FastAPI Documentation](https://fastapi.tiangolo.com)

## License

(Add your license information here)

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review component code comments
3. Check browser console for errors
4. Verify FastAPI backend is running

---

**Built with ❤️ using React and Vite** 

Last Updated: February 27, 2026
