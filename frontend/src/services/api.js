import axios from 'axios';

// Determine backend API base URL from environment (supports VITE_API_URL and VITE_API_BASE_URL, default '/api')
const rawBaseUrl = (import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || '/api').trim();
const API_BASE_URL = rawBaseUrl.endsWith('/api') ? rawBaseUrl : `${rawBaseUrl.replace(/\/+$/, '')}/api`;

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 45000, // 45 seconds for LLM + RAG embedding calls
  headers: {
    'Content-Type': 'application/json',
  },
});

// Automatically inject JWT Bearer token if available
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('tripgenie_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

/**
 * Standardize and translate API errors into user-friendly diagnostic messages
 * Handles network failures, timeouts, 4xx, 5xx, and missing backend scenarios.
 * @param {Error|Object} err
 * @param {string} defaultMessage
 * @returns {string}
 */
export function normalizeApiError(err, defaultMessage = 'An unexpected error occurred.') {
  if (!err) return defaultMessage;

  // Timeout error
  if (err.code === 'ECONNABORTED' || (err.message && err.message.toLowerCase().includes('timeout'))) {
    return 'The request timed out while formulating the AI response. Please try again.';
  }

  // Network / Connection Refused / Backend offline
  if (err.message === 'Network Error' || err.code === 'ERR_NETWORK' || !err.response) {
    return `Cannot connect to the TripGenie backend at ${API_BASE_URL}. Please ensure the FastAPI server is running.`;
  }

  const status = err.response?.status;
  const detail = err.response?.data?.detail;

  if (detail) {
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail)) {
      return detail.map((d) => d.msg || JSON.stringify(d)).join(', ');
    }
  }

  if (status === 404) {
    return 'The requested resource or endpoint was not found on the server (404).';
  }

  if (status === 401) {
    return 'Authentication session expired or invalid credentials. Please sign in again.';
  }

  if (status === 403) {
    return 'Access forbidden. You do not have permission to perform this action.';
  }

  if (status >= 500) {
    return 'TripGenie backend encountered an internal server error. Please check backend logs.';
  }

  return err.message || defaultMessage;
}

/**
 * Check backend health and get indexed destinations
 */
export async function checkHealth() {
  try {
    const res = await apiClient.get('/health');
    return { success: true, data: res.data };
  } catch (err) {
    return {
      success: false,
      error: normalizeApiError(err, 'Cannot reach FastAPI backend server.'),
    };
  }
}

/**
 * Fetch known destinations in the RAG knowledge base
 */
export async function getDestinations() {
  try {
    const res = await apiClient.get('/destinations');
    return { success: true, data: res.data.destinations || [] };
  } catch (err) {
    return {
      success: false,
      data: ['Goa', 'Kerala', 'Manali', 'Jaipur', 'Rishikesh'],
      error: normalizeApiError(err, 'Unable to load destinations catalogue.'),
    };
  }
}

/**
 * Fetch activities catalog for a specific destination
 */
export async function getActivities(destination) {
  try {
    const dest = encodeURIComponent((destination || '').trim());
    const res = await apiClient.get(`/activities/${dest}`);
    return { success: true, data: res.data.activities || [] };
  } catch (err) {
    return {
      success: false,
      data: [],
      error: normalizeApiError(err, 'Unable to load destination activities.'),
    };
  }
}

/**
 * Calculate deterministic 5-category travel budget & evaluate budget health
 */
export async function calculateBudget(params) {
  try {
    const payload = {
      destination: (params.destination || '').trim() || 'Goa',
      days: Number(params.days) || 4,
      travelers: Number(params.travelers) || 2,
      budget: Number(params.budget) || 50000,
      hotel_preference: params.hotelPreference || 'standard',
      transport_preference: params.transportPreference || 'private_cab',
      selected_activities: Array.isArray(params.selectedActivities) ? params.selectedActivities : [],
      travel_style: params.travelStyle || 'balanced',
    };
    const res = await apiClient.post('/calculate-budget', payload);
    return { success: true, data: res.data };
  } catch (err) {
    return {
      success: false,
      error: normalizeApiError(err, 'Budget calculation failed.'),
    };
  }
}

/**
 * Request an AI-generated, RAG-grounded itinerary from FastAPI
 * @param {Object} tripData
 */
export async function planTrip(tripData) {
  try {
    const payload = {
      destination: (tripData.destination || '').trim(),
      days: Number(tripData.days) || 5,
      travelers: Number(tripData.travelers) || 2,
      budget: Number(tripData.budget) || 50000,
      interests: Array.isArray(tripData.interests) ? tripData.interests : [],
      travel_style: tripData.travelStyle || 'balanced',
      hotel_preference: tripData.hotelPreference || 'standard',
      transport_preference: tripData.transportPreference || 'private_cab',
      selected_activities: Array.isArray(tripData.selectedActivities) ? tripData.selectedActivities : [],
      start_date: tripData.startDate || null,
      end_date: tripData.endDate || null,
    };

    const res = await apiClient.post('/plan-trip', payload);
    return { success: true, data: res.data };
  } catch (err) {
    return {
      success: false,
      error: normalizeApiError(err, 'Trip planning failed.'),
      status: err.response?.status,
    };
  }
}

/**
 * Send a message to TripGenie AI Chatbot with trip context and history
 * @param {string} message
 * @param {Object} [tripContext]
 * @param {Array} [history]
 */
export async function sendChatMessage(message, tripContext = null, history = []) {
  try {
    const payload = {
      message: (message || '').trim(),
      trip: tripContext
        ? {
            destination: tripContext.destination || 'Goa',
            days: Array.isArray(tripContext.days) ? tripContext.days : [],
            days_count:
              tripContext.days_count ||
              (Array.isArray(tripContext.days) ? tripContext.days.length : Number(tripContext.days) || 4),
            budget: Number(tripContext.budget) || 50000,
            travelers: Number(tripContext.travelers) || 2,
            hotel_preference: tripContext.hotel_preference || tripContext.hotelPreference || 'standard',
            transport_preference: tripContext.transport_preference || tripContext.transportPreference || 'private_cab',
            selected_activities: Array.isArray(tripContext.selected_activities)
              ? tripContext.selected_activities
              : Array.isArray(tripContext.selectedActivities)
              ? tripContext.selectedActivities
              : [],
            summary: tripContext.summary || '',
          }
        : null,
      history: history.map((h) => ({ role: h.role, content: h.content })),
    };

    const res = await apiClient.post('/chat', payload);
    return { success: true, data: res.data };
  } catch (err) {
    return {
      success: false,
      error: normalizeApiError(err, 'Chat assistant encountered an error.'),
    };
  }
}

/**
 * Fetch real-time meteorological observation and 5-day forecast from backend
 * @param {string} destination
 */
export async function getLiveWeather(destination) {
  const clean = (destination || '').trim();
  if (!clean) return { success: false, error: 'Destination is required for weather.' };

  try {
    const res = await apiClient.get(`/weather?destination=${encodeURIComponent(clean)}`);
    return res.data;
  } catch (err) {
    return {
      success: false,
      error: normalizeApiError(err, `Unable to retrieve weather for '${clean}'.`),
      status: err.response?.status,
    };
  }
}

/**
 * Fetch verified hotel recommendations based on budget, area, tier, and itinerary proximity
 * @param {Object} params
 */
export async function getHotelRecommendations(params = {}) {
  try {
    const payload = {
      destination: (params.destination || '').trim() || 'Goa',
      budget: Number(params.budget) || 30000,
      travelers: Number(params.travelers) || 2,
      duration: Number(params.duration || params.days) || 3,
      preferred_area: params.preferredArea || params.preferred_area || null,
      tier: params.tier || null,
      sort_by: params.sortBy || params.sort_by || 'recommended',
      itinerary_places: Array.isArray(params.itineraryPlaces)
        ? params.itineraryPlaces
        : Array.isArray(params.itinerary_places)
        ? params.itinerary_places
        : [],
      preferences: Array.isArray(params.preferences) ? params.preferences : [],
    };

    const res = await apiClient.post('/hotels/recommend', payload);
    return { success: true, data: res.data };
  } catch (err) {
    return {
      success: false,
      error: normalizeApiError(err, 'Unable to fetch hotel recommendations.'),
    };
  }
}

/**
 * Fetch catalog of verified hotels for destination
 * @param {string} [destination]
 */
export async function getAllHotels(destination = '') {
  try {
    const url = destination ? `/hotels?destination=${encodeURIComponent(destination.trim())}` : '/hotels';
    const res = await apiClient.get(url);
    return { success: true, data: res.data };
  } catch (err) {
    return {
      success: false,
      error: normalizeApiError(err, 'Unable to load hotel catalogue.'),
    };
  }
}

// ==================== AUTHENTICATION & SAVED TRIPS API ====================

export function getToken() {
  return localStorage.getItem('tripgenie_token');
}

export function setToken(token) {
  if (token) {
    localStorage.setItem('tripgenie_token', token);
  } else {
    localStorage.removeItem('tripgenie_token');
  }
}

export function isAuthenticated() {
  return !!getToken();
}

export async function registerUser({ email, password, full_name }) {
  try {
    const res = await apiClient.post('/auth/register', {
      email: (email || '').trim().toLowerCase(),
      password,
      full_name: (full_name || '').trim(),
    });
    if (res.data?.access_token) {
      setToken(res.data.access_token);
    }
    return { success: true, data: res.data };
  } catch (err) {
    return {
      success: false,
      error: normalizeApiError(err, 'Registration failed.'),
    };
  }
}

export async function loginUser({ email, password }) {
  try {
    const res = await apiClient.post('/auth/login', {
      email: (email || '').trim().toLowerCase(),
      password,
    });
    if (res.data?.access_token) {
      setToken(res.data.access_token);
    }
    return { success: true, data: res.data };
  } catch (err) {
    return {
      success: false,
      error: normalizeApiError(err, 'Login failed. Please check your credentials.'),
    };
  }
}

export async function getCurrentUser() {
  try {
    const res = await apiClient.get('/auth/me');
    return { success: true, data: res.data };
  } catch (err) {
    return {
      success: false,
      error: normalizeApiError(err, 'Could not retrieve user session.'),
    };
  }
}

export function logoutUser() {
  setToken(null);
}

export async function saveTrip(tripPayload) {
  try {
    const res = await apiClient.post('/trips', tripPayload);
    return { success: true, data: res.data };
  } catch (err) {
    return {
      success: false,
      error: normalizeApiError(err, 'Failed to save trip to account.'),
      status: err.response?.status,
    };
  }
}

export async function getSavedTrips() {
  try {
    const res = await apiClient.get('/trips');
    return { success: true, data: res.data || [] };
  } catch (err) {
    return {
      success: false,
      data: [],
      error: normalizeApiError(err, 'Failed to retrieve saved trips.'),
    };
  }
}

export async function getTripById(tripId) {
  try {
    const res = await apiClient.get(`/trips/${tripId}`);
    return { success: true, data: res.data };
  } catch (err) {
    return {
      success: false,
      error: normalizeApiError(err, 'Could not load trip details.'),
    };
  }
}

export async function deleteTrip(tripId) {
  try {
    const res = await apiClient.delete(`/trips/${tripId}`);
    return { success: true, data: res.data };
  } catch (err) {
    return {
      success: false,
      error: normalizeApiError(err, 'Failed to delete trip.'),
    };
  }
}
