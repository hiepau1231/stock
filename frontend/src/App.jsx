import React, { useEffect, useState } from 'react';
import './styles.css';

function App() {
    const [stocks, setStocks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        // Fetch mock data from the backend
        fetch('/api/stock_analysis/mock_stock_data/')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                setStocks(data.stocks);
                setLoading(false);
            })
            .catch(error => {
                setError(error);
                setLoading(false);
            });
    }, []);

    if (loading) {
        return <div className="App">Loading...</div>;
    }

    if (error) {
        return <div className="App">Error: {error.message}</div>;
    }

    return (
        <div className="App">
            <h1>Mock Stock Data</h1>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Symbol</th>
                        <th>Name</th>
                        <th>Latest Price</th>
                        <th>Last Updated</th>
                    </tr>
                </thead>
                <tbody>
                    {stocks.map(stock => (
                        <tr key={stock.id}>
                            <td>{stock.id}</td>
                            <td>{stock.symbol}</td>
                            <td>{stock.name}</td>
                            <td>${stock.latest_price.toFixed(2)}</td>
                            <td>{new Date(stock.last_updated).toLocaleString()}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

export default App;
