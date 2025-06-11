```tsx
import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { getUseCaseById, createUseCase, updateUseCase, UseCase as UseCaseType } from '../services/api'; // Renamed UseCase to UseCaseType to avoid conflict
import {
  TextField, Button, Typography, Paper, Grid, Box, Alert, CircularProgress,
  Select, MenuItem, FormControl, InputLabel, RadioGroup, FormControlLabel, Radio
} from '@mui/material';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';

interface UseCaseFormData {
  title: string;
  requestor: string;
  description: string;
  rationale: string;
  stage: string;
  reviewed_by_ai_committee: boolean;
}

// Using UseCaseType from api.ts to avoid redefinition and potential inconsistencies
// interface UseCaseFromServer {
//   id: number;
//   title: string;
//   requestor: string;
//   description: string;
//   rationale: string;
//   stage: string;
//   reviewed_by_ai_committee: boolean;
//   date_updated: string;
//   updated_by: string;
// }

const STAGE_OPTIONS = ["Idea", "Validation", "Development", "Deployment", "Archive"];

const UseCaseForm: React.FC = () => {
  const { id } = useParams<{ id?: string }>();
  const navigate = useNavigate();
  const [formData, setFormData] = useState<UseCaseFormData>({
    title: '',
    requestor: '',
    description: '',
    rationale: '',
    stage: STAGE_OPTIONS[0],
    reviewed_by_ai_committee: false,
  });
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const [dateUpdated, setDateUpdated] = useState<Date | null>(null);
  const [updatedBy, setUpdatedBy] = useState<string | null>(null);

  const isEditMode = Boolean(id);

  const fetchAndSetData = useCallback(async (useCaseId: string) => {
    setIsLoading(true);
    try {
      const data: UseCaseType = await getUseCaseById(useCaseId);
      setFormData({
        title: data.title,
        requestor: data.requestor,
        description: data.description,
        rationale: data.rationale,
        stage: data.stage,
        reviewed_by_ai_committee: data.reviewed_by_ai_committee,
      });
      if (data.date_updated) {
        setDateUpdated(new Date(data.date_updated));
      }
      setUpdatedBy(data.updated_by || null);
      setError(null);
    } catch (err: any) {
      setError(err.message || `Failed to fetch use case with id ${useCaseId}.`);
       if (err.message.includes("401") || err.message.toLowerCase().includes("token")) {
          localStorage.removeItem('ssoToken');
          localStorage.removeItem('isAuthenticated');
          navigate('/login');
      }
    } finally {
      setIsLoading(false);
    }
  }, [navigate]);

  useEffect(() => {
    if (id) {
      fetchAndSetData(id);
    }
  }, [id, fetchAndSetData]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | { name?: string; value: unknown }>) => {
    const target = e.target as HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement;
    const name = target.name;
    let value: string | boolean = target.value;

    // Check if the event target has a 'type' property to avoid errors with SelectChangeEvent
    const targetType = (target as HTMLInputElement).type;

    if (name === 'reviewed_by_ai_committee') {
        value = (target as HTMLInputElement).value === 'true';
    } else if (targetType === 'checkbox') {
        value = (target as HTMLInputElement).checked;
    }

    setFormData(prev => ({ ...prev, [name!]: value }));
  };

  const handleDateChange = (newDate: Date | null) => {
    setDateUpdated(newDate);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    const dataToSubmit: UseCaseFormData = { ...formData };

    try {
      if (isEditMode && id) {
        await updateUseCase(id, dataToSubmit);
      } else {
        await createUseCase(dataToSubmit);
      }
      navigate('/');
    } catch (err: any) {
      setError(err.message || 'Failed to save use case.');
      if (err.message.includes("401") || err.message.toLowerCase().includes("token")) {
        localStorage.removeItem('ssoToken');
        localStorage.removeItem('isAuthenticated');
        navigate('/login');
      }
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading && isEditMode) return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}><CircularProgress /></Box>;

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Paper sx={{ p: 3, mt: 2 }}>
        <Typography variant="h5" component="h2" gutterBottom>
          {isEditMode ? 'Edit Use Case' : 'Create New Use Case'}
        </Typography>
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 3 }}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                name="title"
                label="Title"
                value={formData.title}
                onChange={handleChange}
                fullWidth
                required
                disabled={isLoading}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                name="requestor"
                label="Requestor"
                value={formData.requestor}
                onChange={handleChange}
                fullWidth
                required
                disabled={isLoading}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth required disabled={isLoading}>
                <InputLabel id="stage-label">Stage</InputLabel>
                <Select
                  labelId="stage-label"
                  id="stage"
                  name="stage"
                  value={formData.stage}
                  label="Stage"
                  onChange={handleChange as any} // Cast to any for SelectChangeEvent
                >
                  {STAGE_OPTIONS.map(option => (
                    <MenuItem key={option} value={option}>{option}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                name="description"
                label="Description"
                value={formData.description}
                onChange={handleChange}
                fullWidth
                required
                multiline
                rows={4}
                disabled={isLoading}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                name="rationale"
                label="Rationale"
                value={formData.rationale}
                onChange={handleChange}
                fullWidth
                required
                multiline
                rows={4}
                disabled={isLoading}
              />
            </Grid>
            <Grid item xs={12}>
              <FormControl component="fieldset" disabled={isLoading}>
                <FormLabel component="legend">Reviewed by AI Committee?</FormLabel>
                <RadioGroup
                  row
                  aria-label="reviewed_by_ai_committee"
                  name="reviewed_by_ai_committee"
                  value={formData.reviewed_by_ai_committee.toString()}
                  onChange={handleChange}
                >
                  <FormControlLabel value="true" control={<Radio />} label="Yes" />
                  <FormControlLabel value="false" control={<Radio />} label="No" />
                </RadioGroup>
              </FormControl>
            </Grid>

            {isEditMode && (
              <>
                <Grid item xs={12} sm={6}>
                  <DatePicker
                    label="Date Updated"
                    value={dateUpdated}
                    onChange={handleDateChange}
                    readOnly
                    slotProps={{ textField: { fullWidth: true, disabled: true } }}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    name="updated_by"
                    label="Updated By"
                    value={updatedBy || ''}
                    fullWidth
                    InputProps={{
                      readOnly: true,
                    }}
                    disabled={true}
                  />
                </Grid>
              </>
            )}
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
                <Button onClick={() => navigate('/')} sx={{ mr: 1 }} disabled={isLoading}>
                  Cancel
                </Button>
                <Button type="submit" variant="contained" color="primary" disabled={isLoading}>
                  {isLoading ? <CircularProgress size={24} /> : (isEditMode ? 'Update Use Case' : 'Create New Use Case')}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </Box>
      </Paper>
    </LocalizationProvider>
  );
};

export default UseCaseForm;
```
