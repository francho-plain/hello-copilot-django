import React, { useState, useEffect, useCallback } from 'react';
import { Cat, CatListResponse } from '../types/Cat';
import catService from '../services/catService';
import styles from '../styles/CatList.module.css';

interface CatListProps {
  onAddNew: () => void;
}

const CatList: React.FC<CatListProps> = ({ onAddNew }) => {
  const [cats, setCats] = useState<Cat[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'available' | 'adopted'>('all');
  const [breedFilter, setBreedFilter] = useState('');

  const fetchCats = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const params: any = { page: currentPage };
      
      if (searchTerm) params.search = searchTerm;
      if (statusFilter !== 'all') params.status = statusFilter;
      if (breedFilter) params.breed = breedFilter;

      const response: CatListResponse = await catService.getCats(params);
      setCats(response.results);
      setTotalCount(response.count);
    } catch (err) {
      setError('Failed to fetch cats. Please try again.');
      console.error('Error fetching cats:', err);
    } finally {
      setLoading(false);
    }
  }, [currentPage, searchTerm, statusFilter, breedFilter]);

  useEffect(() => {
    fetchCats();
  }, [fetchCats]);

  const handleAdopt = async (catId: number) => {
    const ownerName = prompt('Enter the new owner\'s name:');
    if (!ownerName) return;

    try {
      await catService.adoptCat(catId, { owner_name: ownerName });
      fetchCats(); // Refresh the list
    } catch (err) {
      alert('Failed to adopt cat. Please try again.');
      console.error('Error adopting cat:', err);
    }
  };

  const handleDelete = async (catId: number, catName: string) => {
    if (!window.confirm(`Are you sure you want to delete ${catName}? This action cannot be undone.`)) {
      return;
    }

    try {
      await catService.deleteCat(catId);
      fetchCats(); // Refresh the list
    } catch (err) {
      alert('Failed to delete cat. Please try again.');
      console.error('Error deleting cat:', err);
    }
  };

  const resetFilters = () => {
    setSearchTerm('');
    setStatusFilter('all');
    setBreedFilter('');
    setCurrentPage(1);
  };

  if (loading && cats.length === 0) {
    return <div className={styles.loading}>Loading cats... 🐱</div>;
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h2 className={styles.title}>All Cats ({totalCount})</h2>
        <button className={styles.addButton} onClick={onAddNew}>
          + Add New Cat
        </button>
      </div>

      <div className={styles.filters}>
        <div className={styles.filterGroup}>
          <label className={styles.filterLabel}>Search</label>
          <input
            type="text"
            className={styles.filterInput}
            placeholder="Search by name, breed, or description..."
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              setCurrentPage(1);
            }}
          />
        </div>

        <div className={styles.filterGroup}>
          <label className={styles.filterLabel}>Status</label>
          <select
            className={styles.filterSelect}
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value as 'all' | 'available' | 'adopted');
              setCurrentPage(1);
            }}
          >
            <option value="all">All</option>
            <option value="available">Available</option>
            <option value="adopted">Adopted</option>
          </select>
        </div>

        <div className={styles.filterGroup}>
          <label className={styles.filterLabel}>Breed</label>
          <input
            type="text"
            className={styles.filterInput}
            placeholder="Filter by breed..."
            value={breedFilter}
            onChange={(e) => {
              setBreedFilter(e.target.value);
              setCurrentPage(1);
            }}
          />
        </div>

        <div className={styles.filterGroup}>
          <label className={styles.filterLabel}>&nbsp;</label>
          <button
            className={styles.addButton}
            onClick={resetFilters}
            style={{ fontSize: '0.9rem', padding: '0.5rem 1rem' }}
          >
            Reset Filters
          </button>
        </div>
      </div>

      {error && <div className={styles.error}>{error}</div>}

      {cats.length === 0 ? (
        <div className={styles.emptyState}>
          <div className={styles.emptyIcon}>🐱</div>
          <h3 className={styles.emptyMessage}>No cats found</h3>
          <p>Try adjusting your filters or add a new cat to get started.</p>
        </div>
      ) : (
        <div className={styles.grid}>
          {cats.map((cat) => (
            <div key={cat.id} className={styles.card}>
              <h3 className={styles.catName}>{cat.name}</h3>
              
              <div className={styles.catDetails}>
                <div className={styles.detail}>
                  <span className={styles.detailLabel}>Breed:</span>
                  <span className={styles.detailValue}>{cat.breed || 'Unknown'}</span>
                </div>
                <div className={styles.detail}>
                  <span className={styles.detailLabel}>Age:</span>
                  <span className={styles.detailValue}>{cat.age_display}</span>
                </div>
                <div className={styles.detail}>
                  <span className={styles.detailLabel}>Color:</span>
                  <span className={styles.detailValue}>{cat.color || 'Not specified'}</span>
                </div>
                <div className={styles.detail}>
                  <span className={styles.detailLabel}>Weight:</span>
                  <span className={styles.detailValue}>{cat.weight_display}</span>
                </div>
              </div>

              {cat.description && (
                <div className={styles.description}>
                  "{cat.description}"
                </div>
              )}

              <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
                <span className={`${styles.status} ${cat.is_adopted ? styles.statusAdopted : styles.statusAvailable}`}>
                  {cat.status_display}
                </span>
                {cat.is_neutered && (
                  <span className={`${styles.status} ${styles.neutered}`}>
                    Neutered
                  </span>
                )}
              </div>

              <div className={styles.actions}>
                {!cat.is_adopted && (
                  <button
                    className={`${styles.button} ${styles.adoptButton}`}
                    onClick={() => handleAdopt(cat.id)}
                  >
                    🏠 Adopt
                  </button>
                )}
                <button
                  className={`${styles.button} ${styles.deleteButton}`}
                  onClick={() => handleDelete(cat.id, cat.name)}
                >
                  🗑️ Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {loading && cats.length > 0 && (
        <div className={styles.loading}>Loading more cats...</div>
      )}
    </div>
  );
};

export default CatList;