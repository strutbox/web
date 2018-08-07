import { Strut, media, api, getYoutubeID, chop } from './utils.js';
import { Song, MiniSong, Playlist, TextInput, UserSidebar } from './components.js';

const { preact } = window;
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
    const value = e.target.value;

    if ( value === '' ) {
      this.setState({
        start: undefined,
      });
      return;
    }

    const { length } = this.state;
    const start = parseInt(value, 10);

    const error = this.validateTimes({ start, length });
    this.setState({ start, error });
  }

  setLength(e) {
    const value = e.target.value;

    if ( value === '' ) {
      this.setState({
        length: undefined,
      });
      return;
    }

    const { start } = this.state;
    const length = parseInt(value, 10);

    const error = this.validateTimes({ start, length });
    this.setState({ length, error });
  }

  validateTimes(input, all = false) {
    const { start, length } = input;
    const { songmeta } = this.state;
    if ( all || (start !== undefined && length !== undefined) ) {
      if ( all ) {
        if ( start === undefined ) {
          return 'Start is empty.';
        }
        if ( length === undefined ) {
          return 'Length is empty.';
        }
      }
      if ( start + length > songmeta.duration ) {
        return `Song is only ${songmeta.duration}s long dummy.`;
      }
      if ( start < 0 ) {
        return 'Start must be positive.';
      }
      if ( length < 1 ) {
        return 'Not long enough';
      }
      if ( length > 30 ) {
        return 'Too long, must be less than 30s';
      }
    }
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
    const error = this.validateTimes(this.state, true);
    if ( error ) {
      this.setState({ error });
      return;
    }

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
      me: this.props.me,
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
    const { me, memberships, addingSong } = this.state;

    return (
      h('div', {class: 'row main'},
        h('div', {class: 'column'},
          h(Jobs, {}),
          h(Playlist, {title: 'My Songs', owner: true, onAddSong: this.onAddSong.bind(this)}),
        ),
        h(UserSidebar, {user: me, memberships: memberships, me: true}),
        ( addingSong && h(AddSongModal, {onFinish: this.onAddSongFinish.bind(this)}) ),
      )
    )
  }
}

render(
  h(Dashboard, Strut.initialData),
  document.getElementById('app')
);
