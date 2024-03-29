var webpack = require('webpack');
var WebpackDevServer = require('webpack-dev-server');
var config = require('./retina_scan/config/webpack.config.development');

new WebpackDevServer(webpack(config), {
  publicPath: config.output.publicPath,
  hot: true,
  inline: true,
  historyApiFallback: true
}).listen(3001, '0.0.0.0', function (err, result) {
  if (err) {
    console.log(err);
  }

  console.log('Listening at 0.0.0.0:3001');
});