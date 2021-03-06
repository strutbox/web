const { preact } = window;
const { Component, h, render } = preact;

class App extends Component {
  constructor() {
    super();
    this.UUID = '6efa9836-b179-4387-b21a-1b7dffacfae0';
    this.state = {
      connected: false,
    };
  }

  onConnect(service) {
    this.setState({
      connected: true,
      service: service,
    });
  }

  render() {
    const { connected, service } = this.state;
    if (!connected)
      return h(Discover, {
        onConnect: this.onConnect.bind(this),
        serviceUUID: this.UUID,
      });

    return h(Device, {service: service});
  }
}

class Discover extends Component {
  onConnect(e) {
    this.setState({connecting: true});

    const { serviceUUID, onConnect } = this.props;

    navigator.bluetooth.requestDevice({
      filters: [{services: [serviceUUID]}]
    })
    .then(device => {
      device.gatt.connect()
      .then(server => {
        server.getPrimaryService(serviceUUID).then(onConnect);
      })
      .catch(e => {
        alert(e);
        this.setState({
          connecting: false,
        });
      })
    })
    .catch(e => {
      this.setState({
        connecting: false,
      });
    });

  }

  render() {
    if (this.state.connecting)
      return h('div', {}, 'connecting...');

    return (
      h('button', {onClick: this.onConnect.bind(this)}, 'Discover')
    )
  }
}

class Device extends Component {
  render() {
    const { service } = this.props;
    return (
      h('div', {},
        h('h1', {}, `Connected to ${service.device.name}`),
        h(IP, {service: service}),
        h(SSID, {service: service}),
      )
    )
  }
}

class SSID extends Component {
  constructor() {
    super();
    this.UUID = '6efa9836-b179-4387-b21a-1b7dffacfae1';
    this.state = {ssids: [], selected: -1};
  }

  componentWillMount() {
    this.fetch();
  }

  fetch() {
    this.props.service.getCharacteristic(this.UUID)
    .then(characteristic => characteristic.startNotifications())
    .then(characteristic => {
      characteristic.addEventListener(
        'characteristicvaluechanged', e => {
          let ssid = JSON.parse(new TextDecoder('utf-8').decode(e.target.value));
          this.setState({
            ssids: [...this.state.ssids, ssid],
          });
      });
    });
  }

  connect(ssid, password) {
    this.props.service.getCharacteristic(this.UUID)
    .then(characteristic => characteristic.writeValue(new TextEncoder('utf-8').encode(JSON.stringify({'s': ssid.s, 'p': password}))));
  }

  onSSIDChange(e) {
    this.setState({selected: parseInt(e.target.value, 10)});
  }

  onConnect(e) {
    e.preventDefault();
    const { selected, ssids } = this.state;
    const passwd = document.getElementById('password');
    this.connect(ssids[selected], passwd.value);
  }

  render() {
    const { selected, ssids } = this.state;
    let encrypted = false;
    if (selected > -1) {
      encrypted = ssids[selected].e;
    }
    return h('div', {}, [
      h('form', {},
        h('div', {},
          h('label', {'for': 'ssid'}, 'SSID'),
          h('select', {id: 'ssid', onChange: this.onSSIDChange.bind(this)},
            h('option', {value: -1}, '--'),
            ssids.map((ssid, idx) =>
              h('option', {value: idx, selected: idx == selected}, ssid.s)
            )
          ),
        ),
        encrypted && (
          h('div', {},
            h('label', {'for': 'password'}, 'Password'),
            h('input', {id: 'password', type: 'password'})
          )
        ),
        selected > -1 && (
          h('div', {},
            h('button', {onClick: this.onConnect.bind(this)}, 'Connect'),
          )
        )
      )
    ]);
  }
}

class IP extends Component {
  constructor() {
    super();
    this.UUID = '6efa9836-b179-4387-b21a-1b7dffacfae2';
  }

  componentWillMount() {
    this.fetch();
  }

  fetch() {
    this.props.service.getCharacteristic(this.UUID)
    .then(characteristic => characteristic.readValue())
    .then(value => {
      this.setState({
        value: JSON.parse(new TextDecoder('utf-8').decode(value))
      });
    });
  }

  render() {
    const { service } = this.props;
    const { value } = this.state;
    const online = !!(value || {}).ip;

    if (online)
      return h('div', {}, `IP Address: ${value.ip}`);

    return h('div', {}, 'Offline');
  }
}

render(h(App), document.body);
