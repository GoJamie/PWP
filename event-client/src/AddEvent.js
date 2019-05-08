import React, { Component } from 'react';
import { Button, Modal, ModalHeader, ModalBody, ModalFooter } from 'reactstrap';

class AddEvent extends Component {
  constructor(props) {
    super(props);
    this.state = {
      modal: false,
      name: '',
      description: '',
      location: ''
    };

    this.toggle = this.toggle.bind(this);
    this.onTextChange = this.onTextChange.bind(this);
    this.onAdd = this.onAdd.bind(this);
  }

  toggle() {
    this.setState(prevState => ({
      modal: !prevState.modal
    }));
  }
  onTextChange(e) {
    if (e.target.id == 'eventname') {
      this.setState({
        name: e.target.value
      });
    } else if (e.target.id == 'eventlocation') {
      this.setState({
        location: e.target.value
      });
    } else if (e.target.id == 'eventdescription') {
      this.setState({
        description: e.target.value
      });
    }
  }
  onAdd() {
    const log = {
      place: this.state.location,
      description: this.state.description,
      name: this.state.name,
      creatorId: parseInt(localStorage.getItem('userId'))
    };
    console.log(JSON.stringify(log));
    const request = async () => {
      const response2 = await fetch('http://localhost:5000/api/events/', {
        method: 'POST',
        mode: 'cors',
        body: JSON.stringify(log), // data can be `string` or {object}!
        headers: {
          'Content-Type': 'application/json'
        }
      });

      const json2 = await response2.json();
      return json2;
    };
    request().then(data => {
      console.log(data);
      localStorage.setItem('token', data.access_token);

      localStorage.setItem('message', data.message);

      localStorage.setItem('userId', data.user_id);
      this.props.update();
    });
    this.toggle();
  }

  render() {
    return (
      <div>
        <Button color="primary" onClick={this.toggle}>
          Add new Event
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
                  <h3>Adding event</h3>
                  <form>
                    <div className="form-group">
                      <input
                        id="eventname"
                        type="text"
                        className="form-control"
                        placeholder="Your event name *"
                        onChange={this.onTextChange}
                      />
                    </div>
                    <div className="form-group">
                      <input
                        id="eventlocation"
                        type="text"
                        className="form-control"
                        placeholder="Your event location *"
                        onChange={this.onTextChange}
                      />
                    </div>
                    <div className="form-group">
                      <input
                        id="eventdescription"
                        type="text"
                        className="form-control"
                        placeholder="Your event description *"
                        onChange={this.onTextChange}
                      />
                    </div>
                  </form>
                </div>
              </div>
            </div>
          </ModalBody>
          <ModalFooter>
            <Button color="primary" onClick={this.onAdd}>
              Add
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

export default AddEvent;
