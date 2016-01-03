

import React, { Component, PropTypes } from 'react';


export default class extends Component {


  static propTypes = {
    hit: PropTypes.object.isRequired,
    rank: PropTypes.number.isRequired,
  }


  /**
   * Render a text row.
   */
  render() {
    return (
      <tr>

        <td>{this.props.rank}</td>

        <td>{this.props.hit.sort[0]}</td>

        <td>{this.props.hit._source.title}</td>

      </tr>
    );
  }


}
