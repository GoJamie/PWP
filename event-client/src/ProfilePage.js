import React, { Component } from 'react';

import { Button, Form, FormGroup, Label, Input, FormText } from 'reactstrap';
export default class EventInfo extends Component {
  constructor(props) {
    super(props);

    this.state = {
      user: {},
      location: '',
      name: ''
    };
    this.onTextChange = this.onTextChange.bind(this);
    this.updateUser = this.updateUser.bind(this);
    this.deleteUser = this.deleteUser.bind(this);
  }

  componentDidMount() {
    const {
      match: { url }
    } = this.props;
    console.log(url);

    const request = async () => {
      const response2 = await fetch('http://localhost:5000' + url + '/', {
        method: 'GET',
        mode: 'cors',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      const json2 = await response2.json();
      return json2;
    };

    request().then(data => {
      console.log(data);
      this.setState({
        user: data,
        location: data.location,
        name: data.name
      });
    });
  }
  updateUser() {
    console.log(this.state.location);

    let update = {
      id: parseInt(localStorage.getItem('userId')),
      name: this.state.name,
      location: this.state.location
    };
    console.log(this.state.user['@controls'].edit.href);

    fetch('http://localhost:5000' + this.state.user['@controls'].edit.href, {
      method: 'PUT',
      mode: 'cors',
      body: JSON.stringify(update),
      headers: {
        'Content-Type': 'application/json'
      }
    });
  }
  deleteUser() {
    fetch(
      'http://localhost:5000' +
        this.state.user['@controls']['eventhub:delete'].href,
      {
        method: 'DELETE',
        mode: 'cors',
        headers: {
          'Content-Type': 'application/json'
        }
      }
    );
    document.location.href = '#';
  }
  onTextChange(e) {
    if (e.target.id == 'locationId') {
      console.log(e.target.value);

      this.setState({
        location: e.target.value
      });
    } else if (e.target.id == 'nameId') {
      this.setState({
        name: e.target.value
      });
    }
  }
  render() {
    return (
      <Form>
        <FormGroup>
          <Label for="exampleEmail">Location</Label>
          <Input
            type="email"
            name="email"
            id="locationId"
            value={this.state.location}
            onChange={this.onTextChange}
          />
        </FormGroup>

        <FormGroup>
          <Label for="exampleEmail">Name</Label>
          <Input
            type="email"
            name="name"
            id="nameId"
            value={this.state.name}
            onChange={this.onTextChange}
          />
        </FormGroup>

        <Button color="primary" onClick={this.updateUser}>
          Update user
        </Button>

        <Button
          onClick={this.deleteUser}
          color="danger"
          style={{ marginLeft: '200px' }}
        >
          Delete User
        </Button>
      </Form>
    );
  }
}
