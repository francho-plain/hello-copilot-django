import React, { useState } from 'react';
import CatList from './components/CatList';
import CatForm from './components/CatForm';
import Statistics from './components/Statistics';
import styles from './styles/App.module.css';

type View = 'list' | 'add' | 'statistics';

function App() {
  const [currentView, setCurrentView] = useState<View>('list');

  const renderContent = () => {
    switch (currentView) {
      case 'list':
        return <CatList onAddNew={() => setCurrentView('add')} />;
      case 'add':
        return <CatForm onCancel={() => setCurrentView('list')} onSuccess={() => setCurrentView('list')} />;
      case 'statistics':
        return <Statistics />;
      default:
        return <CatList onAddNew={() => setCurrentView('add')} />;
    }
  };

  return (
    <div className={styles.app}>
      <header className={styles.header}>
        <div className={styles.headerContent}>
          <div>
            <h1 className={styles.title}>🐱 Cat Adoption Center</h1>
            <p className={styles.subtitle}>Find your perfect feline companion</p>
          </div>
          <nav className={styles.nav}>
            <button
              className={`${styles.navButton} ${currentView === 'list' ? styles.active : ''}`}
              onClick={() => setCurrentView('list')}
            >
              All Cats
            </button>
            <button
              className={`${styles.navButton} ${currentView === 'add' ? styles.active : ''}`}
              onClick={() => setCurrentView('add')}
            >
              Add Cat
            </button>
            <button
              className={`${styles.navButton} ${currentView === 'statistics' ? styles.active : ''}`}
              onClick={() => setCurrentView('statistics')}
            >
              Statistics
            </button>
          </nav>
        </div>
      </header>

      <main className={styles.container}>
        <div className={styles.content}>
          {renderContent()}
        </div>
      </main>
    </div>
  );
}

export default App;
