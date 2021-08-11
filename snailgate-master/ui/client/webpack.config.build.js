var sharedConfig = require('./webpack.config.shared.js');

module.exports = Object.assign(
  {},
  sharedConfig,
  { 
    output: {
      filename: '../server/static/bundle.js'
    },
    entry: [
      './index.js'
    ]
  }
)
