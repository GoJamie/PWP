import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';
import Navbars from './Navbars.js';
import Routes from './Routes.js';
class App extends Component {
  render() {
    return (
      <div className="App">
        <Navbars />
        <Routes />
      </div>
    );
  }
}

export default App;
