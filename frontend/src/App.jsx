import React, { useEffect, useState } from 'react';

const App = () => {
    const [stockData, setStockData] = useState([]);

    useEffect(() => {
        const ws = new WebSocket('ws://localhost:8000/ws/realtime/');

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            setStockData((prevData) => [...prevData, data]);
        };

        return () => {
            ws.close();
        };
    }, []);

    return (
        <div>
            <h1>Welcome to the Stock Analysis Platform</h1>
            <ul>
                {stockData.map((stock, index) => (
                    <li key={index}>
                        {stock.symbol} - {stock.latest_price}
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default App;
