import React from 'react';
import { CssBaseline, AppBar, Toolbar, Typography, Container } from '@mui/material';
import ResearchDashboard from './components/ResearchDashboard';

function App() {
  return (
    <div>
      <CssBaseline />
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            AI Research Assistant
          </Typography>
        </Toolbar>
      </AppBar>
      <Container maxWidth="xl" sx={{ mt: 4 }}>
        <ResearchDashboard />
      </Container>
    </div>
  );
}

export default App;
