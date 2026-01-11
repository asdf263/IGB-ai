/**
 * Profile options constants for dropdowns and selectors
 */

// US States with abbreviations
export const US_STATES = [
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
  { label: 'Select ethnicity', value: '' },
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

// Age constraints
export const AGE_CONSTRAINTS = {
  min: 13,
  max: 120,
  placeholder: '21',
};

// Helper function to validate age
export const validateAge = (value) => {
  const numValue = parseInt(value, 10);
  if (isNaN(numValue)) {
    return { valid: false, error: 'Please enter a valid age' };
  }
  
  if (numValue < AGE_CONSTRAINTS.min) {
    return { valid: false, error: `Age must be at least ${AGE_CONSTRAINTS.min}` };
  }
  
  if (numValue > AGE_CONSTRAINTS.max) {
    return { valid: false, error: `Age cannot exceed ${AGE_CONSTRAINTS.max}` };
  }
  
  return { valid: true, error: null };
};

// Height constraints
export const HEIGHT_CONSTRAINTS = {
  cm: {
    min: 100,
    max: 250,
    placeholder: '170',
  },
  in: {
    min: 40,
    max: 98,
    placeholder: '67',
  },
  ft: {
    // For feet + inches combined input
    minFeet: 3,
    maxFeet: 8,
    minInches: 0,
    maxInches: 11,
  },
};

// Helper function to validate height
export const validateHeight = (value, unit) => {
  const numValue = parseFloat(value);
  if (isNaN(numValue)) {
    return { valid: false, error: 'Please enter a valid number' };
  }
  
  const constraints = HEIGHT_CONSTRAINTS[unit];
  if (!constraints) {
    return { valid: false, error: 'Invalid unit' };
  }
  
  if (numValue < constraints.min) {
    return { valid: false, error: `Height must be at least ${constraints.min} ${unit}` };
  }
  
  if (numValue > constraints.max) {
    return { valid: false, error: `Height cannot exceed ${constraints.max} ${unit}` };
  }
  
  return { valid: true, error: null };
};

// Helper function to convert height between units
export const convertHeight = (value, fromUnit, toUnit) => {
  const numValue = parseFloat(value);
  if (isNaN(numValue)) return '';
  
  if (fromUnit === toUnit) return value;
  
  if (fromUnit === 'cm' && toUnit === 'in') {
    return (numValue / 2.54).toFixed(1);
  }
  
  if (fromUnit === 'in' && toUnit === 'cm') {
    return (numValue * 2.54).toFixed(1);
  }
  
  return value;
};

// Format height for display
export const formatHeightDisplay = (value, unit) => {
  if (!value) return '';
  const numValue = parseFloat(value);
  if (isNaN(numValue)) return value;
  
  // If no unit provided, try to guess based on value
  // Heights > 100 are likely cm, < 100 are likely inches
  const effectiveUnit = unit || (numValue > 100 ? 'cm' : 'in');
  
  if (effectiveUnit === 'in') {
    const feet = Math.floor(numValue / 12);
    const inches = Math.round(numValue % 12);
    return `${feet}'${inches}"`;
  }
  
  if (effectiveUnit === 'cm') {
    // Convert to feet/inches for display
    const totalInches = numValue / 2.54;
    const feet = Math.floor(totalInches / 12);
    const inches = Math.round(totalInches % 12);
    return `${feet}'${inches}" (${numValue} cm)`;
  }
  
  return `${numValue} ${effectiveUnit || ''}`.trim();
};

// Format location for display (city, state abbreviation)
export const formatLocationDisplay = (city, state) => {
  if (!city && !state) return '';
  if (city && state) return `${city}, ${state}`;
  return city || state || '';
};

// Get full state name from abbreviation
export const getStateName = (abbrev) => {
  const state = US_STATES.find(s => s.value === abbrev);
  return state ? state.label : abbrev;
};

