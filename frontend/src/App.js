import Avatar from '@material-ui/core/Avatar';
import Button from '@material-ui/core/Button';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import Checkbox from '@material-ui/core/Checkbox';
import CircularProgress from '@material-ui/core/CircularProgress';
import blue from '@material-ui/core/colors/blue';
import CssBaseline from '@material-ui/core/CssBaseline';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogTitle from '@material-ui/core/DialogTitle';
import Divider from '@material-ui/core/Divider';
import ExpansionPanel from '@material-ui/core/ExpansionPanel';
import ExpansionPanelActions from '@material-ui/core/ExpansionPanelActions';
import ExpansionPanelDetails from '@material-ui/core/ExpansionPanelDetails';
import ExpansionPanelSummary from '@material-ui/core/ExpansionPanelSummary';
import FormControl from '@material-ui/core/FormControl';
import Grid from '@material-ui/core/Grid';
import IconButton from '@material-ui/core/IconButton';
import InputLabel from '@material-ui/core/InputLabel';
import ListItemText from '@material-ui/core/ListItemText';
import MenuItem from '@material-ui/core/MenuItem';
import Select from '@material-ui/core/Select';
import Snackbar from '@material-ui/core/Snackbar';
import {createMuiTheme, MuiThemeProvider} from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import {default as AddCircleOutlineIcon} from '@material-ui/icons/AddCircleOutline';
import {default as ChevronLeftIcon} from '@material-ui/icons/ChevronLeft';
import {default as ChevronRightIcon} from '@material-ui/icons/ChevronRight';
import {default as CloseIcon} from '@material-ui/icons/Close';
import {default as ExpandMoreIcon} from '@material-ui/icons/ExpandMore';
import {default as InfoIcon} from '@material-ui/icons/Info';
import {default as InfoOutlinedIcon} from '@material-ui/icons/InfoOutlined';
import {default as MenuIcon} from '@material-ui/icons/Menu';
import {default as RemoveIcon} from '@material-ui/icons/Remove';
import PropTypes from 'prop-types';
import React, {Component} from 'react';
import {GoogleMap, Polygon, withGoogleMap, withScriptjs} from 'react-google-maps';
import {compose, withProps} from 'recompose';
import 'typeface-roboto';
import './style.css';

const BACKEND_HOST = 'http://115.146.92.26';

const theme = createMuiTheme({
  palette: {
    primary: blue,
  },
  typography: {
    useNextVariants: true,
  },
});

function debounce(fn, delay = 1000) {
  let timer = null;
  return function() {
    let context = this;
    let args = arguments;
    clearTimeout(timer);
    timer = setTimeout(function() {
      fn.apply(context, args);
    }, delay);
  };
}

function capitalize(s) {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

function City(name, lng, lat, color) {
  this.name = name;
  this.lng = lng;
  this.lat = lat;
  this.color = color;
}

function scaleRatio(value, n) {
  let offset = (1 - (1.0 / n)) / 2;
  value = value - offset;
  value = value * n;
  if (value < 0) {
    value = 0;
  } else if (value > 1) {
    value = 1;
  }
  return value;
}

function redGreedColor(value) {
  return `hsl(${Math.round((value) * 120)},80%,50%)`;
}

const years = [2014, 2015, 2016, 2017, 2018];

const weekdays = [
  {key: 0, name: 'Sunday', short: 'Sun'},
  {key: 1, name: 'Monday', short: 'Mon'},
  {key: 2, name: 'Tuesday', short: 'Tue'},
  {key: 3, name: 'Wednesday', short: 'Wed'},
  {key: 4, name: 'Thursday', short: 'Thu'},
  {key: 5, name: 'Friday', short: 'Fri'},
  {key: 6, name: 'Saturday', short: 'Sat'},
];

const cities = [
  new City('melbourne', 144.962, -37.816, '#3f51b5'),
  new City('sydney', 151.208, -33.868, '#ff9800'),
  new City('brisbane', 153.025, -27.469, '#8bc34a'),
  new City('canberra', 149.125, -35.310, '#673ab7'),
  new City('perth', 115.857, -31.952, '#f44336'),
  new City('adelaide', 138.600, -34.928, '#00bcd4'),
  new City('hobart', 147.328, -42.881, '#9c27b0'),
];

function getCity(cityName) {
  cityName = cityName.toLowerCase();
  for (let i = 0; i < cities.length; i++) {
    if (cities[i].name === cityName) {
      return cities[i];
    }
  }
}

function Dataset(city, name, display) {
  this.city = city;
  this.name = name;
  this.display = display;
  this.loaded = false;
  this.failed = false;
  this.timestamp = new Date();
  this.data = null;
}

class MapComponent extends Component {
  constructor(props) {
    super(props);
    this.state = {
      top: null,
      bottom: null,
      left: null,
      right: null,
    };
    this.map = React.createRef();
  }

  boundsChanged = () => {
    const bleed = 0.025;
    let bounds = this.map.current.getBounds();
    this.setState({
      top: bounds.f.f + bleed,
      bottom: bounds.f.b - bleed,
      left: bounds.b.b - bleed,
      right: bounds.b.f + bleed,
    });
  };

  handleHover = area => {
    this.props.updateInfo(area.sa2Name, [
      {key: 'Twitter count', value: area.count},
      {key: 'Sentiment score', value: Number(area.score).toFixed(3)},
    ]);
  };

  render() {
    let content = '';
    if (this.props.dataset) {
      let dataset = this.props.dataset;
      if (dataset.display === 'polygons') {
        let scoreMax = dataset.data.scoreMax;
        let scoreMin = dataset.data.scoreMin;
        content = dataset.data.areas.map(area => {
          if (this.state.top == null || (
            this.state.left < area.right && area.left < this.state.right &&
            this.state.bottom < area.top && area.bottom < this.state.top)) {
            let color = `#666666`;
            if (area.count > 0) {
              let score = area.score;
              let ratio = (score - scoreMin) / (scoreMax - scoreMin);
              ratio = scaleRatio(ratio, 2);
              color = redGreedColor(ratio);
            }
            let polygonOptions = {
              strokeWeight: 1, strokeOpacity: 0.6, strokeColor: color,
              fillOpacity: 0.4, fillColor: color,
            };
            return area.polygons.map((polygon, i) =>
              <Polygon key={`${area.sa2Code}-${i}`} paths={polygon}
                       onMouseOver={() => this.handleHover(area)} options={polygonOptions}/>);
          } else {
            return '';
          }
        });
      }
      else if (dataset.display === 'topic') {
        let dataset = this.props.dataset;
        // TODO: TOPIC
        // 将要显示的东西放到content变量中
        // https://tomchentw.github.io/react-google-maps/#ui-components
      }
    }
    return (
      <GoogleMap defaultZoom={13} ref={this.map}
                 onBoundsChanged={debounce(this.boundsChanged, 250)}
                 defaultCenter={{lat: this.props.city.lat, lng: this.props.city.lng - 0.02}}
                 defaultOptions={{
                   fullscreenControl: false,
                   mapTypeControl: false,
                   streetViewControl: false,
                 }}>
        {content}
      </GoogleMap>
    );
  }
}

const Map = compose(
  withProps({
    googleMapURL: 'https://maps.googleapis.com/maps/api/js?key=AIzaSyCYxK0c15X7efoB79ZenJ-jyhkO6Y6E9o4',
    loadingElement: <div className="wh-100"/>,
    containerElement: <div className="wh-100"/>,
    mapElement: <div className="wh-100"/>,
  }), withScriptjs, withGoogleMap,
)(MapComponent);

class DatasetDialog extends Component {
  getInitialState = (cityName = cities[0].name) => {
    return {
      datasetType: 'sentiment',
      cityName: cityName,
      filterYears: [].concat(years),
      filterWeekdays: weekdays.map(day => day.key),
    };
  };

  constructor(props) {
    super(props);
    this.state = this.getInitialState();
  }

  resetState = (cityName) => {
    this.setState(this.getInitialState(cityName));
  };

  loadDataset = () => {
    this.props.onLoadDataset({
      datasetType: this.state.datasetType,
      cityName: this.state.cityName.toLowerCase(),
      filterYears: this.state.filterYears,
      filterWeekdays: this.state.filterWeekdays,
    });
    this.props.onClose();
  };

  render() {
    const style = {
      minWidth: '240px',
      paddingBottom: '12px',
    };
    return (
      <Dialog open={this.props.open} onClose={this.props.onClose}>
        <DialogTitle>Open Dataset</DialogTitle>
        <DialogContent>
          <Grid container spacing={24}>
            <Grid item md={6}>
              <FormControl fullWidth style={style}>
                <InputLabel>Dataset type</InputLabel>
                <Select value={this.state.datasetType} onChange={e => this.setState({datasetType: e.target.value})}>
                  <MenuItem value="sentiment">
                    Sentiment Analysis
                  </MenuItem>
                  <MenuItem value="topic">
                    Topic Modeling
                  </MenuItem>
                </Select>
              </FormControl>
              <FormControl fullWidth style={style}>
                <InputLabel>City</InputLabel>
                <Select value={this.state.cityName} renderValue={() => capitalize(this.state.cityName)}
                        onChange={e => this.setState({cityName: e.target.value})}>
                  {cities.map(city =>
                    <MenuItem key={city.name} value={city.name}>{capitalize(city.name)}</MenuItem>,
                  )}
                </Select>
              </FormControl>
            </Grid>
            <Grid item md={6}>
              <FormControl fullWidth style={style}>
                <InputLabel>Year(s)</InputLabel>
                <Select multiple value={this.state.filterYears}
                        renderValue={() => this.state.filterYears.length === years.length ?
                          'All years' : this.state.filterYears.join(', ')}
                        onChange={e => this.setState({filterYears: e.target.value.sort()})}>
                  {years.map(year =>
                    <MenuItem key={year} value={year}>
                      <Checkbox checked={this.state.filterYears.indexOf(year) > -1}/>
                      <ListItemText primary={year}/>
                    </MenuItem>)}
                </Select>
              </FormControl>
              <FormControl fullWidth style={style}>
                <InputLabel>Weekday(s)</InputLabel>
                <Select multiple value={this.state.filterWeekdays}
                        renderValue={() => {
                          if (this.state.filterWeekdays.length === weekdays.length) {
                            return 'All weekdays';
                          } else {
                            let days = [];
                            for (let i = 0; i < weekdays.length; i++) {
                              let day = weekdays[i];
                              if (this.state.filterWeekdays.indexOf(day.key) > -1) {
                                days.push(day.short);
                              }
                            }
                            return days.join(', ');
                          }
                        }}
                        onChange={e => this.setState({
                          filterWeekdays: e.target.value.sort((a, b) =>
                            weekdays.indexOf(a) - weekdays.indexOf(b)),
                        })}>
                  {weekdays.map(day =>
                    <MenuItem key={day.name} value={day.key}>
                      <Checkbox checked={this.state.filterWeekdays.indexOf(day.key) > -1}/>
                      <ListItemText primary={day.name}/>
                    </MenuItem>)}
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={this.props.onClose} color="default">
            Cancel
          </Button>
          <Button onClick={this.loadDataset} color="primary">Open</Button>
        </DialogActions>
      </Dialog>
    );
  }
}

DatasetDialog.propTypes = {
  open: PropTypes.bool,
  onClose: PropTypes.func,
  onLoadDataset: PropTypes.func,
};

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      cityOpen: false,
      city: cities[0],
      panelOpen: true,
      dialogOpen: false,
      snackOpen: false,
      snackMessage: '',
      datasets: [],
      datasetSelected: null,
      datasetDisplayed: null,
      infoOpen: true,
      infoTitle: '',
      infoTable: [],
    };
    this.dialog = React.createRef();
  }

  selectCity = city => {
    this.setState({city: city, datasetDisplayed: null});
    // Do other staff...
  };

  loadDataset = options => {
    let cityName = options.cityName;
    let city = getCity(cityName);
    if (options.datasetType === 'sentiment') {
      let dataset = new Dataset(city, 'Sentiment Analysis', 'polygons');
      this.state.datasets.push(dataset);
      this.setState({datasets: this.state.datasets});
      // Send request
      let paras = new URLSearchParams();
      paras.append('city', cityName);
      paras.append('years', options.filterYears);
      paras.append('weekdays', options.filterWeekdays);
      fetch(BACKEND_HOST + '/sentiment?' + paras).then(res => res.json()).then(res => {
        dataset.data = res;
        dataset.loaded = true;
        this.showSnackBar(`Dataset loaded: ${capitalize(cityName)} - ${dataset.name}`);
        this.setState({datasets: this.state.datasets});
      }).catch(e => {
        dataset.failed = true;
        this.showSnackBar(`${e.message}: ${capitalize(cityName)} - ${dataset.name}`);
        this.setState({datasets: this.state.datasets});
      });
    } else if (options.datasetType === 'topic') {
      let dataset = new Dataset(city, 'Topic modeling', 'topic');
      this.state.datasets.push(dataset);
      this.setState({datasets: this.state.datasets});
      let paras = new URLSearchParams();
      // TODO: TOPIC
      // 设置请求参数 paras.append('key', value)
      fetch(BACKEND_HOST + '/路径?' + paras).then(res => res.json()).then(res => {
        // res 就是返回回来的JSON对象
        // 在fetch中将需要的数据保存至dataset.data，在Map中读取
        dataset.data = res;
        dataset.loaded = true;
        this.showSnackBar(`Dataset loaded: ${capitalize(cityName)} - ${dataset.name}`);
        this.setState({datasets: this.state.datasets});
      }).catch(e => {
        dataset.failed = true;
        this.showSnackBar(`${e.message}: ${capitalize(cityName)} - ${dataset.name}`);
        this.setState({datasets: this.state.datasets});
      });

    }
  };

  selectDataset = dataset => {
    if (this.state.datasetSelected !== dataset) {
      this.setState({datasetSelected: dataset});
    } else {
      this.setState({datasetSelected: false});
    }
  };

  displayDataset = dataset => {
    if (dataset === null) {
      this.setState({datasetDisplayed: dataset});
    } else if (dataset.loaded) {
      if (this.state.city !== dataset.city) {
        this.selectCity(dataset.city);
      }
      this.setState({datasetDisplayed: dataset, panelOpen: false});
      this.showSnackBar(`Switched to: ${capitalize(dataset.city.name)} - ${dataset.name}`);
    } else if (dataset.failed) {
      this.showSnackBar('Failed to load dataset!');
    } else {
      this.showSnackBar('Please wait while the dataset is loading...');
    }
  };

  deleteDataset = dataset => {
    this.setState({datasets: this.state.datasets.filter(item => item !== dataset)});
    if (dataset === this.state.datasetDisplayed) {
      this.setState({datasetDisplayed: null});
    }
  };

  openDialog = () => {
    this.dialog.current.resetState(this.state.city.name);
    this.setState({dialogOpen: true});
  };

  showSnackBar = message => {
    this.setState({
      snackOpen: true,
      snackMessage: message,
    });
  };

  updateInfo = (title, table) => {
    this.setState({
      infoTitle: title,
      infoTable: table,
    });
  };

  render() {
    return (
      <MuiThemeProvider theme={theme}>
        <div className="wh-100">
          <CssBaseline/>
          <Map city={this.state.city} key={this.state.city.name}
               dataset={this.state.datasetDisplayed} updateInfo={this.updateInfo}/>
          <Button id="panel-trigger" variant="contained" title="Show / hide dataset panel"
                  onClick={() => this.setState({panelOpen: !this.state.panelOpen})}>
            <MenuIcon/></Button>
          <Card id="info-panel" className={this.state.infoOpen && this.state.infoTitle ? 'open' : ''}>
            {this.state.infoOpen && this.state.infoTitle ?
              <CardContent>
                <Button disableRipple onClick={() => this.setState({infoOpen: false})}
                        style={{width: '40px', minWidth: '40px', position: 'absolute', 'top': '10px', right: '10px'}}>
                  <RemoveIcon/>
                </Button>
                <Typography gutterBottom variant="h6" style={{marginRight: '36px'}}>
                  {this.state.infoTitle}
                </Typography>
                {this.state.infoTable.length > 0 ?
                  <>
                    <Divider style={{marginBottom: '16px'}}/>
                    <table>
                      <tbody>
                      {this.state.infoTable.map(row =>
                        <tr key={row.key}>
                          <td style={{paddingRight: '12px'}}>
                            <Typography gutterBottom variant="body1">{row.key}: </Typography>
                          </td>
                          <td><Typography gutterBottom variant="body1">{row.value}</Typography></td>
                        </tr>)}
                      </tbody>
                    </table>
                  </> : ''}
              </CardContent> :
              <Button id="info-trigger" disableRipple
                      title="Show / hide info panel"
                      style={{background: 'white', width: '40px', height: '40px', minWidth: '40px'}}
                      onClick={() => this.setState({infoOpen: !this.state.infoOpen})}>
                {this.state.infoOpen ? <InfoIcon/> : <InfoOutlinedIcon/>}
              </Button>}
          </Card>
          <Card id="city-selector">
            {cities.map(city => {
              let active = this.state.city.name === city.name;
              let display = active || this.state.cityOpen ? 'inline-flex' : 'none';
              let color = this.state.cityOpen && active ? 'primary' : 'default';
              let variant = this.state.cityOpen && active ? 'contained' : 'text';
              return <Button key={city.name} style={{display: display}} color={color} variant={variant}
                             onClick={() => this.selectCity(city)}>{city.name}</Button>;
            })}
            <Button disableRipple className="trigger" style={{background: 'white'}}
                    title="Show / hide city list"
                    onClick={() => this.setState({cityOpen: !this.state.cityOpen})}>
              {this.state.cityOpen ? <ChevronLeftIcon/> : <ChevronRightIcon/>}
            </Button>
          </Card>
          <Card id="panel" className={this.state.panelOpen ? 'open' : ''}>
            <CardContent>
              <Grid container>
                <Grid item xs>
                  <Typography gutterBottom variant="h5">
                    Dataset List
                  </Typography>
                </Grid>
                <Grid item xs={false}>
                  <Button color="primary" onClick={this.openDialog} title="Open new dataset">
                    <AddCircleOutlineIcon fontSize="small" style={{marginRight: '4px'}}/>open
                  </Button>
                </Grid>
              </Grid>
              <Divider/>
              {this.state.datasets.length > 0 ?
                this.state.datasets.map(dataset =>
                  <ExpansionPanel key={dataset.timestamp.getTime()}
                                  expanded={this.state.datasetSelected === dataset}
                                  onChange={() => this.selectDataset(dataset)}>
                    <ExpansionPanelSummary expandIcon={<ExpandMoreIcon/>}>
                      {dataset.loaded || dataset.failed ?
                        <Avatar style={{background: dataset.city.color, marginRight: '8px'}}>
                          {dataset.city.name.charAt(0).toUpperCase()}
                        </Avatar> :
                        <CircularProgress size={24} style={{margin: '8px 16px 8px 8px'}}/>}
                      <Typography variant="body2" style={{lineHeight: '40px'}}>{dataset.name}</Typography>
                    </ExpansionPanelSummary>
                    {dataset.loaded || dataset.failed ?
                      <ExpansionPanelDetails>
                        <table>
                          <tbody>
                          <tr>
                            <td><Typography variant="body2">City:</Typography></td>
                            <td><Typography variant="body2">{capitalize(dataset.city.name)}</Typography></td>
                          </tr>
                          <tr>
                            <td><Typography variant="body2">Dataset:</Typography></td>
                            <td><Typography variant="body2">{capitalize(dataset.name)}</Typography></td>
                          </tr>
                          </tbody>
                        </table>
                      </ExpansionPanelDetails> :
                      <ExpansionPanelDetails>
                        <Typography variant="body1">Loading the dataset...</Typography>
                      </ExpansionPanelDetails>}
                    {dataset.loaded || dataset.failed ?
                      <ExpansionPanelActions>
                        <Button size="small" color="secondary"
                                onClick={() => this.deleteDataset(dataset)}>delete</Button>
                        <Button size="small" color="primary"
                                onClick={() => this.displayDataset(dataset)}>display</Button>
                      </ExpansionPanelActions> : ''}
                  </ExpansionPanel>)
                : ''}
            </CardContent>
          </Card>
        </div>
        <DatasetDialog ref={this.dialog} open={this.state.dialogOpen}
                       onClose={() => this.setState({dialogOpen: false})}
                       onLoadDataset={this.loadDataset}/>
        <Snackbar open={this.state.snackOpen} autoHideDuration={4000}
                  onClose={() => this.setState({snackOpen: false})}
                  anchorOrigin={{vertical: 'top', horizontal: 'center'}}
                  message={<span>{this.state.snackMessage}</span>}
                  action={<IconButton key="close" color="inherit"
                                      onClick={() => this.setState({snackOpen: false})}>
                    <CloseIcon/></IconButton>}/>
      </MuiThemeProvider>
    );
  }
}

export default App;
