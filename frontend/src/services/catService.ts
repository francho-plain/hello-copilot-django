import axios from 'axios';
import { Cat, CatCreate, CatListResponse, CatStatistics, BreedStatistics } from '../types/Cat';

const API_BASE_URL = 'http://localhost:8000/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const catService = {
  // Get all cats with optional filtering
  async getCats(params?: {
    page?: number;
    search?: string;
    status?: 'available' | 'adopted';
    breed?: string;
    neutered?: boolean;
    min_age?: number;
    max_age?: number;
  }): Promise<CatListResponse> {
    const response = await api.get('/cats/', { params });
    return response.data;
  },

  // Get a single cat by ID
  async getCat(id: number): Promise<Cat> {
    const response = await api.get(`/cats/${id}/`);
    return response.data;
  },

  // Create a new cat
  async createCat(catData: CatCreate): Promise<{ status: string; message: string; cat: Cat }> {
    const response = await api.post('/cats/', catData);
    return response.data;
  },

  // Update a cat
  async updateCat(id: number, catData: Partial<CatCreate>): Promise<Cat> {
    const response = await api.patch(`/cats/${id}/`, catData);
    return response.data;
  },

  // Delete a cat
  async deleteCat(id: number): Promise<void> {
    await api.delete(`/cats/${id}/`);
  },

  // Adopt a cat
  async adoptCat(id: number, adoptionData: { owner_name: string; adoption_date?: string }): Promise<{
    status: string;
    message: string;
    cat: Cat;
  }> {
    const response = await api.post(`/cats/${id}/adopt/`, adoptionData);
    return response.data;
  },

  // Get statistics
  async getStatistics(): Promise<CatStatistics> {
    const response = await api.get('/cats/statistics/');
    return response.data;
  },

  // Get breed statistics
  async getBreeds(): Promise<BreedStatistics[]> {
    const response = await api.get('/cats/breeds/');
    return response.data;
  },

  // Search cats
  async searchCats(query: string): Promise<CatListResponse> {
    const response = await api.get('/cats/search/', { params: { q: query } });
    return response.data;
  },
};

export default catService;