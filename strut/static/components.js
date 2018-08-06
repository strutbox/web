import { media, api, chop } from './utils.js';

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
    const { id, title } = this.props;
    const { songs } = this.state;

    return (
      h('div', {},
        h('h6', {}, title),
        h('div', {class: 'song-list'},
          songs.map((song) => {
            return h(Song, song);
          }),
          h('button', {class: 'btn', onClick: this.onClick.bind(this)}, 'Add Song'),
        )
      )
    );
  }
}

export class TextInput extends Component {
  render() {
    return h('input', {
      value: this.state.value,
      class: 'Input',
      'type': 'text',
      ...this.props
    });
  }
}
