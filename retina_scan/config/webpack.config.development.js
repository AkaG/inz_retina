var path = require("path");
var webpack = require('webpack');
var config = require('./webpack.config.base.js');
var BundleTracker = require('webpack-bundle-tracker');

// use webpack dev server
config.entry = [
  'webpack-dev-server/client?http://localhost:3001',
  '../../static_src/js/index'
];

// override django's STATIC_URL for webpack bundles
config.output.publicPath = 'http://localhost:3001/static_src/bundles/'

// Add HotModuleReplacementPlugin and BundleTracker plugins
config.plugins = config.plugins.concat([
  new webpack.HotModuleReplacementPlugin(),
  new webpack.SourceMapDevToolPlugin({filename: '[file].map'}),
  new BundleTracker({filename: './webpack-stats.json'})
]);

config.module.loaders.push(
  { test: /\.js$/, exclude: /node_modules/, loaders: ['babel-loader'], },
  { test: /\.scss$/, loader: "style-loader!css-loader!postcss-loader!sass-loader" }
);

module.exports = config;