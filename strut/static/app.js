import { media, api, getYoutubeID, chop } from './utils.js';

const { preact, Strut } = window;
const { Component, h, render } = preact;


class Song extends Component {
  onDelete(e) {
    e.preventDefault();
    const { id } = this.props;
    alert(`Deleting: ${id}`);
  }

  render() {
    const { start, length, meta, file } = this.props;

    return (
      h('div', {class: 'song'},
        h('a', {onClick: this.onDelete.bind(this), href: '#', class: 'delete'},
          h('img', {src: media('trash.svg')}),
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

class Playlist extends Component {
  onClick(e) {
    e.preventDefault();
    this.props.onAddSong();
  }

  render() {
    const { id, songs } = this.props;

    return (
      h('div', {class: 'song-list'},
        songs.map((song) => {
          return h(Song, song);
        }),
        h('button', {class: 'btn', onClick: this.onClick.bind(this)}, 'Add Song'),
      )
    );
  }
}

class TextInput extends Component {
  render() {
    return h('input', {
      value: this.state.value,
      class: 'Input',
      'type': 'text',
      ...this.props
    });
  }
}

class AddSongModal extends Component {
  constructor() {
    super();
    this.state = {
      source: 0,
      step: 0,
      isLoading: false,
    };
  }

  setYoutubeURL(e) {
    this.setState({
      source: 0,
      youtubeURL: e.target.value,
    });
  }

  setStart(e) {
    this.setState({
      start: parseInt(e.target.value, 10),
    });
  }

  setLength(e) {
    this.setState({
      length: parseInt(e.target.value, 10),
    });

    this.validateTimes();
  }

  validateTimes() {
    const { start, length, songmeta } = this.state;
    if ( start !== undefined && length !== undefined ) {
      if ( start + length > songmeta.duration ) {
        this.setState({ error: `Song is only ${songmeta.duration}s long dummy.` });
        return;
      }
      if ( length < 1 ) {
        this.setState({ error: 'Not long enough' });
        return
      }
      if ( length > 20 ) {
        this.setState({ error: 'Too long' });
      }
    }
    this.setState({ error: null });
  }

  lookupMeta() {
    this.setState({ isLoading: true });
    const { source, youtubeURL } = this.state;
    const identifier = getYoutubeID(youtubeURL);

    api('songmeta', {
      query: {
        source: source,
        identifier: identifier,
      }
    })
    .then(response => {
      if (response.status === 200) {
        this.setState({
          isLoading: false,
          songmeta: response.songmeta,
          error: null,
          step: 1,
        });
      } else {
        this.setState({
          isLoading: false,
          step: 0,
          error: response.error,
        })
      }
    });
  }

  createSong() {
    this.setState({ isLoading: true });

    const form = new FormData();
    form.append('source', this.state.songmeta.source);
    form.append('identifier', this.state.songmeta.identifier);
    form.append('start', this.state.start);
    form.append('length', this.state.length);

    api('song', {
      method: 'POST',
      body: form,
    }).then(response => {
      this.setState({
        isLoading: false,
      })
      this.props.onFinish(response);
    })
  }

  renderLoading() {
    return (
      h('div', {},
        h('div', {class: 'modal-body'},
          h('div', {class: 'row field'},
            h('h4', {}, 'Loading...')
          ),
        ),
      )
    )
  }

  renderStep() {
    switch (this.state.step) {
      case 0:
        return this.renderURLForm();
      case 1:
        return this.renderSegmentForm();
    }
  }

  renderSegmentForm() {
    const { songmeta, error } = this.state;

    return (
      h('div', {},
        h('div', {class: 'modal-body'},
          ( error ? h('h3', {}, error) : null ),
          h('div', {class: 'row field'},
            h('div', {class: 'song-thumb'},
              h('img', {src: songmeta.thumbnail}),
            ),
            h('div', {class: 'song-desc'},
              h('h6', {title: songmeta.title}, chop(songmeta.title, 35)),
            )
          ),
          h('div', {class: 'row field'},
            h('div', {class: 'column'}, 'Start time', h('em', {}, 'in seconds')),
            h('div', {class: 'column'},
              h(TextInput, {
                value: this.state.start,
                onChange: this.setStart.bind(this),
                type: 'number',
                placeholder: 128,
              })
            )
          ),
          h('div', {class: 'row field'},
            h('div', {class: 'column'}, 'Play duration', h('em', {}, 'in seconds')),
            h('div', {class: 'column'},
              h(TextInput, {
                value: this.state.length,
                onChange: this.setLength.bind(this),
                type: 'number',
                placeholder: 6,
              })
            )
          )
        ),
        h('div', {class: 'modal-footer'},
          h('button', {class: 'btn pull-right', onClick: this.createSong.bind(this)}, 'Load it up')
        )
      )
    );
  }

  renderURLForm() {
    const { error } = this.state;

    return (
      h('div', {},
        h('div', {class: 'modal-body'},
          ( error ? h('h3', {}, error) : null ),
          h('div', {class: 'row field'},
            h('div', {class: 'column'}, 'YouTube URL:'),
            h('div', {class: 'column'},
              h(TextInput, {
                value: this.state.youtubeURL,
                onChange: this.setYoutubeURL.bind(this),
                placeholder: 'https://www.youtube.com/watch?v=6YMPAH67f4o',
              }),
            ),
          )
        ),
        h('div', {class: 'modal-footer'},
          h('button', {class: 'btn pull-right', onClick: this.lookupMeta.bind(this)}, 'Lookup')
        )
      )
    );
  }

  render() {
    const { isLoading } = this.state;
    return (
      h('div', {class: 'modal-wrapper'},
        h('div', {class: 'modal'},
          h('div', {class: 'modal-header'},
            h('h3', {}, 'Add Song'),
          ),
          ( isLoading ? this.renderLoading() : this.renderStep() )
        )
      )
    )
  }
}

class App extends Component {
  componentWillMount() {
    this.setState({
      user: this.props.user,
      songs: this.props.songs,
      memberships: this.props.memberships,
      addingSong: false,
    })
  }

  onAddSong() {
    this.setState({ addingSong: true });
  }

  onAddSongFinish() {
    this.setState({ addingSong: false });
  }

  render() {
    const { user, songs, memberships, addingSong } = this.state;

    return (
      h('div', {class: 'row main'},
        h('div', {class: 'column'},
          h('h6', {}, 'My Songs'),
          h(Playlist, {id: 1, songs: songs, onAddSong: this.onAddSong.bind(this)}),
        ),
        h('div', {class: 'column'},
          h('div', {class: 'field'},
            h('label', {}, 'Email'),
            h(TextInput, {
              readonly: true,
              value: user.email
            })
          ),
          h('div', {class: 'field'},
            h('label', {}, 'Memberships'),
            h('ul', {},
              memberships.map((m) => {
                return h('li', {}, m.organization.slug);
              })
            )
          )
        ),
        ( addingSong && h(AddSongModal, {onFinish: this.onAddSongFinish.bind(this)}) ),
      )
    )
  }
}

render(
  h(App, Strut.initialData),
  document.getElementById('app')
);
