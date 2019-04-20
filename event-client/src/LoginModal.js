import React, { Component } from 'react';
import { Button, Modal, ModalHeader, ModalBody, ModalFooter } from 'reactstrap';
import './css/login.css';
class LoginModal extends Component {
  constructor(props) {
    super(props);
    this.state = {
      modal: false,
      username: '',
      password: ''
    };

    this.toggle = this.toggle.bind(this);
    this.onTextChange = this.onTextChange.bind(this);
    this.onLogin = this.onLogin.bind(this);
  }

  toggle() {
    this.setState(prevState => ({
      modal: !prevState.modal
    }));
  }
  onTextChange(e) {
    if (e.target.id == 'password') {
      this.setState({
        password: e.target.value
      });
    } else if (e.target.id == 'username') {
      this.setState({
        username: e.target.value
      });
    }
  }
  onLogin() {
    this.toggle();
  }

  render() {
    return (
      <div>
        <Button color="primary" onClick={this.toggle}>
          Login
        </Button>
        <Modal
          isOpen={this.state.modal}
          toggle={this.toggle}
          className={this.props.className}
        >
          <ModalHeader toggle={this.toggle}>Modal title</ModalHeader>
          <ModalBody>
            <div className="container login-container">
              <div className="row">
                <div className="col-md-12 login-form-1">
                  <h3>Login for Form 1</h3>
                  <form>
                    <div className="form-group">
                      <input
                        id="username"
                        type="text"
                        className="form-control"
                        placeholder="Your username *"
                        onChange={this.onTextChange}
                      />
                    </div>
                    <div className="form-group">
                      <input
                        id="password"
                        type="password"
                        class="form-control"
                        placeholder="Your Password *"
                        onChange={this.onTextChange}
                      />
                    </div>
                  </form>
                </div>
              </div>
            </div>
          </ModalBody>
          <ModalFooter>
            <Button color="primary" onClick={this.onLogin}>
              Login
            </Button>{' '}
            <Button color="secondary" onClick={this.toggle}>
              Cancel
            </Button>
          </ModalFooter>
        </Modal>
      </div>
    );
  }
}

export default LoginModal;
