import { useState, useEffect, useCallback } from 'react';
import { toast } from 'react-hot-toast';
import { menuService } from '../../services/api';
import { uploadImage, transformImage, getImagePlaceholder } from '../../services/cloudinary';
import Loader from '../../components/ui/Loader';
import styles from './MenuManager.module.css';

const initialItemState = {
  name: '',
  description: '',
  price: '',
  category_id: '',
  image: null,
  image_url: '',
  ingredients: [],
  is_available: true,
  is_featured: false,
  add_ons: []
};

const MenuManager = () => {
  const [menuItems, setMenuItems] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState({
    initial: true,
    categoryCreate: false,
    categoryUpdate: false,
    categoryDelete: false,
    itemCreate: false,
    itemUpdate: false,
    itemDelete: false
  });
  const [editingItem, setEditingItem] = useState(null);
  const [editingCategory, setEditingCategory] = useState(null);
  const [selectedImage, setSelectedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [newCategory, setNewCategory] = useState({ name: '', description: '' });
  const [imageUrl, setImageUrl] = useState('');
  const [newItem, setNewItem] = useState(initialItemState);

  // Add default images mapping
  const defaultImages = {
    'Kebabs': '/images/menu/kebabs.jpg',
    'Shawarma': '/images/menu/shawarma.jpg',
    'Falafel': '/images/menu/falafel.jpg',
    'Hummus': '/images/menu/hummus.jpg',
    'Beef Burgers': '/images/menu/beef-burger.jpg',
    'Chicken Burgers': '/images/menu/chicken-burger.jpg',
    'Veggie Options': '/images/menu/veggie-options.jpg',
    'Qaffee Point Special': '/images/menu/special.jpg',
    'Lasagna': '/images/menu/lasagna.jpg'
  };

  // Helper function to get image URL
  const getItemImage = (item) => {
    if (!item || !item.image_url) {
      return '/images/placeholder-food.jpg';
    }
    
    // If the image_url is a full URL (e.g., https://...), use it directly
    if (item.image_url.startsWith('http')) {
      return item.image_url;
    }
    
    // If it's a relative path from the backend, prepend the API base URL
    const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';
    return `${baseUrl}${item.image_url}`;
  };

  const fetchMenuData = useCallback(async () => {
    try {
      setLoading(prev => ({ ...prev, initial: true }));
      const [itemsRes, categoriesRes] = await Promise.all([
        menuService.getItems(),
        menuService.getCategories()
      ]);

      // Handle response formats
      const categories = categoriesRes.data?.data || categoriesRes.data || [];
      const items = itemsRes.data || [];
      
      console.log('Fetched items:', items);  // Debug log

      setCategories(categories);
      setMenuItems(items);
    } catch (error) {
      console.error('Error fetching menu data:', error);
      toast.error('Failed to fetch menu data. Please refresh the page.');
    } finally {
      setLoading(prev => ({ ...prev, initial: false }));
    }
  }, []);

  useEffect(() => {
    fetchMenuData();
  }, [fetchMenuData]);

  useEffect(() => {
    if (editingItem) {
      setImageUrl(editingItem.image_url || '');
      setImagePreview(editingItem.image_url || null);
    } else {
      setImageUrl('');
      setImagePreview(null);
    }
  }, [editingItem]);

  useEffect(() => {
    if (!editingItem && !newItem.image_url) {
      setImageUrl('');
      setImagePreview(null);
    }
  }, [editingItem, newItem.image_url]);

  const handleImageChange = async (e, isEditing = false) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      // Show preview immediately
      const reader = new FileReader();
      reader.onloadend = () => setImagePreview(reader.result);
      reader.readAsDataURL(file);

      // Upload to Cloudinary
      const uploadedImage = await uploadImage(file);
      
      if (isEditing) {
        setEditingItem(prev => ({ 
          ...prev, 
          image_url: uploadedImage.url || '',
          cloudinary_id: uploadedImage.publicId
        }));
      } else {
        setSelectedImage(uploadedImage);
        setNewItem(prev => ({
          ...prev,
          image_url: uploadedImage.url || '',
          cloudinary_id: uploadedImage.publicId
        }));
      }

      // Clear URL input when file is uploaded
      setImageUrl('');
      toast.success('Image uploaded successfully');
    } catch (error) {
      console.error('Error uploading image:', error);
      toast.error('Failed to upload image');
      setImagePreview(null);
    }
  };

  const handleImageUrlChange = (e) => {
    const url = e.target.value;
    setImageUrl(url);
    setImagePreview(url || null);
    
    if (editingItem) {
      setEditingItem(prev => ({ 
        ...prev, 
        image_url: url,
        image: null // Clear file input when URL is provided
      }));
    } else {
      setNewItem(prev => ({
        ...prev,
        image_url: url,
        image: null // Clear file input when URL is provided
      }));
    }
  };

  const handleCreateCategory = async (e) => {
    e.preventDefault();
    if (!editingCategory.name.trim()) {
      toast.error('Category name is required');
      return;
    }

    try {
      setLoading(prev => ({ ...prev, categoryCreate: true }));
      const response = await menuService.createCategory(editingCategory);
      const newCategory = response.data?.data || response.data;
      setCategories([...categories, newCategory]);
      setEditingCategory(null);
      toast.success('Category created successfully');
    } catch (error) {
      console.error('Error creating category:', error);
      toast.error(error.response?.data?.message || 'Failed to create category');
    } finally {
      setLoading(prev => ({ ...prev, categoryCreate: false }));
    }
  };

  const handleUpdateCategory = async (e) => {
    e.preventDefault();
    if (!editingCategory?.name.trim()) {
      toast.error('Category name is required');
      return;
    }

    try {
      setIsSubmitting(true);
      const response = await menuService.updateCategory(editingCategory.id, editingCategory);
      setCategories(categories.map(cat => 
        cat.id === editingCategory.id ? response.data : cat
      ));
      setEditingCategory(null);
      toast.success('Category updated successfully');
    } catch (error) {
      console.error('Error updating category:', error);
      toast.error('Failed to update category');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteCategory = async (id) => {
    if (!window.confirm('Are you sure? This will also delete all items in this category!')) {
      return;
    }

    try {
      setLoading(prev => ({ ...prev, categoryDelete: true }));
      await menuService.deleteCategory(id);
      setCategories(categories.filter(cat => cat.id !== id));
      setMenuItems(menuItems.filter(item => item.category_id !== id));
      toast.success('Category deleted successfully');
    } catch (error) {
      console.error('Error deleting category:', error);
      toast.error(error.response?.data?.message || 'Failed to delete category');
    } finally {
      setLoading(prev => ({ ...prev, categoryDelete: false }));
    }
  };

  const handleEditItem = (item) => {
    if (item) {
      setEditingItem(item);
      setImagePreview(item.image_url);
      setImageUrl(item.image_url || '');
    } else {
      setEditingItem({
        ...initialItemState,
        add_ons: [],
        is_available: true,
        is_featured: false
      });
      setImagePreview(null);
      setImageUrl('');
    }
  };

  const handleCancelEdit = () => {
    setEditingItem(null);
    setImagePreview(null);
    setImageUrl('');
    resetItemForm();
  };

  const resetItemForm = () => {
    setNewItem(initialItemState);
    setSelectedImage(null);
    setImagePreview(null);
    setImageUrl('');
  };

  const validateItemForm = (item) => {
    if (!item.name.trim()) {
      toast.error('Item name is required');
      return false;
    }
    if (!item.category_id) {
      toast.error('Please select a category');
      return false;
    }
    if (!item.price || isNaN(item.price) || parseFloat(item.price) <= 0) {
      toast.error('Please enter a valid price');
      return false;
    }
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const itemToSave = editingItem;
    if (!validateItemForm(itemToSave)) return;

    try {
      setIsSubmitting(true);
      // Clean up the data before sending
      const cleanData = {
        name: itemToSave.name,
        description: itemToSave.description || '',
        price: parseFloat(itemToSave.price),
        category_id: parseInt(itemToSave.category_id),
        image_url: itemToSave.image_url || '',
        is_available: Boolean(itemToSave.is_available),
        is_featured: Boolean(itemToSave.is_featured)
      };

      if (itemToSave.id) {
        const response = await menuService.updateItem(itemToSave.id, cleanData);
        const updatedItem = response.data?.data || response.data;
        if (!updatedItem || !updatedItem.id) {
          throw new Error('Invalid response data from server');
        }
        setMenuItems(prevItems => prevItems.map(item => 
          item.id === itemToSave.id ? updatedItem : item
        ));
        toast.success('Item updated successfully');
      } else {
        const response = await menuService.createItem(cleanData);
        const newItem = response.data?.data || response.data;
        if (!newItem || !newItem.id) {
          throw new Error('Invalid response data from server');
        }
        setMenuItems(prevItems => [...prevItems, newItem]);
        toast.success('Item created successfully');
      }
      handleCancelEdit();
    } catch (error) {
      console.error('Error saving item:', error);
      toast.error(error.response?.data?.message || 'Failed to save item');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading.initial) {
    return (
      <div className={styles.container}>
        <div className={styles.loaderContainer}>
          <Loader />
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      {loading.initial ? (
        <div className={styles.loaderContainer}>
          <Loader />
        </div>
      ) : (
        <>
          <div className={styles.header}>
            <h1 className={styles.title}>Menu Management</h1>
            <p className={styles.subtitle}>Manage your menu items and categories</p>
          </div>

          {/* Categories Section */}
      <section className={styles.section}>
        <div className={styles.sectionHeader}>
          <h2 className={styles.sectionTitle}>Categories</h2>
          <button
            onClick={() => setEditingCategory({ name: '', description: '' })}
            className={styles.addButton}
          >
            Add Category
          </button>
        </div>

        <div className={styles.categoriesGrid}>
          {categories.map(category => (
            <div key={category.id} className={styles.categoryCard}>
              <div className={styles.categoryHeader}>
                <h3 className={styles.categoryName}>{category.name}</h3>
                <div className={styles.categoryActions}>
                  <button
                    onClick={() => setEditingCategory(category)}
                    className={styles.editButton}
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDeleteCategory(category.id)}
                    className={styles.deleteButton}
                  >
                    Delete
                  </button>
                </div>
              </div>
              {category.description && (
                <p className={styles.categoryDescription}>{category.description}</p>
              )}
              <p className={styles.itemCount}>
                {menuItems.filter(item => item.category_id === category.id).length} items
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Menu Items Section */}
      <section className={styles.section}>
        <div className={styles.sectionHeader}>
          <h2 className={styles.sectionTitle}>Menu Items</h2>
          <button
            onClick={() => handleEditItem(null)}
            className={styles.addButton}
          >
            Add Item
          </button>
        </div>

        <div className={styles.itemsGrid}>
          {menuItems.map(item => (
            <div key={item.id} className={styles.itemCard}>
              <div className={styles.itemImageContainer}>
                <img
                  src={getItemImage(item)}
                  alt={item.name}
                  className={styles.itemImage}
                />
                {!item.is_available && (
                  <div className={styles.unavailableBadge}>Out of Stock</div>
                )}
                {item.is_featured && (
                  <div className={styles.featuredBadge}>Featured</div>
                )}
              </div>
              <div className={styles.itemContent}>
                <h3 className={styles.itemName}>{item.name}</h3>
                <p className={styles.itemCategory}>
                  {categories.find(cat => cat.id === item.category_id)?.name}
                </p>
                <p className={styles.itemPrice}>KSh {item.price}</p>
                <p className={styles.itemDescription}>{item.description}</p>
                <div className={styles.itemActions}>
                  <button
                    onClick={() => handleEditItem(item)}
                    className={styles.editButton}
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDeleteItem(item.id)}
                    className={styles.deleteButton}
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>
      </>
      )}

      {/* Category Modal */}
      {editingCategory && (
        <div className={styles.modalOverlay}>
          <div className={styles.modal}>
            <h2 className={styles.modalTitle}>
              {editingCategory.id ? 'Edit Category' : 'New Category'}
            </h2>
            <form onSubmit={editingCategory.id ? handleUpdateCategory : handleCreateCategory}>
              <div className={styles.formGroup}>
                <label className={styles.formLabel} htmlFor="categoryName">Name</label>
                <input
                  type="text"
                  id="categoryName"
                  placeholder="Enter category name"
                  value={editingCategory.name}
                  onChange={e => setEditingCategory(prev => ({ ...prev, name: e.target.value }))}
                  className={styles.input}
                  required
                />
              </div>
              <div className={styles.formGroup}>
                <label className={styles.formLabel} htmlFor="categoryDescription">Description</label>
                <textarea
                  id="categoryDescription"
                  placeholder="Enter category description"
                  value={editingCategory.description}
                  onChange={e => setEditingCategory(prev => ({ ...prev, description: e.target.value }))}
                  className={styles.textarea}
                />
              </div>
              <div className={styles.modalActions}>
                <button
                  type="button"
                  onClick={() => setEditingCategory(null)}
                  className={styles.cancelButton}
                  disabled={isSubmitting}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className={styles.submitButton}
                  disabled={isSubmitting}
                >
                  {isSubmitting ? 'Saving...' : editingCategory.id ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Item Modal */}
      {editingItem && (
        <div className={styles.modalOverlay}>
          <div className={styles.modal}>
            <h2 className={styles.modalTitle}>
              {editingItem.id ? 'Edit Item' : 'New Item'}
            </h2>
            <form onSubmit={handleSubmit} className={styles.form}>
              {/* Basic Information */}
              <div className={styles.formSection}>
                <h3 className={styles.formSectionTitle}>Basic Information</h3>
                <div className={styles.formGroup}>
                  <label className={styles.formLabel} htmlFor="itemName">Name</label>
                  <input
                    type="text"
                    id="itemName"
                    placeholder="Enter item name"
                    value={editingItem.name || ''}
                    onChange={e => setEditingItem(prev => ({ ...prev, name: e.target.value }))}
                    className={styles.input}
                    required
                  />
                </div>

                <div className={styles.formGroup}>
                  <label className={styles.formLabel} htmlFor="itemCategory">Category</label>
                  <select
                    id="itemCategory"
                    value={editingItem.category_id || ''}
                    onChange={e => setEditingItem(prev => ({ ...prev, category_id: e.target.value }))}
                    className={styles.select}
                    required
                  >
                    <option value="">Select Category</option>
                    {categories.map(cat => (
                      <option key={cat.id} value={cat.id}>{cat.name}</option>
                    ))}
                  </select>
                </div>

                <div className={styles.formGroup}>
                  <label className={styles.formLabel} htmlFor="itemPrice">Price (KSh)</label>
                  <input
                    type="number"
                    id="itemPrice"
                    placeholder="Enter price"
                    value={editingItem.price || ''}
                    onChange={e => setEditingItem(prev => ({ ...prev, price: e.target.value }))}
                    className={styles.input}
                    min="0"
                    step="0.01"
                    required
                  />
                </div>

                <div className={styles.formGroup}>
                  <label className={styles.formLabel} htmlFor="itemDescription">Description</label>
                  <textarea
                    id="itemDescription"
                    placeholder="Enter item description"
                    value={editingItem.description || ''}
                    onChange={e => setEditingItem(prev => ({ ...prev, description: e.target.value }))}
                    className={styles.textarea}
                    rows={3}
                  />
                </div>
              </div>

              {/* Image Upload */}
              <div className={styles.formSection}>
                <h3 className={styles.formSectionTitle}>Item Image</h3>
                <div className={styles.imageUpload}>
                  {imagePreview && (
                    <img
                      src={imagePreview}
                      alt="Preview"
                      className={styles.imagePreview}
                    />
                  )}
                  <div className={styles.imageInputs}>
                    <div className={styles.formGroup}>
                      <label className={styles.formLabel}>Upload Image</label>
                      <input
                        type="file"
                        accept="image/*"
                        onChange={e => handleImageChange(e, Boolean(editingItem?.id))}
                        className={styles.fileInput}
                      />
                    </div>
                    <div className={styles.formGroup}>
                      <label className={styles.formLabel}>Or Enter Image URL</label>
                      <input
                        type="url"
                        value={imageUrl}
                        onChange={handleImageUrlChange}
                        placeholder="https://example.com/image.jpg"
                        className={styles.input}
                      />
                    </div>
                  </div>
                </div>
              </div>

              {/* Status */}
              <div className={styles.formSection}>
                <h3 className={styles.formSectionTitle}>Status</h3>
                <div className={styles.checkboxGroup}>
                  <label className={styles.checkbox}>
                    <input
                      type="checkbox"
                      checked={editingItem.is_available ?? true}
                      onChange={e => setEditingItem(prev => ({ ...prev, is_available: e.target.checked }))}
                    />
                    Available
                  </label>
                  <label className={styles.checkbox}>
                    <input
                      type="checkbox"
                      checked={editingItem.is_featured ?? false}
                      onChange={e => setEditingItem(prev => ({ ...prev, is_featured: e.target.checked }))}
                    />
                    Featured
                  </label>
                </div>
              </div>

              {/* Add-ons */}
              <div className={styles.formSection}>
                <h3 className={styles.formSectionTitle}>Add-ons</h3>
                <button
                  type="button"
                  onClick={() => {
                    const newAddon = { name: '', price: '', is_available: true };
                    setEditingItem(prev => ({
                      ...prev,
                      add_ons: [...(prev.add_ons || []), newAddon]
                    }));
                  }}
                  className={styles.addButton}
                >
                  Add Add-on
                </button>
                <div className={styles.addonsGrid}>
                  {(editingItem.add_ons || []).map((addon, index) => (
                    <div key={index} className={styles.addonItem}>
                      <input
                        type="text"
                        placeholder="Add-on name"
                        value={addon.name}
                        onChange={e => {
                          const newAddons = [...(editingItem.add_ons || [])];
                          newAddons[index] = { ...addon, name: e.target.value };
                          setEditingItem(prev => ({ ...prev, add_ons: newAddons }));
                        }}
                        className={styles.input}
                      />
                      <input
                        type="number"
                        placeholder="Price"
                        value={addon.price}
                        onChange={e => {
                          const newAddons = [...(editingItem.add_ons || [])];
                          newAddons[index] = { ...addon, price: e.target.value };
                          setEditingItem(prev => ({ ...prev, add_ons: newAddons }));
                        }}
                        className={styles.input}
                        min="0"
                        step="0.01"
                      />
                      <button
                        type="button"
                        onClick={() => {
                          const newAddons = [...(editingItem.add_ons || [])];
                          newAddons.splice(index, 1);
                          setEditingItem(prev => ({ ...prev, add_ons: newAddons }));
                        }}
                        className={styles.deleteButton}
                      >
                        Remove
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              <div className={styles.modalActions}>
                <button
                  type="button"
                  onClick={handleCancelEdit}
                  className={styles.cancelButton}
                  disabled={isSubmitting}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className={styles.submitButton}
                  disabled={isSubmitting}
                >
                  {isSubmitting ? 'Saving...' : editingItem.id ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default MenuManager;