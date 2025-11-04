export interface Cat {
  id: number;
  name: string;
  breed?: string;
  age?: number;
  color?: string;
  weight?: string;
  is_neutered: boolean;
  owner_name?: string;
  adoption_date?: string;
  description?: string;
  created_at: string;
  is_adopted: boolean;
  age_display: string;
  weight_display: string;
  status_display: string;
}

export interface CatCreate {
  name: string;
  breed?: string;
  age?: number;
  color?: string;
  weight?: number;
  is_neutered?: boolean;
  description?: string;
}

export interface CatListResponse {
  count: number;
  next?: string;
  previous?: string;
  results: Cat[];
}

export interface CatStatistics {
  total_cats: number;
  adopted_cats: number;
  available_cats: number;
  adoption_rate: number;
  average_age: number;
  youngest_age: number;
  oldest_age: number;
  neutered_cats: number;
  breeds_count: number;
  recent_adoptions: number;
}

export interface BreedStatistics {
  breed: string;
  count: number;
  adoption_rate: number;
  average_age: number;
  average_weight: number;
}

export interface ApiResponse<T> {
  status: string;
  message?: string;
  data?: T;
  errors?: Record<string, string[]>;
}