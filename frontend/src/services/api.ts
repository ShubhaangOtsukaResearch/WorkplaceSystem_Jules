// TODO: Define the base URL for the backend API, e.g., from an environment variable
const API_BASE_URL = 'http://localhost:5000'; // Assuming backend runs on port 5000

export interface UseCase { // Exporting for potential use in components
  id?: number;
  title: string;
  requestor: string;
  description: string;
  rationale: string;
  stage: string;
  reviewed_by_ai_committee: boolean;
  date_updated?: string; // ISO string
  updated_by?: string;
}

export interface UseCaseFormData {
  title: string;
  requestor: string;
  description: string;
  rationale: string;
  stage: string;
  reviewed_by_ai_committee: boolean;
}

// Helper function to get the token from local storage
const getToken = (): string | null => localStorage.getItem('ssoToken');

// Helper function for making API requests
const apiRequest = async (url: string, method: string, body?: any, isProtected: boolean = true) => {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };

  if (isProtected) {
    const token = getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    } else {
      console.error('API call to protected route without token.');
      // Optionally, you could throw an error here or handle redirection globally
      // For now, let's assume the backend will catch this and return a 401
    }
  }

  const config: RequestInit = {
    method,
    headers,
  };

  if (body) {
    config.body = JSON.stringify(body);
  }

  const response = await fetch(`${API_BASE_URL}${url}`, config);

  if (!response.ok) {
    let errorData;
    try {
        errorData = await response.json();
    } catch (e) {
        errorData = { error: `HTTP error! Status: ${response.status} ${response.statusText}` };
    }
    throw new Error(errorData.error || `API request failed with status ${response.status}`);
  }

  if (response.status === 204) { // No Content
    return null;
  }
  return response.json();
};

// API functions
export const login = async (username_param: string, password_param: string): Promise<{ message: string, sso_token: string }> => {
  return apiRequest('/login', 'POST', { username: username_param, password: password_param }, false);
};

export const getUseCases = async (): Promise<UseCase[]> => {
  return apiRequest('/use_cases', 'GET');
};

export const getUseCaseById = async (id: number | string): Promise<UseCase> => {
  return apiRequest(`/use_cases/${id}`, 'GET');
};

export const createUseCase = async (data: UseCaseFormData): Promise<{ message: string, id: number }> => {
  return apiRequest('/use_cases', 'POST', data);
};

export const updateUseCase = async (id: number | string, data: Partial<UseCaseFormData>): Promise<{ message: string }> => {
  return apiRequest(`/use_cases/${id}`, 'PUT', data);
};

export const deleteUseCase = async (id: number | string): Promise<null> => {
  return apiRequest(`/use_cases/${id}`, 'DELETE');
};
