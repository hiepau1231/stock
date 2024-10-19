import React, { useState, useEffect } from 'react';
import axios from 'axios';

const StockList = () => {
    const [stocks, setStocks] = useState([]);

    useEffect(() => {
        const fetchStocks = async () => {
            try {
                const response = await axios.get('/api/stocks/');
                setStocks(response.data);
            } catch (error) {
                console.error('Error fetching stocks:', error);
            }
        };

        fetchStocks();

        // Set up WebSocket connection
        const socket = new WebSocket('ws://' + window.location.host + '/ws/stocks/');

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            setStocks(prevStocks => {
                const updatedStocks = [...prevStocks];
                const index = updatedStocks.findIndex(stock => stock.symbol === data.symbol);
                if (index !== -1) {
                    updatedStocks[index] = data;
                }
                return updatedStocks;
            });
        };

        return () => {
            socket.close();
        };
    }, []);

    return (
        <div>
            <h2>Stock List</h2>
            <ul>
                {stocks.map(stock => (
                    <li key={stock.symbol}>
                        {stock.symbol} - {stock.name}: ${stock.latest_price}
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default StockList;