var sharedConfig = require('./webpack.config.shared.js');

var path = require('path');
var resolve = path.resolve;
var webpack = require('webpack');

module.exports = Object.assign(
  {},
  sharedConfig,
  { 
    entry: [
      'react-hot-loader/patch',
      // activate HMR for React

      'webpack-dev-server/client?http://localhost:8080',
      // bundle the client for webpack-dev-server
      // and connect to the provided endpoint

      'webpack/hot/only-dev-server',
      // bundle the client for hot reloading
      // only- means to only hot reload for successful updates

      './index.js'
    ],
    devServer: {
      hot: true,
      // enable HMR on the server

      contentBase: resolve(__dirname, 'dist'),
      // match the output path

      publicPath: '/'
      // match the output `publicPath`
    },
    plugins: [
      new webpack.HotModuleReplacementPlugin(),
      // enable HMR globally

      new webpack.NamedModulesPlugin(),
      // prints more readable module names in the browser console on HMR updates
    ]
  }
);
