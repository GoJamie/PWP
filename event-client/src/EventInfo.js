import React, { Component } from 'react';

import {
  Card,
  CardImg,
  CardText,
  CardBody,
  CardTitle,
  CardSubtitle,
  Button
} from 'reactstrap';
import { ListGroup, ListGroupItem } from 'reactstrap';

export default class EventInfo extends Component {
  constructor(props) {
    super(props);

    this.state = {
      event: {}
    };
  }

  componentDidMount() {
    const {
      match: { url }
    } = this.props;
    console.log(url);

    const request = async () => {
      const response2 = await fetch('http://localhost:5000' + url, {
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
        event: data
      });
    });
  }
  render() {
    console.log(this.state);
    let listgroup;
    console.log(localStorage.getItem('token'));

    if (this.state.event.name !== undefined) {
      listgroup = (
        <Card>
          <CardBody>
            <CardTitle>{this.state.event.name}</CardTitle>
            <CardSubtitle>Place: {this.state.event.place}</CardSubtitle>
            <CardText>{this.state.event.description}</CardText>
            {localStorage.getItem('token') !== null ? (
              <Button style={{ marginRight: '20px' }} color="danger">
                Delete Event
              </Button>
            ) : (
              undefined
            )}

            <Button color="success">join Event</Button>
          </CardBody>
        </Card>
      );
    }

    return <div>{listgroup}</div>;
  }
}
