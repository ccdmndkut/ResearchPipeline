import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

interface ResultsListProps {
  view: 'cards' | 'list' | 'graph';
  onViewChange: (view: 'cards' | 'list' | 'graph') => void;
}

const ResultsList: React.FC<ResultsListProps> = ({ view, onViewChange }) => {
  return (
    <Paper elevation={2} sx={{ p: 2 }}>
      <Typography variant="h6">Results</Typography>
      <Typography>View: {view}</Typography>
      {/* Results will be displayed here */}
    </Paper>
  );
};

export default ResultsList;
