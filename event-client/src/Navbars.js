import React, { Component } from 'react';
import {
  Collapse,
  Navbar,
  NavbarToggler,
  NavbarBrand,
  Nav,
  NavItem,
  NavLink,
  UncontrolledDropdown,
  DropdownToggle,
  DropdownMenu,
  DropdownItem,
  Button
} from 'reactstrap';
import LoginModal from './LoginModal.js';

export default class Navbars extends Component {
  constructor(props) {
    super(props);

    this.toggle = this.toggle.bind(this);
    this.login = this.login.bind(this);

    this.state = {
      isOpen: false,
      login: false,
      logged: false
    };
  }
  toggle() {
    this.setState({
      isOpen: !this.state.isOpen
    });
  }

  openLogin() {
    this.setState({
      login: !this.state.isOpen
    });
  }
  login() {
    this.setState({
      logged: true
    });
  }
  render() {
    console.log(localStorage.getItem('message'));

    console.log(localStorage.getItem('token'));
    return (
      <div>
        <Navbar color="light" light expand="md">
          <NavbarBrand href="/">Event</NavbarBrand>
          <Nav className="ml-auto" navbar>
            <NavItem>
              <NavLink href="/api/events/">Events</NavLink>
            </NavItem>
            {this.state.logged || localStorage.getItem('token') !== null ? (
              <div>
                <h3>{localStorage.getItem('message')}</h3>
                <button
                  onClick={() => {
                    localStorage.removeItem('token');
                    this.setState({
                      logged: false
                    });
                  }}
                >
                  Logout
                </button>
              </div>
            ) : (
              <LoginModal login={this.login} />
            )}
          </Nav>
        </Navbar>
      </div>
    );
  }
}
