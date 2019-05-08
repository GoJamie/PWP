import React, { Component } from 'react';

import { ListGroup, ListGroupItem } from 'reactstrap';
import AddEvent from './AddEvent';

export default class EventList extends Component {
  constructor(props) {
    super(props);

    this.state = {
      events: [],
      update: false
    };

    this.update = this.update.bind(this);
  }

  componentDidMount() {
    const request = async () => {
      const response2 = await fetch('http://localhost:5000/api/events/', {
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
      this.setState({
        events: data.items
      });
    });
  }
  update() {
    this.setState(prevState => ({
      update: !prevState.update
    }));
  }
  render() {
    let listgroup = [];
    if (this.state.events.length > 0) {
      this.state.events.forEach(event => {
        listgroup.push(
          <ListGroupItem tag="a" href={event['@controls'].self.href}>
            {event.name}
          </ListGroupItem>
        );
      });
    }

    return (
      <div>
        {localStorage.getItem('token') !== null ? (
          <ListGroup>{listgroup}</ListGroup>
        ) : (
          undefined
        )}
        <AddEvent update={this.update} />
      </div>
    );
  }
}
