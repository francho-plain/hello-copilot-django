import React, { useEffect, useState } from 'react';
import { CatStatistics } from '../../types/Cat';
import catService from '../../services/catService';
import styles from './Statistics.module.css';

const Statistics: React.FC = () => {
  const [stats, setStats] = useState<CatStatistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    loadStatistics();
  }, []);

  const loadStatistics = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await catService.getStatistics();
      setStats(response);
    } catch (error: any) {
      setError(error.response?.data?.message || 'Failed to load statistics');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>
          <div className={styles.spinner}></div>
          <p>Loading statistics... 📊</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>
          <h3>Error Loading Statistics</h3>
          <p>{error}</p>
          <button 
            onClick={loadStatistics}
            className={styles.retryButton}
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className={styles.container}>
        <div className={styles.noData}>
          <h3>No Statistics Available</h3>
          <p>Add some cats to see statistics</p>
        </div>
      </div>
    );
  }

  const neuteredPercentage = stats.total_cats > 0 
    ? Math.round((stats.neutered_cats / stats.total_cats) * 100) 
    : 0;

  return (
    <div className={styles.container}>
      <h2 className={styles.title}>Cat Statistics 📈</h2>

      <div className={styles.statsGrid}>
        {/* Total Cats */}
        <div className={styles.statCard}>
          <div className={styles.statIcon}>🐱</div>
          <div className={styles.statContent}>
            <h3 className={styles.statNumber}>{stats.total_cats}</h3>
            <p className={styles.statLabel}>Total Cats</p>
          </div>
        </div>

        {/* Average Age */}
        <div className={styles.statCard}>
          <div className={styles.statIcon}>📅</div>
          <div className={styles.statContent}>
            <h3 className={styles.statNumber}>
              {stats.average_age ? `${stats.average_age}y` : 'N/A'}
            </h3>
            <p className={styles.statLabel}>Average Age</p>
          </div>
        </div>

        {/* Adoption Rate */}
        <div className={styles.statCard}>
          <div className={styles.statIcon}>📊</div>
          <div className={styles.statContent}>
            <h3 className={styles.statNumber}>
              {stats.adoption_rate ? `${stats.adoption_rate}%` : 'N/A'}
            </h3>
            <p className={styles.statLabel}>Adoption Rate</p>
          </div>
        </div>

        {/* Neutered Percentage */}
        <div className={styles.statCard}>
          <div className={styles.statIcon}>💉</div>
          <div className={styles.statContent}>
            <h3 className={styles.statNumber}>
              {neuteredPercentage}%
            </h3>
            <p className={styles.statLabel}>Neutered</p>
          </div>
        </div>

        {/* Available for Adoption */}
        <div className={styles.statCard}>
          <div className={styles.statIcon}>🏠</div>
          <div className={styles.statContent}>
            <h3 className={styles.statNumber}>{stats.available_cats}</h3>
            <p className={styles.statLabel}>Available</p>
          </div>
        </div>

        {/* Adopted */}
        <div className={styles.statCard}>
          <div className={styles.statIcon}>❤️</div>
          <div className={styles.statContent}>
            <h3 className={styles.statNumber}>{stats.adopted_cats}</h3>
            <p className={styles.statLabel}>Adopted</p>
          </div>
        </div>
      </div>

      {/* Additional Statistics */}
      <div className={styles.additionalStats}>
        <div className={styles.statRow}>
          <div className={styles.statInfo}>
            <span className={styles.statIcon}>🧬</span>
            <div className={styles.statDetails}>
              <h4 className={styles.statTitle}>Breed Diversity</h4>
              <p className={styles.statValue}>{stats.breeds_count} different breeds</p>
            </div>
          </div>

          <div className={styles.statInfo}>
            <span className={styles.statIcon}>⏰</span>
            <div className={styles.statDetails}>
              <h4 className={styles.statTitle}>Recent Adoptions</h4>
              <p className={styles.statValue}>{stats.recent_adoptions} in last 30 days</p>
            </div>
          </div>
        </div>

        {/* Age Range */}
        {stats.youngest_age !== null && stats.oldest_age !== null && (
          <div className={styles.rangeCard}>
            <h3 className={styles.rangeTitle}>Age Range</h3>
            <div className={styles.rangeContent}>
              <div className={styles.range}>
                <span className={styles.rangeValue}>{stats.youngest_age} years</span>
                <span className={styles.rangeSeparator}>to</span>
                <span className={styles.rangeValue}>{stats.oldest_age} years</span>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className={styles.refreshSection}>
        <button 
          onClick={loadStatistics}
          className={styles.refreshButton}
          disabled={loading}
        >
          🔄 Refresh Statistics
        </button>
        <p className={styles.lastUpdated}>
          Click refresh to get the latest statistics
        </p>
      </div>
    </div>
  );
};

export default Statistics;