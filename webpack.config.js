var path = require("path"),
    webpack = require("webpack");

var staticPrefix = "src/sentry/static/sentry",
    distPath = staticPrefix + "/dist";

module.exports = {
  context: path.join(__dirname, staticPrefix),
  entry: {
    "app": "app",
    "vendor": [
      "bootstrap/js/dropdown",
      "bootstrap/js/tooltip",
      "crypto-js/md5",
      "jquery",
      "moment",
      "raven-js",
      "react/addons",
      "react-document-title",
      "react-router",
      "react-bootstrap",
      "reflux",
      "flot/jquery.flot",
      "flot/jquery.flot.stack",
      "flot/jquery.flot.time",
      "flot-tooltip/jquery.flot.tooltip",
      "vendor/simple-slider/simple-slider"
    ]
  },
  module: {
    loaders: [
      {
        test: /\.jsx$/,
        loader: "jsx-loader?insertPragma=React.DOM&harmony",
        include: path.join(__dirname, staticPrefix),
        exclude: /vendor/
      }
    ]
  },
  plugins: [
    new webpack.optimize.CommonsChunkPlugin("vendor", distPath + "/vendor.js"),
    new webpack.optimize.UglifyJsPlugin(),
    new webpack.optimize.DedupePlugin(),
    new webpack.ProvidePlugin({
      $: 'jquery',
      jQuery: 'jquery',
      "window.jQuery": "jquery",
      "root.jQuery": "jquery"
    })
  ],
  resolve: {
    alias: {
      "app": path.join(__dirname, staticPrefix, "app"),
      "flot": path.join(__dirname, staticPrefix, "vendor", "jquery-flot"),
      "flot-tooltip": path.join(__dirname, staticPrefix, "vendor", "jquery-flot-tooltip"),
      "vendor": path.join(__dirname, staticPrefix, "vendor")
    },
    modulesDirectories: ["node_modules"],
    extensions: ["", ".jsx", ".js", ".json"]
  },
  output: {
    filename: distPath + "/[name].js",
    libraryTarget: "var",
    library: "exports"
  },
  devtool: 'source-map'
}
