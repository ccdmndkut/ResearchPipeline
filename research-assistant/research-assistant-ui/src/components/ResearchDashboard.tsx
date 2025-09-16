import React, { useState } from 'react';
import { Box, Grid } from '@mui/material';
import FilterPanel from './FilterPanel';
import ResultsList from './ResultsList';
import VisualizationPanel from './VisualizationPanel';
// import { useResearch } from '../hooks/useResearch'; // This will be enabled later

const ResearchDashboard: React.FC = () => {
  // const { search, results, loading, progress, qualityScores } = useResearch();
  const [view, setView] = useState<'cards' | 'list' | 'graph'>('cards');
  const [filters, setFilters] = useState({
    minQuality: 0.7,
    databases: ['arxiv', 'pubmed'],
    dateRange: 'last_year',
    minCitations: 0
  });

  const handleSearch = (query: string) => {
    // search({ query, filters });
    console.log('Searching for:', query, 'with filters:', filters);
  };

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <FilterPanel 
            onSearch={handleSearch}
            filters={filters}
            onFiltersChange={setFilters}
          />
        </Grid>
        
        {/* {loading && (
          <Grid item xs={12}>
            <ProgressTracker 
              progress={progress}
              activeAgents={['search', 'summarizer']}
            />
          </Grid>
        )} */}
        
        <Grid item xs={12} md={8}>
          <ResultsList 
            // results={results}
            view={view}
            onViewChange={setView}
            // qualityScores={qualityScores}
          />
        </Grid>
        
        <Grid item xs={12} md={4}>
          <VisualizationPanel 
            // data={results}
            type="citation_network"
          />
        </Grid>
      </Grid>
    </Box>
  );
};

export default ResearchDashboard;
