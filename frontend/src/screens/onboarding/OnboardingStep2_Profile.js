import React, { useState } from 'react';
import { View, StyleSheet, ScrollView, KeyboardAvoidingView, Platform } from 'react-native';
import { TextInput, Button, Text, Snackbar, ProgressBar, Menu, List, TouchableRipple } from 'react-native-paper';
import { US_STATES, ETHNICITIES, HEIGHT_CONSTRAINTS, validateHeight, formatHeightDisplay } from '../../constants/profileOptions';

const OnboardingStep2_Profile = ({ navigation, route }) => {
  const accountData = route.params?.accountData || {};
  
  const [name, setName] = useState('');
  const [instagramHandle, setInstagramHandle] = useState('');
  const [city, setCity] = useState('');
  const [state, setState] = useState('');
  const [showStateMenu, setShowStateMenu] = useState(false);
  const [ethnicity, setEthnicity] = useState('');
  const [showEthnicityMenu, setShowEthnicityMenu] = useState(false);
  const [height, setHeight] = useState('');
  const [showError, setShowError] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [heightError, setHeightError] = useState('');

  console.log('[ONBOARD-2] Rendering Step 2 - Profile');
  console.log('[ONBOARD-2] Account data received:', { email: accountData.email });

  // Validate height on change
  const handleHeightChange = (value) => {
    // Allow only numbers
    const cleaned = value.replace(/[^0-9]/g, '');
    setHeight(cleaned);
    
    if (cleaned) {
      const validation = validateHeight(cleaned);
      setHeightError(validation.error || '');
    } else {
      setHeightError('');
    }
  };

  const handleNext = () => {
    console.log('[ONBOARD-2] Next pressed');
    
    // Validate all required fields
    if (!name.trim()) {
      setErrorMessage('Full Name is required');
      setShowError(true);
      return;
    }

    if (!instagramHandle.trim()) {
      setErrorMessage('Instagram Handle is required');
      setShowError(true);
      return;
    }

    if (!city.trim()) {
      setErrorMessage('City is required');
      setShowError(true);
      return;
    }

    if (!state) {
      setErrorMessage('State is required');
      setShowError(true);
      return;
    }

    if (!ethnicity) {
      setErrorMessage('Ethnicity is required');
      setShowError(true);
      return;
    }

    if (!height.trim()) {
      setErrorMessage('Height is required');
      setShowError(true);
      return;
    }

    // Validate height value
    const validation = validateHeight(height);
    if (!validation.valid) {
      setErrorMessage(validation.error);
      setShowError(true);
      return;
    }

    const profileData = {
      name: name.trim(),
      instagram_handle: instagramHandle.trim().replace(/^@+/, ''),
      city: city.trim(),
      state: state,
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

  const handleStateSelect = (st) => {
    setState(st.value);
    setShowStateMenu(false);
  };

  const handleEthnicitySelect = (eth) => {
    setEthnicity(eth.value);
    setShowEthnicityMenu(false);
  };

  const getStateLabel = () => {
    const selected = US_STATES.find(s => s.value === state);
    return selected && selected.value ? selected.label : 'Select state *';
  };

  const getEthnicityLabel = () => {
    const selected = ETHNICITIES.find(e => e.value === ethnicity);
    return selected && selected.value ? selected.label : 'Select ethnicity *';
  };

  // Get height hint in feet/inches
  const getHeightHint = () => {
    if (!height || heightError) return null;
    return formatHeightDisplay(height);
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      keyboardVerticalOffset={Platform.OS === 'ios' ? 64 : 0}
    >
      <ScrollView 
        contentContainerStyle={styles.scrollContent} 
        keyboardShouldPersistTaps="handled"
        removeClippedSubviews={false}
      >
        <View style={styles.content}>
          <ProgressBar progress={0.5} color="#6200ee" style={styles.progressBar} />
          
          <Text variant="headlineSmall" style={styles.title}>
            Step 2 of 4: Your Profile
          </Text>
          <Text variant="bodyMedium" style={styles.subtitle}>
            All fields are required
          </Text>

          <TextInput
            label="Full Name *"
            value={name}
            onChangeText={setName}
            mode="outlined"
            style={styles.input}
            autoComplete="name"
          />

          <TextInput
            label="Instagram Handle *"
            value={instagramHandle}
            onChangeText={setInstagramHandle}
            mode="outlined"
            style={styles.input}
            autoCapitalize="none"
            autoCorrect={false}
            left={<TextInput.Affix text="@" />}
          />

          {/* City Input */}
          <TextInput
            label="City *"
            value={city}
            onChangeText={setCity}
            mode="outlined"
            style={styles.input}
            autoComplete="postal-address-locality"
          />

          {/* State Dropdown */}
          <View style={styles.dropdownContainer}>
            <Menu
              visible={showStateMenu}
              onDismiss={() => setShowStateMenu(false)}
              anchor={
                <TouchableRipple
                  onPress={() => setShowStateMenu(true)}
                  style={styles.dropdownButton}
                >
                  <View style={styles.dropdownButtonContent}>
                    <Text style={state ? styles.dropdownText : styles.dropdownPlaceholder}>
                      {getStateLabel()}
                    </Text>
                    <List.Icon icon="menu-down" />
                  </View>
                </TouchableRipple>
              }
              style={styles.menu}
              contentStyle={styles.menuContent}
            >
              <ScrollView style={styles.menuScroll} nestedScrollEnabled>
                {US_STATES.filter(s => s.value !== '').map((st) => (
                  <Menu.Item
                    key={st.value}
                    onPress={() => handleStateSelect(st)}
                    title={st.label}
                    style={state === st.value ? styles.selectedMenuItem : null}
                  />
                ))}
              </ScrollView>
            </Menu>
          </View>

          {/* Ethnicity Dropdown */}
          <View style={styles.dropdownContainer}>
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
              <ScrollView style={styles.menuScroll} nestedScrollEnabled>
                {ETHNICITIES.filter(e => e.value !== '').map((eth) => (
                  <Menu.Item
                    key={eth.value}
                    onPress={() => handleEthnicitySelect(eth)}
                    title={eth.label}
                    style={ethnicity === eth.value ? styles.selectedMenuItem : null}
                  />
                ))}
              </ScrollView>
            </Menu>
          </View>

          {/* Height Input (inches only) */}
          <View style={styles.heightSection}>
            <TextInput
              label={`Height in inches * (${HEIGHT_CONSTRAINTS.min}-${HEIGHT_CONSTRAINTS.max})`}
              value={height}
              onChangeText={handleHeightChange}
              mode="outlined"
              style={styles.input}
              keyboardType="number-pad"
              placeholder={HEIGHT_CONSTRAINTS.placeholder}
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
  scrollContent: { flexGrow: 1, padding: 20, paddingBottom: 40 },
  content: { width: '100%', maxWidth: 400, alignSelf: 'center', marginTop: 10 },
  progressBar: { marginBottom: 20, height: 4, borderRadius: 2 },
  title: { textAlign: 'center', marginBottom: 4, fontWeight: 'bold' },
  subtitle: { textAlign: 'center', marginBottom: 24, color: '#666' },
  input: { marginBottom: 12, backgroundColor: '#fff' },
  dropdownContainer: { 
    marginBottom: 12,
  },
  dropdownButton: {
    borderWidth: 1,
    borderColor: '#79747E',
    borderRadius: 4,
    backgroundColor: '#fff',
    height: 56,
  },
  dropdownButtonContent: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 16,
    paddingHorizontal: 12,
    height: 56,
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
    width: '92%',
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
    marginBottom: 12,
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
  buttonRow: { flexDirection: 'row', marginTop: 8, gap: 12 },
  backButton: { flex: 1 },
  nextButton: { flex: 1 },
});

export default OnboardingStep2_Profile;
