import React from 'react';
import { useNavigate } from 'react-router-dom';
import UseCaseList from './UseCaseList';
import { Button, Typography, Box } from '@mui/material';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();

  const handleNewEntry = () => {
    navigate('/usecases/new');
  };

  return (
    <Box sx={{ mt: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h4" component="h1">
          Use Case Dashboard
        </Typography>
        <Button variant="contained" color="primary" onClick={handleNewEntry}>
          New Use Case
        </Button>
      </Box>
      <UseCaseList />
    </Box>
  );
};

export default Dashboard;
