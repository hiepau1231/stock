const path = require('path');

module.exports = {
    entry: './frontend/src/index.js',
    output: {
        path: path.resolve(__dirname, 'static/frontend/'),
        filename: 'bundle.js',
    },
    module: {
        rules: [
            {
                test: /\.(js|jsx)$/,
                exclude: /node_modules/,
                use: ['babel-loader'],
            },
            {
                test: /\.css$/,
                use: ['style-loader', 'css-loader'],
            },
            // Add more loaders as needed
        ],
    },
    resolve: {
        extensions: ['*', '.js', '.jsx'],
    },
    devServer: {
        contentBase: path.join(__dirname, 'static/frontend/'),
        compress: true,
        port: 9000,
    },
};
