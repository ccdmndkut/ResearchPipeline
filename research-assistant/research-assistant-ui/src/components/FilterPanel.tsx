import React from 'react';
import { Box, TextField, Button, Paper } from '@mui/material';

interface FilterPanelProps {
  onSearch: (query: string) => void;
  filters: {
    minQuality: number;
    databases: string[];
    dateRange: string;
    minCitations: number;
  };
  onFiltersChange: (filters: any) => void;
}

const FilterPanel: React.FC<FilterPanelProps> = ({ onSearch, filters, onFiltersChange }) => {
  const [query, setQuery] = React.useState('');

  const handleSearch = () => {
    onSearch(query);
  };

  return (
    <Paper elevation={2} sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', gap: 2 }}>
        <TextField 
          fullWidth
          label="Enter your research query"
          variant="outlined"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
        />
        <Button variant="contained" onClick={handleSearch}>Search</Button>
      </Box>
    </Paper>
  );
};

export default FilterPanel;
