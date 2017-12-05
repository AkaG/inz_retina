var path = require("path")
var webpack = require('webpack');

module.exports = {
  context: __dirname,

  entry: '../../static_src/js/index',

  output: {
      path: path.resolve('./static_src/bundles/'),
      filename: "[name].js"
  },

  plugins: [],

  module: {
    loaders: []
  }
};