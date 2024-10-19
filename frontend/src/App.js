import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import StockList from './components/StockList';

const App = () => {
    return (
        <Router>
            <div>
                <nav>
                    <ul>
                        <li>
                            <Link to="/">Home</Link>
                        </li>
                    </ul>
                </nav>

                <Switch>
                    <Route path="/" exact>
                        <StockList />
                    </Route>
                </Switch>
            </div>
        </Router>
    );
};

export default App;