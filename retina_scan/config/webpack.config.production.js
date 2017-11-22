var webpack = require('webpack');
var config = require('./webpack.config.base.js');
var ExtractTextPlugin = require("extract-text-webpack-plugin");
var BundleTracker = require('webpack-bundle-tracker');
var extractCSS = new ExtractTextPlugin('styles/[name].css');

config.output.path = require('path').resolve('./static/dist/');

config.plugins = config.plugins.concat([
  // sets the node env to production
  new webpack.DefinePlugin({'process.env': {'NODE_ENV': JSON.stringify('production')}}),
  // minifies code
  new webpack.optimize.UglifyJsPlugin({compressor: {warnings: false}}),
  // stats file is used to determine static files location
  new BundleTracker({filename: './webpack-stats-prod.json'}),
  // builds a css file
  extractCSS,
]);

config.module.loaders.push(
  { test: /\.scss$/,
    use: extractCSS.extract([
      {
        loader: 'css-loader',
        options: {
          minimize: true
        }
      },
      {
        loader: 'postcss-loader',
      },
      {
        loader: 'sass-loader',
      },
    ]),
  },
  { test: /\.js$/, exclude: /node_modules/, loader: 'babel-loader' }
);

module.exports = config;