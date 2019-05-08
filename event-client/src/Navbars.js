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
    let profilelink = '';
    if (localStorage.getItem('userId') !== null) {
      profilelink = '/api/users/' + localStorage.getItem('userId');
    }

    return (
      <div>
        <Navbar color="light" light expand="md">
          <NavbarBrand href="/">Event</NavbarBrand>
          <Nav className="ml-auto" navbar>
            <NavItem>
              <NavLink href="/api/events/">Events</NavLink>
            </NavItem>
            {this.state.logged || localStorage.getItem('userId') !== null ? (
              <NavItem>
                <NavLink href={profilelink}>Profile Page</NavLink>
              </NavItem>
            ) : (
              undefined
            )}

            {this.state.logged || localStorage.getItem('token') !== null ? (
              <div>
                <h3>{localStorage.getItem('message')}</h3>
                <button
                  onClick={() => {
                    localStorage.removeItem('token');
                    localStorage.removeItem('userId');
                    localStorage.removeItem('message');

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
