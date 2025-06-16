import { useState, useEffect, useCallback } from 'react';
import { toast } from 'react-hot-toast';
import { promotionService } from '../../services/api';
import Loader from '../../components/ui/Loader';
import styles from './PromoManager.module.css';

const PromoManager = () => {
  const [promotions, setPromotions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingPromo, setEditingPromo] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const fetchPromotions = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      console.log('Fetching promotions...');
      
      const response = await promotionService.getAdminPromotions();
      console.log('Raw API response:', response);

      if (!response?.data) {
        throw new Error('Invalid response from server');
      }

      // Handle both array and object responses
      let promotionsData = response.data;
      if (!Array.isArray(promotionsData)) {
        if (promotionsData.promotions && Array.isArray(promotionsData.promotions)) {
          promotionsData = promotionsData.promotions;
        } else {
          throw new Error('Unexpected data structure from server');
        }
      }

      console.log('Processed promotions data:', promotionsData);
      setPromotions(promotionsData);
    } catch (err) {
      console.error('Error fetching promotions:', err);
      setError(err.message || 'Failed to fetch promotions');
      toast.error(err.message || 'Failed to fetch promotions');
      setPromotions([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    console.log('Component mounted, fetching promotions...');
    fetchPromotions();
  }, [fetchPromotions]);

  useEffect(() => {
    console.log('Promotions state updated:', promotions);
  }, [promotions]);

  const handleCreatePromo = async (e) => {
    e.preventDefault();
    if (isSubmitting) return;

    try {
      setIsSubmitting(true);
      setError(null);

      // Validate form data
      const formData = {
        code: editingPromo.code?.trim().toUpperCase(),
        description: editingPromo.description?.trim() || '',
        discount_type: editingPromo.discount_type || 'percentage',
        discount_value: parseFloat(editingPromo.discount_value),
        min_purchase_amount: editingPromo.min_purchase_amount ? parseFloat(editingPromo.min_purchase_amount) : 0,
        max_uses: editingPromo.max_uses ? parseInt(editingPromo.max_uses, 10) : null,
        start_date: editingPromo.start_date,
        end_date: editingPromo.end_date,
        is_active: Boolean(editingPromo.is_active)
      };

      // Validate required fields
      if (!formData.code || !formData.discount_value || !formData.start_date || !formData.end_date) {
        throw new Error('Please fill in all required fields');
      }

      console.log('Creating promotion:', formData);
      const response = await promotionService.createAdminPromotion(formData);
      console.log('Create promotion response:', response);

      if (!response?.data) {
        throw new Error('Invalid response from server');
      }

      toast.success('Promotion created successfully');
      setEditingPromo(null);
      await fetchPromotions();
    } catch (err) {
      console.error('Error creating promotion:', err);
      setError(err.message || 'Failed to create promotion');
      toast.error(err.message || 'Failed to create promotion');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleUpdatePromo = async (e) => {
    e.preventDefault();
    if (isSubmitting) return;

    try {
      setIsSubmitting(true);
      setError(null);

      if (!editingPromo?.id) {
        throw new Error('Invalid promotion data');
      }

      const formData = {
        code: editingPromo.code?.trim().toUpperCase(),
        description: editingPromo.description?.trim() || '',
        discount_type: editingPromo.discount_type || 'percentage',
        discount_value: parseFloat(editingPromo.discount_value),
        min_purchase_amount: editingPromo.min_purchase_amount ? parseFloat(editingPromo.min_purchase_amount) : 0,
        max_uses: editingPromo.max_uses ? parseInt(editingPromo.max_uses, 10) : null,
        start_date: editingPromo.start_date,
        end_date: editingPromo.end_date,
        is_active: Boolean(editingPromo.is_active)
      };

      console.log('Updating promotion:', formData);
      const response = await promotionService.updateAdminPromotion(editingPromo.id, formData);
      console.log('Update promotion response:', response);

      if (!response?.data) {
        throw new Error('Invalid response from server');
      }

      toast.success('Promotion updated successfully');
      setEditingPromo(null);
      await fetchPromotions();
    } catch (err) {
      console.error('Error updating promotion:', err);
      setError(err.message || 'Failed to update promotion');
      toast.error(err.message || 'Failed to update promotion');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeletePromo = async (id) => {
    if (!id || isSubmitting) return;

    try {
      setIsSubmitting(true);
      setError(null);

      console.log('Deleting promotion:', id);
      await promotionService.deleteAdminPromotion(id);
      
      toast.success('Promotion deleted successfully');
      await fetchPromotions();
    } catch (err) {
      console.error('Error deleting promotion:', err);
      setError(err.message || 'Failed to delete promotion');
      toast.error(err.message || 'Failed to delete promotion');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className={styles.container}>
        <div className="flex items-center justify-center min-h-screen">
          <Loader />
        </div>
      </div>
    );
  }

  if (error && !promotions.length) {
    return (
      <div className={styles.container}>
        <div className="text-center py-8">
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={fetchPromotions}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>Promotions Management</h1>
        <p className={styles.subtitle}>Create and manage promotional offers</p>
      </div>

      <div className="flex justify-end mb-6">
        <button
          onClick={() => setEditingPromo({
            code: '',
            discount_type: 'percentage',
            discount_value: '',
            min_purchase_amount: '',
            start_date: new Date().toISOString().split('T')[0],
            end_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
            max_uses: '',
            description: '',
            is_active: true
          })}
          className={styles.addButton}
          disabled={isSubmitting}
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-5 h-5">
            <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
          </svg>
          Add Promotion
        </button>
      </div>

      {promotions.length === 0 ? (
        <div className={styles.card}>
          <div className="text-center py-8">
            <svg xmlns="http://www.w3.org/2000/svg" className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No promotions</h3>
            <p className="mt-1 text-sm text-gray-500">Get started by creating a new promotion.</p>
          </div>
        </div>
      ) : (
        <div className={styles.grid}>
          {promotions.map(promo => (
            <div key={promo.id} className={styles.card}>
              <div className={styles.cardHeader}>
                <div>
                  <h3 className={styles.promoCode}>{promo.code}</h3>
                  <p className={styles.description}>{promo.description}</p>
                </div>
                <span className={`${styles.status} ${promo.is_active ? styles.active : styles.inactive}`}>
                  {promo.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>

              <div className={styles.details}>
                <div className={styles.detailRow}>
                  <span className={styles.label}>Discount:</span>
                  <span className={styles.value}>
                    {promo.discount_value}{promo.discount_type === 'percentage' ? '%' : ' KSh'} off
                  </span>
                </div>

                {promo.min_purchase_amount > 0 && (
                  <div className={styles.detailRow}>
                    <span className={styles.label}>Min. Purchase:</span>
                    <span className={styles.value}>KSh {promo.min_purchase_amount}</span>
                  </div>
                )}

                {promo.max_uses && (
                  <div>
                    <div className={styles.detailRow}>
                      <span className={styles.label}>Usage:</span>
                      <span className={styles.value}>
                        {promo.current_uses || 0} / {promo.max_uses}
                      </span>
                    </div>
                    <div className={styles.progressBar}>
                      <div 
                        className={styles.progressFill}
                        style={{ width: `${((promo.current_uses || 0) / promo.max_uses) * 100}%` }}
                      />
                    </div>
                  </div>
                )}

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className={styles.label}>Start Date</span>
                    <span className={styles.value}>
                      {new Date(promo.start_date).toLocaleDateString()}
                    </span>
                  </div>
                  <div>
                    <span className={styles.label}>End Date</span>
                    <span className={styles.value}>
                      {new Date(promo.end_date).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </div>

              <div className={styles.actions}>
                <button
                  onClick={() => setEditingPromo(promo)}
                  className={styles.editButton}
                  disabled={isSubmitting}
                >
                  Edit
                </button>
                <button
                  onClick={() => handleDeletePromo(promo.id)}
                  className={styles.deleteButton}
                  disabled={isSubmitting}
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {editingPromo && (
        <div className={styles.modal}>
          <div className={styles.modalContent}>
            <div className={styles.modalHeader}>
              <h2 className={styles.modalTitle}>
                {editingPromo.id ? 'Edit Promotion' : 'Create Promotion'}
              </h2>
              <button
                onClick={() => setEditingPromo(null)}
                className={styles.closeButton}
                disabled={isSubmitting}
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <form onSubmit={editingPromo.id ? handleUpdatePromo : handleCreatePromo} className={styles.form}>
              <div className={styles.formGroup}>
                <label className={styles.label}>
                  Promo Code
                </label>
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={editingPromo.code || ''}
                    onChange={e => setEditingPromo(prev => ({ ...prev, code: e.target.value }))}
                    className={styles.input}
                    placeholder="Enter promo code"
                    required
                  />
                </div>
              </div>

              <div className={styles.formGroup}>
                <label className={styles.label}>
                  Description
                </label>
                <textarea
                  value={editingPromo.description || ''}
                  onChange={e => setEditingPromo(prev => ({ ...prev, description: e.target.value }))}
                  rows={2}
                  className={styles.input}
                  placeholder="Enter promotion description"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className={styles.formGroup}>
                  <label className={styles.label}>
                    Discount Type
                  </label>
                  <select
                    value={editingPromo.discount_type || 'percentage'}
                    onChange={e => setEditingPromo(prev => ({ ...prev, discount_type: e.target.value }))}
                    className={styles.select}
                  >
                    <option value="percentage">Percentage</option>
                    <option value="fixed">Fixed Amount</option>
                  </select>
                </div>
                <div className={styles.formGroup}>
                  <label className={styles.label}>
                    Discount Value
                  </label>
                  <input
                    type="number"
                    value={editingPromo.discount_value || ''}
                    onChange={e => setEditingPromo(prev => ({ ...prev, discount_value: e.target.value }))}
                    className={styles.input}
                    placeholder={editingPromo.discount_type === 'percentage' ? '10' : '100'}
                    min="0"
                    max={editingPromo.discount_type === 'percentage' ? "100" : undefined}
                    step={editingPromo.discount_type === 'percentage' ? "1" : "0.01"}
                    required
                  />
                </div>
              </div>

              <div className={styles.formGroup}>
                <label className={styles.label}>
                  Minimum Purchase Amount
                </label>
                <input
                  type="number"
                  value={editingPromo.min_purchase_amount || ''}
                  onChange={e => setEditingPromo(prev => ({ ...prev, min_purchase_amount: e.target.value }))}
                  className={styles.input}
                  placeholder="0"
                  min="0"
                  step="0.01"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className={styles.formGroup}>
                  <label className={styles.label}>
                    Start Date
                  </label>
                  <input
                    type="date"
                    value={editingPromo.start_date || ''}
                    onChange={e => setEditingPromo(prev => ({ ...prev, start_date: e.target.value }))}
                    className={styles.input}
                    required
                  />
                </div>
                <div className={styles.formGroup}>
                  <label className={styles.label}>
                    End Date
                  </label>
                  <input
                    type="date"
                    value={editingPromo.end_date || ''}
                    onChange={e => setEditingPromo(prev => ({ ...prev, end_date: e.target.value }))}
                    className={styles.input}
                    required
                  />
                </div>
              </div>

              <div className={styles.formGroup}>
                <label className={styles.label}>
                  Maximum Uses
                </label>
                <input
                  type="number"
                  value={editingPromo.max_uses || ''}
                  onChange={e => setEditingPromo(prev => ({ ...prev, max_uses: e.target.value }))}
                  className={styles.input}
                  placeholder="Leave empty for unlimited"
                  min="1"
                />
              </div>

              <div className="flex items-center mb-4">
                <input
                  type="checkbox"
                  id="is_active"
                  checked={editingPromo.is_active}
                  onChange={e => setEditingPromo(prev => ({ ...prev, is_active: e.target.checked }))}
                  className={styles.checkbox}
                />
                <label htmlFor="is_active" className="ml-2 text-sm text-gray-900">
                  Active
                </label>
              </div>

              <div className={styles.formActions}>
                <button
                  type="button"
                  onClick={() => setEditingPromo(null)}
                  className={styles.editButton}
                  disabled={isSubmitting}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className={styles.addButton}
                  disabled={isSubmitting}
                >
                  {isSubmitting ? (
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                  ) : null}
                  {editingPromo.id ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default PromoManager;