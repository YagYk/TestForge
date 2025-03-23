/**
 * Utility script to fix the Spline tool dependencies
 * Run with: node fix-spline.js
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('Starting Spline dependency fix...');

// Check if package.json exists
const packageJsonPath = path.join(__dirname, 'package.json');
if (!fs.existsSync(packageJsonPath)) {
  console.error('Error: Could not find package.json in the current directory');
  process.exit(1);
}

try {
  // Read the current package.json
  const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
  
  // Check if splinetool dependencies exist
  const hasReactSpline = packageJson.dependencies && packageJson.dependencies['@splinetool/react-spline'];
  
  if (!hasReactSpline) {
    console.log('No @splinetool/react-spline dependency found in package.json');
    console.log('Adding it with a compatible version...');
  } else {
    console.log(`Found @splinetool/react-spline version: ${packageJson.dependencies['@splinetool/react-spline']}`);
    console.log('Updating to a compatible version...');
  }
  
  // Create a backup of package.json
  fs.copyFileSync(packageJsonPath, path.join(__dirname, 'package.json.backup'));
  console.log('Created backup of package.json');
  
  // Uninstall existing splinetool dependencies
  console.log('Removing existing Spline dependencies...');
  execSync('npm uninstall @splinetool/react-spline @splinetool/runtime', { stdio: 'inherit' });
  
  // Install specific versions of the dependencies
  console.log('Installing compatible versions of Spline dependencies...');
  execSync('npm install @splinetool/react-spline@2.2.6 @splinetool/runtime@0.9.369', { stdio: 'inherit' });
  
  console.log('Clearing npm cache...');
  execSync('npm cache clean --force', { stdio: 'inherit' });
  
  console.log('Cleanup node_modules...');
  const nodeModulesSplinePath = path.join(__dirname, 'node_modules', '@splinetool');
  if (fs.existsSync(nodeModulesSplinePath)) {
    console.log('Removing Spline from node_modules to ensure clean reinstall');
    try {
      execSync(`rimraf "${nodeModulesSplinePath}"`, { stdio: 'inherit' });
    } catch (e) {
      console.log('Could not use rimraf, trying manual deletion');
      try {
        fs.rmdirSync(nodeModulesSplinePath, { recursive: true });
      } catch (e2) {
        console.warn('Warning: Could not remove @splinetool directory. You may need to delete it manually.');
      }
    }
  }
  
  console.log('Reinstalling dependencies...');
  execSync('npm install', { stdio: 'inherit' });
  
  console.log('\nSpline dependency fix completed!');
  console.log('\nNext steps:');
  console.log('1. Delete the build directory: npm run clean (or manually delete the build folder)');
  console.log('2. Restart the development server: npm start');
  console.log('3. If issues persist, try using the fallback mode in the application');
  
} catch (error) {
  console.error('Error fixing Spline dependencies:', error);
  process.exit(1);
} 