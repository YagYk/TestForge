// Custom override for webpack to fix chunk loading errors
const webpack = require('webpack');

module.exports = function override(config, env) {
  // Add environment variables to the build
  config.plugins.push(
    new webpack.DefinePlugin({
      'process.env.REACT_APP_DISABLE_SPLINE': JSON.stringify(process.env.REACT_APP_DISABLE_SPLINE)
    })
  );
  
  // Modify chunking strategy
  if (config.optimization && config.optimization.splitChunks) {
    config.optimization.splitChunks.cacheGroups = {
      ...config.optimization.splitChunks.cacheGroups,
      // Prevent Splinetool from being split into chunks
      splineVendors: {
        test: /[\\/]node_modules[\\/](@splinetool)[\\/]/,
        name: 'spline-vendors',
        chunks: 'all',
        enforce: true,
        priority: 10,
      },
    };
  }
  
  // Add resolver fallbacks for problematic modules
  if (!config.resolve) config.resolve = {};
  if (!config.resolve.fallback) config.resolve.fallback = {};
  
  config.resolve.fallback = {
    ...config.resolve.fallback,
    fs: false,
    path: false,
    crypto: false,
    stream: false,
    zlib: false,
  };
  
  // Return the modified config
  return config;
};  
module.exports = function override(config, env) { 
  // Add environment variables to the build 
  config.plugins.push( 
    new webpack.DefinePlugin({ 
      'process.env.REACT_APP_DISABLE_SPLINE': JSON.stringify(process.env.REACT_APP_DISABLE_SPLINE) 
    }) 
  ); 
 
  // Modify chunking strategy 
  if (config.optimization && config.optimization.splitChunks) { 
    config.optimization.splitChunks.cacheGroups = { 
      ...config.optimization.splitChunks.cacheGroups, 
      // Prevent Splinetool from being split into chunks 
      splineVendors: { 
        test: /[\\\/]node_modules[\\\/](@splinetool)[\\\/]/, 
        name: 'spline-vendors', 
        chunks: 'all', 
        enforce: true, 
        priority: 10, 
      }, 
    }; 
  } 
 
  // Add resolver fallbacks for problematic modules 
  if (!config.resolve) config.resolve = {}; 
  if (!config.resolve.fallback) config.resolve.fallback = {}; 
 
  config.resolve.fallback = { 
    ...config.resolve.fallback, 
    fs: false, 
    path: false, 
    crypto: false, 
    stream: false, 
    zlib: false, 
  }; 
 
  // Return the modified config 
  return config; 
}; 
