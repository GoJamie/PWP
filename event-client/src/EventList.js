import React, { Component } from 'react';

import { ListGroup, ListGroupItem } from 'reactstrap';

export default class EventList extends Component {
  constructor(props) {
    super(props);

    this.state = {
      events: []
    };
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
      console.log(data);
      this.setState({
        events: data.items
      });
    });
  }
  render() {
    console.log(this.state);
    let listgroup = [];
    if (this.state.events.length > 0) {
      this.state.events.forEach(event => {
        console.log(event['@controls'].self.href);

        listgroup.push(
          <ListGroupItem tag="a" href={event['@controls'].self.href}>
            {event.name}
          </ListGroupItem>
        );
      });
    }

    return <ListGroup>{listgroup}</ListGroup>;
  }
}
