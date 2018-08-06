import { Strut, chop } from './utils.js';

const { preact } = window;
const { Component, h, render } = preact;

class User extends Component {
  render() {
    const { email } = this.props;

    return (
      h('a', {href: `/users/${email}/`},
      h('div', {class: 'song'},
        h('div', {class: 'song-desc'},
          h('h6', {}, chop(this.props.email, 35)),
        )
      )
    ));
  }
}

class MemberList extends Component {
  render() {
    const { members } = this.props;

    if (!members.length) return (
      h('div', {},
        h('h6', {}, 'Get some friends')
      )
    );

    return (
      h('div', {},
        h('div', {class: 'song-list'},
          members.map((user) => {
            return h(User, user);
          }),
        )
      )
    );
  }
}

render(
  h(MemberList, Strut.initialData),
  document.getElementById('app')
);
