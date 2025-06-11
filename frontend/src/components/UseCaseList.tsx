import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { getUseCases, deleteUseCase, UseCase } from '../services/api'; // Import UseCase interface
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  Box,
  Alert,
  IconButton,
  CircularProgress
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';

const UseCaseList: React.FC = () => {
  const [useCases, setUseCases] = useState<UseCase[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const navigate = useNavigate();

  const fetchUseCases = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await getUseCases();
      setUseCases(data);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch use cases.');
      if (err.message.includes("401") || err.message.toLowerCase().includes("token") || err.message.toLowerCase().includes("unauthorized")) {
          localStorage.removeItem('ssoToken');
          localStorage.removeItem('isAuthenticated');
          navigate('/login');
      }
    } finally {
      setIsLoading(false);
    }
  }, [navigate]);

  useEffect(() => {
    fetchUseCases();
  }, [fetchUseCases]);

  const handleEdit = (id: number) => {
    navigate(`/usecases/edit/${id}`);
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this use case?')) {
      setIsLoading(true);
      try {
        await deleteUseCase(id);
        await fetchUseCases();
      } catch (err: any) {
        setError(err.message || 'Failed to delete use case.');
      } finally {
        setIsLoading(false);
      }
    }
  };

  if (isLoading && useCases.length === 0) {
    return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}><CircularProgress /></Box>;
  }

  if (error) {
    return <Alert severity="error" sx={{ mt: 2 }}>Error: {error}</Alert>;
  }

  return (
    <Paper sx={{ width: '100%', overflow: 'hidden', mt: 2 }}>
      {isLoading && <CircularProgress size={24} sx={{position: 'absolute', top: '50%', left: '50%', zIndex: 1}}/>}
      {useCases.length === 0 && !isLoading && (
        <Typography variant="subtitle1" sx={{ p: 2 }}>
          No use cases found. Click "New Use Case" in the dashboard header to add one.
        </Typography>
      )}
      {useCases.length > 0 && (
        <TableContainer>
          <Table stickyHeader aria-label="use cases table">
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>Title</TableCell>
                <TableCell>Requestor</TableCell>
                <TableCell>Stage</TableCell>
                <TableCell>Reviewed by AI Committee</TableCell>
                <TableCell>Last Updated</TableCell>
                <TableCell>Updated By</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {useCases.map((uc) => (
                <TableRow hover role="checkbox" tabIndex={-1} key={uc.id}>
                  <TableCell>{uc.id}</TableCell>
                  <TableCell>{uc.title}</TableCell>
                  <TableCell>{uc.requestor}</TableCell>
                  <TableCell>{uc.stage}</TableCell>
                  <TableCell>{uc.reviewed_by_ai_committee ? 'Yes' : 'No'}</TableCell>
                  <TableCell>{new Date(uc.date_updated!).toLocaleDateString()}</TableCell>
                  <TableCell>{uc.updated_by}</TableCell>
                  <TableCell align="right">
                    <IconButton onClick={() => handleEdit(uc.id!)} color="primary" aria-label="edit use case">
                      <EditIcon />
                    </IconButton>
                    <IconButton onClick={() => handleDelete(uc.id!)} color="secondary" aria-label="delete use case" disabled={isLoading}>
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Paper>
  );
};

export default UseCaseList;
