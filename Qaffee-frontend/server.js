import express from 'express';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import fs from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const PORT = process.env.PORT || 8080;

// Check if dist directory exists
const distPath = join(__dirname, 'dist');
if (!fs.existsSync(distPath)) {
  console.error('Error: dist directory not found. Please run npm run build first.');
  process.exit(1);
}

// Serve static files from the dist directory
app.use(express.static(distPath));

// Health check endpoint
app.get('/health', (req, res) => {
  // Check if index.html exists in dist
  if (fs.existsSync(join(distPath, 'index.html'))) {
    res.status(200).send('OK');
  } else {
    res.status(500).send('Error: Build files not found');
  }
});

// Basic error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).send('Something broke!');
});

// Serve index.html for all routes to support client-side routing
app.get('*', (req, res) => {
  res.sendFile(join(distPath, 'index.html'));
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server is running on port ${PORT}`);
  console.log(`Serving static files from: ${distPath}`);
}); 