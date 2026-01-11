# Expo Go Performance Optimization Guide

## Why Expo Go Takes Long on Download Screen

The "download screen" in Expo Go refers to the initial bundle download and compilation. This can be slow due to:

1. **Large Bundle Size** - All JavaScript code needs to be bundled and downloaded
2. **Network Speed** - Slow internet connection
3. **Metro Bundler Compilation** - First-time compilation takes longer
4. **Heavy Dependencies** - Large libraries like react-native-paper, react-native-svg

## Optimizations Applied

### 1. Fixed Asset Bundle Patterns ⚡ **CRITICAL FIX**
- Changed `assetBundlePatterns` from `["**/*"]` to `["assets/**/*"]`
- **This was the main cause of 100+ second downloads** - it was bundling everything!
- Now only bundles necessary assets from the assets folder

### 2. Metro Bundler Optimization
- Created `metro.config.js` with:
  - Minification enabled
  - Inline requires for better code splitting
  - Optimized module ID factory

### 3. Lazy Screen Loading
- Implemented lazy loading for all screens using factory functions
- Screens are only loaded when navigated to, not on initial mount
- Reduces initial bundle size significantly

### 4. Lazy Tab Loading
- Added `lazy={true}` to Tab.Navigator
- Tabs are only loaded when accessed

### 5. AsyncStorage Timeout
- Added 2-second timeout to prevent indefinite loading
- App will show login screen if storage read times out

## Additional Optimization Tips

### 1. Use Development Build Instead of Expo Go
For better performance, consider using a development build:
```bash
npx expo prebuild
npx expo run:ios  # or run:android
```

### 2. Clear Metro Cache
If bundle is slow, clear cache:
```bash
npx expo start --clear
```

### 3. Use Production Mode
Production builds are faster:
```bash
NODE_ENV=production npx expo start
```

### 4. Optimize Network
- Use same WiFi network for phone and computer
- Use USB connection for Android (faster than WiFi)
- Use localhost tunnel for iOS simulator

### 5. Reduce Bundle Size
- Remove unused dependencies
- Use tree-shaking
- Consider removing heavy libraries if not needed

## Current Bundle Size
- node_modules: ~383MB (normal for React Native)
- Initial bundle: ~2-5MB (depends on dependencies)

## Expected Load Times (After Optimizations)
- First load: 5-15 seconds (download + compilation) ⚡ **Much faster!**
- Subsequent loads: 2-5 seconds (cached bundle)
- With slow network: 15-30 seconds (previously 100+ seconds)

## Troubleshooting

### If download is still slow (>30s):
1. **Clear Metro cache**: `npx expo start --clear` (IMPORTANT after config changes!)
2. Check network connection
3. Clear Expo Go cache (shake device → Reload)
4. Restart Metro bundler
5. Verify `assetBundlePatterns` is set to `["assets/**/*"]` not `["**/*"]`

### If app crashes on load:
1. Check console for errors
2. Verify all dependencies are installed
3. Check if backend is running
4. Try clearing AsyncStorage

## Performance Monitoring

To see bundle size:
```bash
npx expo export --platform ios
# Check .expo/web-build/ for bundle sizes
```

