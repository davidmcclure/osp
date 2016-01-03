

import _ from 'lodash';
import React, { Component, PropTypes } from 'react';

import HitCount from './hit-count';
import Search from './search';
import TextList from './text-list';


export default class extends Component {


  /**
   * Render the ranking results.
   */
  render() {
    return (
      <div id="results">
        <HitCount />
        <Search />
        <TextList />
      </div>
    );
  }


}
