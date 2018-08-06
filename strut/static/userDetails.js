import { Strut } from './utils.js';
import { Playlist, UserSidebar } from './components.js';

const { preact } = window;
const { Component, h, render } = preact;


class Dashboard extends Component {
  render() {
    const { user, memberships, songs } = this.props;

    return (
      h('div', {class: 'row main'},
        h('div', {class: 'column'},
          h(Playlist, {title: 'Their songs', owner: false, songs: songs}),
        ),
        h(UserSidebar, {user: user, me: false}),
      )
    )
  }
}

render(
  h(Dashboard, Strut.initialData),
  document.getElementById('app')
);
