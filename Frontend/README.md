# TestForge Frontend

This is the frontend for the TestForge application, a modern test case generation tool.

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm start
   ```

3. Build for production:
   ```bash
   npm run build
   ```

## Troubleshooting

### Fixing Spline 3D Component Chunk Loading Errors

If you encounter errors like "Loading chunk X failed" or issues with the 3D component on the home page, we provide tools to fix these issues:

#### Automatic Fix (Windows)

For Windows users, simply run the `fix_spline_errors.bat` file in the Frontend directory:

1. Open File Explorer and navigate to the Frontend folder
2. Double-click on `fix_spline_errors.bat`
3. Follow the prompts to apply the fixes

#### Automatic Fix (All Platforms)

Run the JavaScript fix script directly:

```bash
# Navigate to Frontend directory
cd Frontend

# Run the fix script
node fix_chunk_error.js
```

The script will:
1. Create a `.env` file with webpack optimization flags
2. Add webpack configuration overrides
3. Modify the 3D component loading to prevent errors
4. Update package.json to use these overrides

#### Manual Fix

If the automatic fixes don't work, you can apply these changes manually:

1. Create a `.env` file in the Frontend directory with:
   ```
   GENERATE_SOURCEMAP=false
   INLINE_RUNTIME_CHUNK=false
   REACT_APP_DISABLE_SPLINE=true
   ```

2. Install react-app-rewired:
   ```bash
   npm install --save-dev react-app-rewired
   ```

3. Create a `config-overrides.js` file in the Frontend directory with webpack configuration overrides

4. Update your package.json scripts to use react-app-rewired instead of react-scripts

5. Clean and rebuild:
   ```bash
   rm -rf build
   npm run build
   ```

### Other Common Issues

#### API Connection Issues

If you're experiencing API connection issues:

1. Make sure the Flask backend is running at http://localhost:5000
2. Check the server status using: `python server_manager.py check`
3. Restart the server if needed: `python server_manager.py restart`

## Deployment

To build the application for production, use:

```bash
npm run build
```

This creates an optimized production build in the `build` folder.

## More Information

For more details on using the TestForge application, see the main [TestForge README](../README.md). 