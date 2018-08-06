window.Strut = {
  settings: JSON.parse(document.getElementById('strut-settings-data').textContent),
  initialData: JSON.parse(document.getElementById('strut-initial-data').textContent),
};

const { Strut } = window;

export const media = (src) => { return Strut.settings.static + src };

const getCookie = (name) => {
  if (document.cookie && document.cookie != '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) == (name + '=')) {
        return decodeURIComponent(cookie.substring(name.length + 1));
      }
    }
  }
  return null;
};

export const api = (endpoint, options = {}) => {
  const { query } = options;
  delete options.query;

  let qs = '';
  if (query !== undefined) {
    qs = '?' + Object.keys(query).map(
      k => encodeURIComponent(k) + '=' + encodeURIComponent(query[k])
    ).join('&');
  }

  const headers = new Headers();
  if (!/^GET|HEAD|OPTIONS|TRACE$/i.test(options.method || 'GET')) {
    headers.append('X-CSRFToken', getCookie('csrftoken'));
  }

  return fetch(`/api/0/${endpoint}/${qs}`, {
    credentials: 'same-origin',
    headers: headers,
    ...options,
  }).then(res => res.json());
};

export const chop = (input, length) => {
  if (input.length < length) return input;
  return input.substring(0, length-1) + '…';
};

// Adapted from https://gist.github.com/takien/4077195
export const getYoutubeID = (url) => {
  if (!url) return '';
  if (url.length == 11) return url;
  url = url.split(/(vi\/|v=|\/v\/|youtu\.be\/|\/embed\/)/);
  if (url[2] !== undefined) {
    url = url[2].split(/[^0-9a-z_\-]/i);
  }
  return url[0];
};
