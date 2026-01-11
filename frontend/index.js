// #region agent log
console.log('[INDEX] index.js loading - VERY FIRST LINE');
// #endregion

import 'expo/src/Expo.fx';
import { registerRootComponent } from 'expo';

// #region agent log
console.log('[INDEX] imports complete, about to import App');
// #endregion

import App from './App';

// #region agent log
console.log('[INDEX] App imported, about to register');
// #endregion

registerRootComponent(App);

// #region agent log
console.log('[INDEX] registerRootComponent called');
// #endregion
