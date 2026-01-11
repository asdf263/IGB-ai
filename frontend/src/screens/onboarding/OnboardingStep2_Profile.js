import React, { useState } from 'react';
import { View, StyleSheet, ScrollView, KeyboardAvoidingView, Platform } from 'react-native';
import { TextInput, Button, Text, Snackbar, ProgressBar, Menu, List, TouchableRipple } from 'react-native-paper';
import { ETHNICITIES, HEIGHT_CONSTRAINTS, validateHeight, AGE_CONSTRAINTS, validateAge } from '../../constants/profileOptions';

const OnboardingStep2_Profile = ({ navigation, route }) => {
  const accountData = route.params?.accountData || {};
  
  const [name, setName] = useState('');
  const [age, setAge] = useState('');
  const [ageError, setAgeError] = useState('');
  const [instagramHandle, setInstagramHandle] = useState('');
  const [city, setCity] = useState('');
  const [country, setCountry] = useState('');
  const [ethnicity, setEthnicity] = useState('');
  const [showEthnicityMenu, setShowEthnicityMenu] = useState(false);
  const [height, setHeight] = useState('');
  const [showError, setShowError] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [heightError, setHeightError] = useState('');

  console.log('[ONBOARD-2] Rendering Step 2 - Profile');
  console.log('[ONBOARD-2] Account data received:', { email: accountData.email });

  // Validate age on change
  const handleAgeChange = (value) => {
    // Allow only numbers
    const cleaned = value.replace(/[^0-9]/g, '');
    setAge(cleaned);
    
    if (cleaned) {
      const validation = validateAge(cleaned);
      setAgeError(validation.error || '');
    } else {
      setAgeError('');
    }
  };

  // Validate height on change (inches only)
  const handleHeightChange = (value) => {
    // Allow only numbers
    const cleaned = value.replace(/[^0-9]/g, '');
    setHeight(cleaned);
    
    if (cleaned) {
      const validation = validateHeight(cleaned, 'in');
      setHeightError(validation.error || '');
    } else {
      setHeightError('');
    }
  };

  // Format height as feet and inches for display hint
  const getHeightHint = () => {
    if (!height || heightError) return null;
    const inches = parseInt(height, 10);
    const feet = Math.floor(inches / 12);
    const remainingInches = inches % 12;
    return `${feet}'${remainingInches}"`;
  };

  const handleNext = () => {
    console.log('[ONBOARD-2] Next pressed');
    if (!name.trim()) {
      setErrorMessage('Name is required');
      setShowError(true);
      return;
    }

    // Validate age if provided
    if (age) {
      const ageValidation = validateAge(age);
      if (!ageValidation.valid) {
        setErrorMessage(ageValidation.error);
        setShowError(true);
        return;
      }
    }

    // Validate height if provided (inches only)
    if (height) {
      const validation = validateHeight(height, 'in');
      if (!validation.valid) {
        setErrorMessage(validation.error);
        setShowError(true);
        return;
      }
    }

    const profileData = {
      name: name.trim(),
      age: age ? parseInt(age, 10) : null,
      instagram_handle: instagramHandle.trim().replace(/^@+/, ''),
      city: city.trim(),
      country: country.trim(),
      ethnicity: ethnicity,
      height: height.trim(),
    };

    console.log('[ONBOARD-2] Navigating to Step 3 with profile data');
    navigation.navigate('OnboardingStep3', {
      accountData,
      profileData,
    });
  };

  const handleBack = () => {
    navigation.goBack();
  };

  const handleEthnicitySelect = (eth) => {
    setEthnicity(eth.value);
    setShowEthnicityMenu(false);
  };

  const getEthnicityLabel = () => {
    const selected = ETHNICITIES.find(e => e.value === ethnicity);
    return selected ? selected.label : 'Select ethnicity';
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView contentContainerStyle={styles.scrollContent} keyboardShouldPersistTaps="handled">
        <View style={styles.content}>
          <ProgressBar progress={0.5} color="#6200ee" style={styles.progressBar} />
          
          <Text variant="headlineSmall" style={styles.title}>
            Step 2 of 4: Your Profile
          </Text>
          <Text variant="bodyMedium" style={styles.subtitle}>
            Tell us about yourself
          </Text>

          <TextInput
            label="Full Name *"
            value={name}
            onChangeText={setName}
            mode="outlined"
            style={styles.input}
          />

          <TextInput
            label="Age"
            value={age}
            onChangeText={handleAgeChange}
            mode="outlined"
            style={styles.input}
            keyboardType="number-pad"
            placeholder={AGE_CONSTRAINTS.placeholder}
            error={!!ageError}
          />
          {ageError ? (
            <Text style={styles.errorText}>{ageError}</Text>
          ) : null}

          <TextInput
            label="Instagram Handle"
            value={instagramHandle}
            onChangeText={setInstagramHandle}
            mode="outlined"
            style={styles.input}
            autoCapitalize="none"
            placeholder="@username"
          />

          {/* City Input */}
          <TextInput
            label="City"
            value={city}
            onChangeText={setCity}
            mode="outlined"
            style={styles.input}
            placeholder="e.g. Los Angeles"
          />

          {/* Country Input */}
          <TextInput
            label="Country"
            value={country}
            onChangeText={setCountry}
            mode="outlined"
            style={styles.input}
            placeholder="e.g. United States"
          />

          {/* Ethnicity Dropdown */}
          <View style={styles.dropdownContainer}>
            <Text variant="bodySmall" style={styles.fieldLabel}>Ethnicity</Text>
            <Menu
              visible={showEthnicityMenu}
              onDismiss={() => setShowEthnicityMenu(false)}
              anchor={
                <TouchableRipple
                  onPress={() => setShowEthnicityMenu(true)}
                  style={styles.dropdownButton}
                >
                  <View style={styles.dropdownButtonContent}>
                    <Text style={ethnicity ? styles.dropdownText : styles.dropdownPlaceholder}>
                      {getEthnicityLabel()}
                    </Text>
                    <List.Icon icon="menu-down" />
                  </View>
                </TouchableRipple>
              }
              style={styles.menu}
              contentStyle={styles.menuContent}
            >
              {ETHNICITIES.filter(e => e.value !== '').map((eth) => (
                <Menu.Item
                  key={eth.value}
                  onPress={() => handleEthnicitySelect(eth)}
                  title={eth.label}
                  style={ethnicity === eth.value ? styles.selectedMenuItem : null}
                />
              ))}
            </Menu>
          </View>

          {/* Height Input (inches only) */}
          <View style={styles.heightSection}>
            <TextInput
              label={`Height in inches (${HEIGHT_CONSTRAINTS.in.min}-${HEIGHT_CONSTRAINTS.in.max})`}
              value={height}
              onChangeText={handleHeightChange}
              mode="outlined"
              style={styles.input}
              keyboardType="number-pad"
              placeholder={HEIGHT_CONSTRAINTS.in.placeholder}
              error={!!heightError}
              right={<TextInput.Affix text="in" />}
            />
            {heightError ? (
              <Text variant="bodySmall" style={styles.errorText}>{heightError}</Text>
            ) : height ? (
              <Text variant="bodySmall" style={styles.heightHint}>
                {getHeightHint()}
              </Text>
            ) : null}
          </View>

          <View style={styles.buttonRow}>
            <Button mode="outlined" onPress={handleBack} style={styles.backButton}>
              Back
            </Button>
            <Button mode="contained" onPress={handleNext} style={styles.nextButton}>
              Next
            </Button>
          </View>
        </View>
      </ScrollView>

      <Snackbar
        visible={showError}
        onDismiss={() => setShowError(false)}
        duration={3000}
      >
        {errorMessage}
      </Snackbar>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f5f5' },
  scrollContent: { flexGrow: 1, padding: 20 },
  content: { width: '100%', maxWidth: 400, alignSelf: 'center', marginTop: 20 },
  progressBar: { marginBottom: 24, height: 4, borderRadius: 2 },
  title: { textAlign: 'center', marginBottom: 8, fontWeight: 'bold' },
  subtitle: { textAlign: 'center', marginBottom: 32, color: '#666' },
  input: { marginBottom: 16 },
  fieldLabel: { 
    color: '#666', 
    marginBottom: 4,
    marginLeft: 4,
  },
  dropdownContainer: { 
    marginBottom: 16,
    zIndex: 1,
  },
  dropdownButton: {
    borderWidth: 1,
    borderColor: '#79747E',
    borderRadius: 4,
    backgroundColor: '#fff',
  },
  dropdownButtonContent: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 12,
    paddingHorizontal: 12,
  },
  dropdownText: {
    fontSize: 16,
    color: '#1C1B1F',
  },
  dropdownPlaceholder: {
    fontSize: 16,
    color: '#79747E',
  },
  menu: { 
    width: '100%',
    maxWidth: 360,
  },
  menuContent: {
    backgroundColor: '#fff',
  },
  menuScroll: {
    maxHeight: 300,
  },
  selectedMenuItem: {
    backgroundColor: '#E8DEF8',
  },
  heightSection: {
    marginBottom: 16,
  },
  heightHint: {
    color: '#6200ee',
    marginTop: 4,
    marginLeft: 4,
    fontWeight: '500',
  },
  errorText: {
    color: '#B3261E',
    marginTop: 4,
    marginLeft: 4,
  },
  buttonRow: { flexDirection: 'row', marginTop: 16, gap: 12 },
  backButton: { flex: 1 },
  nextButton: { flex: 1 },
});

export default OnboardingStep2_Profile;
