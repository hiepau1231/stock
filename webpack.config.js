const path = require('path');
const webpack = require('webpack');
const Dotenv = require('dotenv-webpack');

module.exports = {
    entry: './frontend/src/index.js',
    output: {
        path: path.resolve(__dirname, 'frontend/static/frontend/'),
        filename: 'main.js',
        publicPath: '/static/frontend/',
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
            {
                test: /\.(png|svg|jpg|gif)$/,
                use: ['file-loader'],
            },
        ],
    },
    resolve: {
        extensions: ['*', '.js', '.jsx'],
    },
    plugins: [
        new Dotenv(),
        new webpack.HotModuleReplacementPlugin(),
    ],
    devServer: {
        contentBase: path.join(__dirname, 'frontend/static/frontend/'),
        publicPath: '/static/frontend/',
        hot: true,
        port: 3000,
        proxy: {
            '/api': 'http://localhost:8000',
            '/ws': {
                target: 'ws://localhost:8000',
                ws: true,
            },
        },
    },
};