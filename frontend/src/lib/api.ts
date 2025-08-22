import axios from 'axios';

// Create axios instance for API calls
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 30000, // 30 seconds for file uploads
});

// Types for API responses
export interface ChatResponse {
  response: string;
}

export interface UploadResponse {
  message: string;
  files: string[];
}

// Chat API
export const sendMessage = async (prompt: string): Promise<ChatResponse> => {
  const response = await api.post('/chat/', { prompt });
  return response.data;
};

// File upload API with progress tracking
export const uploadFiles = async (
  files: File[], 
  onProgress?: (progress: number) => void
): Promise<UploadResponse> => {
  const formData = new FormData();
  
  files.forEach(file => {
    formData.append('files', file);
  });

  const response = await api.post('/upload/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent) => {
      if (progressEvent.total && onProgress) {
        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onProgress(progress);
      }
    },
  });

  return response.data;
};

export default api;