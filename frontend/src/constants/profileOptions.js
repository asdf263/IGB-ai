/**
 * Profile options constants for dropdowns and selectors
 */

// US States and major countries
export const LOCATIONS = [
  // US States
  { label: 'Alabama', value: 'Alabama, USA' },
  { label: 'Alaska', value: 'Alaska, USA' },
  { label: 'Arizona', value: 'Arizona, USA' },
  { label: 'Arkansas', value: 'Arkansas, USA' },
  { label: 'California', value: 'California, USA' },
  { label: 'Colorado', value: 'Colorado, USA' },
  { label: 'Connecticut', value: 'Connecticut, USA' },
  { label: 'Delaware', value: 'Delaware, USA' },
  { label: 'Florida', value: 'Florida, USA' },
  { label: 'Georgia', value: 'Georgia, USA' },
  { label: 'Hawaii', value: 'Hawaii, USA' },
  { label: 'Idaho', value: 'Idaho, USA' },
  { label: 'Illinois', value: 'Illinois, USA' },
  { label: 'Indiana', value: 'Indiana, USA' },
  { label: 'Iowa', value: 'Iowa, USA' },
  { label: 'Kansas', value: 'Kansas, USA' },
  { label: 'Kentucky', value: 'Kentucky, USA' },
  { label: 'Louisiana', value: 'Louisiana, USA' },
  { label: 'Maine', value: 'Maine, USA' },
  { label: 'Maryland', value: 'Maryland, USA' },
  { label: 'Massachusetts', value: 'Massachusetts, USA' },
  { label: 'Michigan', value: 'Michigan, USA' },
  { label: 'Minnesota', value: 'Minnesota, USA' },
  { label: 'Mississippi', value: 'Mississippi, USA' },
  { label: 'Missouri', value: 'Missouri, USA' },
  { label: 'Montana', value: 'Montana, USA' },
  { label: 'Nebraska', value: 'Nebraska, USA' },
  { label: 'Nevada', value: 'Nevada, USA' },
  { label: 'New Hampshire', value: 'New Hampshire, USA' },
  { label: 'New Jersey', value: 'New Jersey, USA' },
  { label: 'New Mexico', value: 'New Mexico, USA' },
  { label: 'New York', value: 'New York, USA' },
  { label: 'North Carolina', value: 'North Carolina, USA' },
  { label: 'North Dakota', value: 'North Dakota, USA' },
  { label: 'Ohio', value: 'Ohio, USA' },
  { label: 'Oklahoma', value: 'Oklahoma, USA' },
  { label: 'Oregon', value: 'Oregon, USA' },
  { label: 'Pennsylvania', value: 'Pennsylvania, USA' },
  { label: 'Rhode Island', value: 'Rhode Island, USA' },
  { label: 'South Carolina', value: 'South Carolina, USA' },
  { label: 'South Dakota', value: 'South Dakota, USA' },
  { label: 'Tennessee', value: 'Tennessee, USA' },
  { label: 'Texas', value: 'Texas, USA' },
  { label: 'Utah', value: 'Utah, USA' },
  { label: 'Vermont', value: 'Vermont, USA' },
  { label: 'Virginia', value: 'Virginia, USA' },
  { label: 'Washington', value: 'Washington, USA' },
  { label: 'West Virginia', value: 'West Virginia, USA' },
  { label: 'Wisconsin', value: 'Wisconsin, USA' },
  { label: 'Wyoming', value: 'Wyoming, USA' },
  { label: 'Washington D.C.', value: 'Washington D.C., USA' },
  // International
  { label: '──── International ────', value: '', disabled: true },
  { label: 'Canada', value: 'Canada' },
  { label: 'United Kingdom', value: 'United Kingdom' },
  { label: 'Australia', value: 'Australia' },
  { label: 'Germany', value: 'Germany' },
  { label: 'France', value: 'France' },
  { label: 'Japan', value: 'Japan' },
  { label: 'South Korea', value: 'South Korea' },
  { label: 'China', value: 'China' },
  { label: 'India', value: 'India' },
  { label: 'Brazil', value: 'Brazil' },
  { label: 'Mexico', value: 'Mexico' },
  { label: 'Spain', value: 'Spain' },
  { label: 'Italy', value: 'Italy' },
  { label: 'Netherlands', value: 'Netherlands' },
  { label: 'Sweden', value: 'Sweden' },
  { label: 'Singapore', value: 'Singapore' },
  { label: 'Other', value: 'Other' },
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

// Format location for display (city, state)
export const formatLocationDisplay = (city, state) => {
  if (!city && !state) return '';
  if (city && state) return `${city}, ${state}`;
  return city || state || '';
};

