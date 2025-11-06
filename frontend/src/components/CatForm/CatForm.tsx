import React, { useState } from 'react';
import { CatCreate } from '../../types/Cat';
import catService from '../../services/catService';
import styles from './CatForm.module.css';

interface CatFormProps {
  onCancel: () => void;
  onSuccess: () => void;
}

const CatForm: React.FC<CatFormProps> = ({ onCancel, onSuccess }) => {
  const [formData, setFormData] = useState<CatCreate>({
    name: '',
    breed: '',
    age: undefined,
    color: '',
    weight: undefined,
    is_neutered: false,
    description: '',
  });

  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string[]>>({});
  const [successMessage, setSuccessMessage] = useState('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' 
        ? (e.target as HTMLInputElement).checked
        : type === 'number' 
          ? value ? Number(value) : undefined
          : value
    }));

    // Clear errors for this field
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: []
      }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrors({});
    setSuccessMessage('');

    try {
      // Filter out empty strings and undefined values
      const cleanFormData: CatCreate = {
        name: formData.name.trim(),
        ...(formData.breed?.trim() && { breed: formData.breed.trim() }),
        ...(formData.age !== undefined && formData.age > 0 && { age: formData.age }),
        ...(formData.color?.trim() && { color: formData.color.trim() }),
        ...(formData.weight !== undefined && formData.weight > 0 && { weight: formData.weight }),
        ...(formData.is_neutered !== undefined && { is_neutered: formData.is_neutered }),
        ...(formData.description?.trim() && { description: formData.description.trim() }),
      };

      const response = await catService.createCat(cleanFormData);
      setSuccessMessage(response.message);
      
      setTimeout(() => {
        onSuccess();
      }, 1500);

    } catch (error: any) {
      if (error.response?.data?.errors) {
        setErrors(error.response.data.errors);
      } else if (error.response?.data?.message) {
        setErrors({ general: [error.response.data.message] });
      } else {
        setErrors({ general: ['Failed to create cat. Please try again.'] });
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <h2 className={styles.title}>Add New Cat</h2>

      <form onSubmit={handleSubmit} className={styles.form}>
        {errors.general && (
          <div className={styles.formError}>
            {errors.general.map((error, index) => (
              <div key={index}>{error}</div>
            ))}
          </div>
        )}

        {successMessage && (
          <div className={styles.formSuccess}>
            {successMessage}
          </div>
        )}

        <div className={styles.formGroup}>
          <label htmlFor="cat-name" className={styles.label}>
            Name <span className={styles.required}>*</span>
          </label>
          <input
            id="cat-name"
            type="text"
            name="name"
            value={formData.name}
            onChange={handleChange}
            className={styles.input}
            required
            placeholder="Enter cat's name"
          />
          {errors.name && <span className={styles.error}>{errors.name[0]}</span>}
          <span className={styles.hint}>Must be at least 2 characters long</span>
        </div>

        <div className={styles.formGroup}>
          <label htmlFor="cat-breed" className={styles.label}>Breed</label>
          <input
            id="cat-breed"
            type="text"
            name="breed"
            value={formData.breed}
            onChange={handleChange}
            className={styles.input}
            placeholder="e.g., Persian, Siamese, Maine Coon"
          />
          {errors.breed && <span className={styles.error}>{errors.breed[0]}</span>}
        </div>

        <div className={styles.formGroup}>
          <label htmlFor="cat-age" className={styles.label}>Age (years)</label>
          <input
            id="cat-age"
            type="number"
            name="age"
            value={formData.age || ''}
            onChange={handleChange}
            className={styles.input}
            min="0"
            max="30"
            placeholder="e.g., 3"
          />
          {errors.age && <span className={styles.error}>{errors.age[0]}</span>}
          <span className={styles.hint}>Age between 0 and 30 years</span>
        </div>

        <div className={styles.formGroup}>
          <label htmlFor="cat-color" className={styles.label}>Color</label>
          <input
            id="cat-color"
            type="text"
            name="color"
            value={formData.color}
            onChange={handleChange}
            className={styles.input}
            placeholder="e.g., Black, White, Tabby, Calico"
          />
          {errors.color && <span className={styles.error}>{errors.color[0]}</span>}
        </div>

        <div className={styles.formGroup}>
          <label htmlFor="cat-weight" className={styles.label}>Weight (kg)</label>
          <input
            id="cat-weight"
            type="number"
            name="weight"
            value={formData.weight || ''}
            onChange={handleChange}
            className={styles.input}
            min="0.1"
            max="20"
            step="0.1"
            placeholder="e.g., 4.2"
          />
          {errors.weight && <span className={styles.error}>{errors.weight[0]}</span>}
          <span className={styles.hint}>Weight between 0.1 and 20 kg</span>
        </div>

        <div className={styles.formGroup}>
          <div className={styles.checkbox}>
            <input
              id="cat-is-neutered"
              type="checkbox"
              name="is_neutered"
              checked={formData.is_neutered}
              onChange={handleChange}
              className={styles.checkboxInput}
            />
            <label htmlFor="cat-is-neutered" className={styles.checkboxLabel}>Cat is neutered/spayed</label>
          </div>
          {errors.is_neutered && <span className={styles.error}>{errors.is_neutered[0]}</span>}
        </div>

        <div className={styles.formGroup}>
          <label className={styles.label}>Description</label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            className={styles.textarea}
            placeholder="Describe the cat's personality, characteristics, special needs, etc..."
            rows={4}
          />
          {errors.description && <span className={styles.error}>{errors.description[0]}</span>}
          <span className={styles.hint}>At least 10 characters (optional)</span>
        </div>

        <div className={styles.actions}>
          <button
            type="button"
            onClick={onCancel}
            className={`${styles.button} ${styles.cancelButton}`}
            disabled={loading}
          >
            Cancel
          </button>
          <button
            type="submit"
            className={`${styles.button} ${styles.submitButton}`}
            disabled={loading || !formData.name.trim()}
          >
            {loading ? 'Creating...' : 'Create Cat'}
          </button>
        </div>

        {loading && (
          <div className={styles.loadingOverlay}>
            Creating your cat... 🐱
          </div>
        )}
      </form>
    </div>
  );
};

export default CatForm;