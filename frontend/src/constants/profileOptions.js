/**
 * Profile options constants for dropdowns and selectors
 */

// US States for state dropdown
export const US_STATES = [
  { label: 'Select state *', value: '' },
  { label: 'Alabama', value: 'AL' },
  { label: 'Alaska', value: 'AK' },
  { label: 'Arizona', value: 'AZ' },
  { label: 'Arkansas', value: 'AR' },
  { label: 'California', value: 'CA' },
  { label: 'Colorado', value: 'CO' },
  { label: 'Connecticut', value: 'CT' },
  { label: 'Delaware', value: 'DE' },
  { label: 'Florida', value: 'FL' },
  { label: 'Georgia', value: 'GA' },
  { label: 'Hawaii', value: 'HI' },
  { label: 'Idaho', value: 'ID' },
  { label: 'Illinois', value: 'IL' },
  { label: 'Indiana', value: 'IN' },
  { label: 'Iowa', value: 'IA' },
  { label: 'Kansas', value: 'KS' },
  { label: 'Kentucky', value: 'KY' },
  { label: 'Louisiana', value: 'LA' },
  { label: 'Maine', value: 'ME' },
  { label: 'Maryland', value: 'MD' },
  { label: 'Massachusetts', value: 'MA' },
  { label: 'Michigan', value: 'MI' },
  { label: 'Minnesota', value: 'MN' },
  { label: 'Mississippi', value: 'MS' },
  { label: 'Missouri', value: 'MO' },
  { label: 'Montana', value: 'MT' },
  { label: 'Nebraska', value: 'NE' },
  { label: 'Nevada', value: 'NV' },
  { label: 'New Hampshire', value: 'NH' },
  { label: 'New Jersey', value: 'NJ' },
  { label: 'New Mexico', value: 'NM' },
  { label: 'New York', value: 'NY' },
  { label: 'North Carolina', value: 'NC' },
  { label: 'North Dakota', value: 'ND' },
  { label: 'Ohio', value: 'OH' },
  { label: 'Oklahoma', value: 'OK' },
  { label: 'Oregon', value: 'OR' },
  { label: 'Pennsylvania', value: 'PA' },
  { label: 'Rhode Island', value: 'RI' },
  { label: 'South Carolina', value: 'SC' },
  { label: 'South Dakota', value: 'SD' },
  { label: 'Tennessee', value: 'TN' },
  { label: 'Texas', value: 'TX' },
  { label: 'Utah', value: 'UT' },
  { label: 'Vermont', value: 'VT' },
  { label: 'Virginia', value: 'VA' },
  { label: 'Washington', value: 'WA' },
  { label: 'West Virginia', value: 'WV' },
  { label: 'Wisconsin', value: 'WI' },
  { label: 'Wyoming', value: 'WY' },
  { label: 'Washington D.C.', value: 'DC' },
];

// Ethnicity options based on US Census categories with additional options
export const ETHNICITIES = [
  { label: 'Select ethnicity *', value: '' },
  { label: 'Asian', value: 'Asian' },
  { label: 'Black or African American', value: 'Black or African American' },
  { label: 'Hispanic or Latino', value: 'Hispanic or Latino' },
  { label: 'Native American or Alaska Native', value: 'Native American or Alaska Native' },
  { label: 'Native Hawaiian or Pacific Islander', value: 'Native Hawaiian or Pacific Islander' },
  { label: 'White', value: 'White' },
  { label: 'Middle Eastern or North African', value: 'Middle Eastern or North African' },
  { label: 'Two or More Races', value: 'Two or More Races' },
  { label: 'Prefer not to say', value: 'Prefer not to say' },
  { label: 'Other', value: 'Other' },
];

// Height constraints (inches only)
export const HEIGHT_CONSTRAINTS = {
  min: 48,  // 4'0"
  max: 96,  // 8'0"
  placeholder: '68',
};

// Helper function to validate height (inches only)
export const validateHeight = (value) => {
  const numValue = parseFloat(value);
  if (isNaN(numValue)) {
    return { valid: false, error: 'Please enter a valid number' };
  }
  
  if (numValue < HEIGHT_CONSTRAINTS.min) {
    return { valid: false, error: `Height must be at least ${HEIGHT_CONSTRAINTS.min} inches (4'0")` };
  }
  
  if (numValue > HEIGHT_CONSTRAINTS.max) {
    return { valid: false, error: `Height cannot exceed ${HEIGHT_CONSTRAINTS.max} inches (8'0")` };
  }
  
  return { valid: true, error: null };
};

// Format height for display (always in feet/inches format)
export const formatHeightDisplay = (value) => {
  if (!value) return '';
  const numValue = parseFloat(value);
  if (isNaN(numValue)) return value;
  
  const feet = Math.floor(numValue / 12);
  const inches = Math.round(numValue % 12);
  return `${feet}'${inches}"`;
};

// Get state label from value
export const getStateLabel = (value) => {
  const state = US_STATES.find(s => s.value === value);
  return state ? state.label : value;
};

// Format location for display (city, state)
export const formatLocationDisplay = (city, state) => {
  if (!city && !state) return 'Not specified';
  if (!state) return city;
  if (!city) return getStateLabel(state);
  return `${city}, ${getStateLabel(state)}`;
};
