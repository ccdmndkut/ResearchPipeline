import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

interface VisualizationPanelProps {
  type: string;
}

const VisualizationPanel: React.FC<VisualizationPanelProps> = ({ type }) => {
  return (
    <Paper elevation={2} sx={{ p: 2 }}>
      <Typography variant="h6">Visualization</Typography>
      <Typography>Type: {type}</Typography>
      {/* Visualization will be displayed here */}
    </Paper>
  );
};

export default VisualizationPanel;
