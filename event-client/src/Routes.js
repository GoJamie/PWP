import React from 'react';
import { Switch, Route } from 'react-router-dom';
import EventList from './EventList';

import EventInfo from './EventInfo';

// The Main component renders one of the three provided
// Routes (provided that one matches). Both the /roster
// and /schedule routes will match any pathname that starts
// with /roster or /schedule. The / route will only match
// when the pathname is exactly the string "/"
const Routes = () => (
  <main className="content-container">
    <Switch>
      <Route exact path="/api/events/" component={EventList} />
      <Route exact path="/api/events/:eventid" component={EventInfo} />
    </Switch>
  </main>
);

export default Routes;
