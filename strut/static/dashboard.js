import { media, api, getYoutubeID, chop } from './utils.js';
import {Song, MiniSong, Playlist, TextInput } from './components.js';

const { preact, Strut } = window;
const { Component, h, render } = preact;


class Jobs extends Component {
  constructor() {
    super();
    this.state = {
      jobs: [],
    };
  }

  componentWillMount() {
    this.reload();
    this.timer = setInterval(this.reload.bind(this), 5000);
    document.body.addEventListener('playlist-update', (e) => {
      this.reload();
    }, false);
  }

  componentWillUnmount() {
    clearInterval(this.timer);
  }

  reload() {
    api('songjob')
    .then(response => {
      if (response.status === 200) {
        this.setState({
          jobs: response.jobs,
        });
      } else {
        this.setState({
          jobs: [],
        })
      }
    });
  }

  render() {
    const { id } = this.props;
    const { jobs } = this.state;

    if (!jobs.length) return;

    return (
      h('div', {},
        h('h6', {}, 'Crunching...'),
        h('div', {class: 'song-list'},
          jobs.map((j) => {
            return h(MiniSong, j.song)
          })
        )
      )
    );
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

class Dashboard extends Component {
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
    document.body.dispatchEvent(new Event('playlist-update'));
  }

  render() {
    const { user, memberships, addingSong } = this.state;

    return (
      h('div', {class: 'row main'},
        h('div', {class: 'column'},
          h(Jobs, {}),
          h(Playlist, {id: 1, title: 'My Songs', onAddSong: this.onAddSong.bind(this)}),
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
  h(Dashboard, Strut.initialData),
  document.getElementById('app')
);
