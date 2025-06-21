import axios from 'axios';
import api from './api';

const CLOUDINARY_URL = import.meta.env.VITE_CLOUDINARY_URL;
const UPLOAD_PRESET = import.meta.env.VITE_CLOUDINARY_UPLOAD_PRESET;

export const uploadImage = async (file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('upload_preset', UPLOAD_PRESET);

    const response = await axios.post(CLOUDINARY_URL, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return {
      url: response.data.secure_url,
      publicId: response.data.public_id,
    };
  } catch (error) {
    console.error('Error uploading image:', error);
    throw new Error('Failed to upload image');
  }
};

export const uploadImageFromUrl = async (url) => {
  try {
    const formData = new FormData();
    formData.append('file', url);
    formData.append('upload_preset', UPLOAD_PRESET);

    const response = await axios.post(CLOUDINARY_URL, formData, {
      headers: {
        'Content-Type': 'application/json',
      },
    });

    return {
      url: response.data.secure_url,
      publicId: response.data.public_id,
    };
  } catch (error) {
    console.error('Error uploading image from URL:', error);
    throw new Error('Failed to upload image from URL');
  }
};

export const deleteImage = async (publicId) => {
  try {
    // This should be handled through your backend to protect your API secret
    await api.post('/cloudinary/delete', { publicId });
  } catch (error) {
    console.error('Error deleting image:', error);
    throw new Error('Failed to delete image');
  }
};

export const transformImage = (url, options = {}) => {
  if (!url) return '';
  
  // If the URL is already a full URL (e.g., https://...), return it as is
  if (url.startsWith('http')) {
    return url;
  }
  
  // Extract base URL and transformation string
  const baseUrl = url.split('/upload/')[0] + '/upload/';
  const imagePath = url.split('/upload/')[1];
  
  // Build transformation string
  const transformations = [];
  
  if (options.width) transformations.push(`w_${options.width}`);
  if (options.height) transformations.push(`h_${options.height}`);
  if (options.crop) transformations.push(`c_${options.crop}`);
  if (options.quality) transformations.push(`q_${options.quality}`);
  if (options.format) transformations.push(`f_${options.format}`);
  
  const transformationString = transformations.length > 0 
    ? transformations.join(',') + '/'
    : '';
  
  return `${baseUrl}${transformationString}${imagePath}`;
};

export const getImagePlaceholder = () => {
  return '/images/placeholder-food.jpg';
}; 