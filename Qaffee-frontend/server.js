import express from 'express';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const PORT = process.env.PORT || 8080;

// Serve static files from the dist directory
app.use(express.static(join(__dirname, 'dist')));

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).send('OK');
});

// Serve index.html for all routes to support client-side routing
app.get('*', (req, res) => {
  res.sendFile(join(__dirname, 'dist', 'index.html'));
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server is running on port ${PORT}`);
}); 