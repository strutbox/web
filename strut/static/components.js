import { Strut, media, api, chop } from './utils.js';

const { preact } = window;
const { Component, h, render } = preact;

export class Song extends Component {
  onDelete(e) {
    e.preventDefault();
    if (!confirm('Are you sure you want to delete this song?')) return;
    const { id } = this.props;
    api(`song/${id}`, {
      method: 'DELETE',
    })
    .then(response => {
      document.body.dispatchEvent(new Event('playlist-update'));
    });
  }

  render() {
    const { start, length, meta, file, editable } = this.props;

    return (
      h('div', {class: 'song'},
        (editable &&
          h('a', {onClick: this.onDelete.bind(this), href: '#', class: 'delete'},
            h('img', {src: media('trash.svg')}),
          )
        ),
        h('div', {class: 'song-thumb'},
          h('img', {src: meta.thumbnail}),
        ),
        h('div', {class: 'song-desc'},
          h('h6', {title: meta.title}, chop(meta.title, 35)),
          h('div', {}, `Starts at ${start}s & plays for ${length}s`),
          h('audio', {controls: 'controls'},
            h('source', {src: file, type: 'audio/mpeg'})
          )
        )
      )
    );
  }
}

export class MiniSong extends Component {
  render() {
    const { start, length, meta, file } = this.props;

    return (
      h('div', {class: 'song'},
        h('div', {class: 'song-thumb'},
          h('img', {src: meta.thumbnail}),
        ),
        h('div', {class: 'song-desc'},
          h('h6', {title: meta.title}, chop(meta.title, 35)),
          h('div', {}, `Starts at ${start}s & plays for ${length}s`),
        )
      )
    );
  }
}

export class Playlist extends Component {
  constructor() {
    super();
    this.state = {
      isLoading: true,
      songs: [],
    };
  }

  componentWillMount() {
    const { owner } = this.props;
    this.reload();
    if (!owner) return;

    this.timer = setInterval(this.reload.bind(this), 5000);
    document.body.addEventListener('playlist-update', (e) => {
      this.reload();
    }, false);
  }

  componentWillUnmount() {
    if (this.timer) clearInterval(this.timer);
  }

  reload() {
    const { songs, owner } = this.props;

    if (!owner) {
      this.setState({
        isLoading: false,
        songs: songs,
      });
      return;
    }

    api('song')
    .then(response => {
      if (response.status === 200) {
        this.setState({
          isLoading: false,
          songs: response.songs,
        });
      } else {
        this.setState({
          isLoading: false,
        })
      }
    });
  }

  onClick(e) {
    e.preventDefault();
    this.props.onAddSong();
  }

  render() {
    const { title, owner } = this.props;
    const { songs } = this.state;

    return (
      h('div', {},
        h('h6', {}, title),
        h('div', {class: 'song-list'},
          (songs || []).map((song) => {
            return h(Song, {...song, ...{editable: !!owner}});
          }),
          (owner &&
            h('button', {class: 'btn', onClick: this.onClick.bind(this)}, 'Add Song')
          ),
        )
      )
    );
  }
}

export class TextInput extends Component {
  render() {
    return h('input', {
      class: 'Input',
      type: 'text',
      ...this.props
    });
  }
}

class Checkbox extends Component {
  render() {
    return (
      h('div', {},
        h('label', {class: 'switch'},
          h('input', {
            type: 'checkbox',
            ...this.props
          }),
          h('span', {'class': 'slider'}),
          h('div', {}, this.props.label),
        ),
      )
    )
  }
}

class UserSettings extends Component {
  onPrivacyChange(e) {

    api('user/settings', {
      method: 'POST',
      form: {
        privacy_public: e.target.checked,
      }
    });
  }

  render() {
    const { settings } = this.props;
    return (
      h('div', {class: 'field'},
        h('h6', {}, 'Settings'),
        h(Checkbox, {
          label: 'Share Publicly',
          checked: settings.privacy_public,
          onChange: this.onPrivacyChange.bind(this),
        }),
      )
    )
  }
}

export class UserSidebar extends Component {
  render() {
    const { user, memberships, me } = this.props;

    return (
      h('div', {class: 'column'},
        h('div', {class: 'field'},
          h('label', {}, 'Email'),
          h(TextInput, {
            readonly: true,
            value: user.email,
          })
        ),
        (me ?
          h('div', {class: 'field'},
            h('h6', {}, 'Memberships'),
            h('ul', {},
              memberships.map((m) => {
                return h('li', {}, (
                  h('a', {'href': `/organization/${m.organization.slug}/members/`}, m.organization.name)
                ));
              })
            )
          )
          : Strut.settings.is_authenticated &&
          h('div', {class: 'field'},
            h('form', {method: 'get', action: '/dashboard/'},
              h('button', {class: 'btn', }, 'Back to dashboard')
            )
          )
        ),
        (me && h(UserSettings, user)),
      )
    )
  }
}
