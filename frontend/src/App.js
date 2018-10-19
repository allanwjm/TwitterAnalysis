import Avatar from '@material-ui/core/Avatar';
import Button from '@material-ui/core/Button';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import blue from '@material-ui/core/colors/blue';
import CssBaseline from '@material-ui/core/CssBaseline';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogTitle from '@material-ui/core/DialogTitle';
import Divider from '@material-ui/core/Divider';
import FormControl from '@material-ui/core/FormControl';
import Grid from '@material-ui/core/Grid';
import IconButton from '@material-ui/core/IconButton';
import InputLabel from '@material-ui/core/InputLabel';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemSecondaryAction from '@material-ui/core/ListItemSecondaryAction';
import ListItemText from '@material-ui/core/ListItemText';
import MenuItem from '@material-ui/core/MenuItem';
import Select from '@material-ui/core/Select';
import {createMuiTheme} from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import {default as AddCircleOutlineIcon} from '@material-ui/icons/AddCircleOutline';
import {default as ChevronLeftIcon} from '@material-ui/icons/ChevronLeft';
import {default as ChevronRightIcon} from '@material-ui/icons/ChevronRight';
import {default as DeleteIcon} from '@material-ui/icons/Delete';
import {default as FolderIcon} from '@material-ui/icons/Folder';
import {default as MenuIcon} from '@material-ui/icons/Menu';
import React, {Component} from 'react';
import {GoogleMap, Marker, withGoogleMap, withScriptjs} from 'react-google-maps';
import {compose, withProps} from 'recompose';
import './style.css';

const theme = createMuiTheme({
  palette: {
    primary: blue,
  },
  typography: {
    useNextVariants: true,
  },
});

const cities = [
  {
    name: 'melbourne',
    lng: 144.962,
    lat: -37.816,
  },
  {
    name: 'sydney',
    lng: 151.208,
    lat: -33.868,
  },
  {
    name: 'brisbane',
    lng: 153.025,
    lat: -27.469,
  },
  {
    name: 'canberra',
    lng: 149.125,
    lat: -35.310,
  },
  {
    name: 'perth',
    lng: 115.857,
    lat: -31.952,
  },
  {
    name: 'adelaide',
    lng: 138.600,
    lat: -34.928,
  },
  {
    name: 'hobart',
    lng: 147.328,
    lat: -42.881,
  },
];

const availDatasets = [
  {
    name: 'Sentiment Analysis',
  },
  {
    name: 'Topic Modeling',
  },
];

function Dataset(name) {
  this.name = name;
}

const Map = compose(
  withProps({
    googleMapURL: 'https://maps.googleapis.com/maps/api/js?key=AIzaSyCYxK0c15X7efoB79ZenJ-jyhkO6Y6E9o4',
    loadingElement: <div className="wh-100"/>,
    containerElement: <div className="wh-100"/>,
    mapElement: <div className="wh-100"/>,
  }), withScriptjs, withGoogleMap)(props =>
  <GoogleMap defaultZoom={13}
             defaultCenter={{lat: props.city.lat, lng: props.city.lng}}
             defaultOptions={{mapTypeControl: false, streetViewControl: false}}>
    <Marker position={{lat: props.city.lat, lng: props.city.lng}}/>
  </GoogleMap>,
);

class DatasetDialog extends Component {
  constructor(props) {
    super(props);
    this.state = {};
  }

  render() {
    return (
      <Dialog open={this.state.dialogOpen}
              onClose={() => this.setState({dialogOpen: false})}>
        <DialogTitle>Open Dataset</DialogTitle>
        <Divider/>
        <DialogContent>
          <FormControl style={{minWidth: '240px'}}>
            <InputLabel>Dataset type</InputLabel>
            <Select value={this.state.age}
                    onChange={this.handleChange}>
              <MenuItem value="sentiment">
                Sentiment Analysis
              </MenuItem>
              <MenuItem value="topic">
                Topic Modeling
              </MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => this.setState({dialogOpen: false})} color="default">
            Cancel
          </Button>
          <Button onClick={() => this.setState({dialogOpen: false})} color="primary">
            Open
          </Button>
        </DialogActions>
      </Dialog>
    );
  }
}

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      city: cities[0],
      cityOpen: true,
      panelOpen: true,
      dialogOpen: false,
      datasets: [new Dataset('Wow'), new Dataset('Aha'), new Dataset('Alalal')],
      dataset: null,
    };
  }

  selectCity = city => {
    this.setState({city: city});
    // Do other staff...
  };

  selectDataset = dataset => {
    this.setState({dataset: dataset});
    // Do other staff...
  };

  render() {
    return (
      <div className="wh-100">
        <CssBaseline/>
        <Map city={this.state.city} key={this.state.city.name}/>
        <Button id="panel-trigger" variant="contained"
                onClick={() => this.setState({panelOpen: !this.state.panelOpen})}><MenuIcon/></Button>
        <Card id="city-selector">
          {cities.map(city => {
            let active = this.state.city.name === city.name;
            let display = active || this.state.cityOpen ? 'inline-flex' : 'none';
            let color = this.state.cityOpen && active ? 'primary' : 'default';
            let variant = this.state.cityOpen && active ? 'contained' : 'text';
            return <Button key={city.name} style={{display: display}} color={color} variant={variant}
                           onClick={() => this.selectCity(city)}>{city.name}</Button>;
          })}
          <Button className="trigger" onClick={() => this.setState({cityOpen: !this.state.cityOpen})}>
            {this.state.cityOpen ? <ChevronLeftIcon/> : <ChevronRightIcon/>}
          </Button>
        </Card>
        <Card id="panel" className={this.state.panelOpen ? 'open' : ''}>
          <CardContent>
            <Grid container>
              <Grid item xs>
                <Typography gutterBottom variant="h5" component="h2">
                  Datasets
                </Typography>
              </Grid>
              <Grid item xs={false}>
                <Button color="primary" onClick={() => this.setState({dialogOpen: true})}>
                  <AddCircleOutlineIcon fontSize="small" style={{marginRight: '4px'}}/>open
                </Button>
              </Grid>
            </Grid>
            <Divider/>
            {this.state.datasets.length > 0 ?
              <List>
                {this.state.datasets.map(dataset =>
                  <ListItem
                    button key={dataset.name}
                    selected={this.state.dataset === dataset}
                    onClick={() => this.selectDataset(dataset)}>
                    <Avatar>
                      <FolderIcon/>
                    </Avatar>
                    <ListItemText primary={dataset.name}/>
                    <ListItemSecondaryAction>
                      <IconButton>
                        <DeleteIcon/>
                      </IconButton>
                    </ListItemSecondaryAction>
                  </ListItem>)}
              </List> :
              <Typography variant="h5" component="h2">
                No datasets!
              </Typography>}
          </CardContent>
        </Card>
      </div>
    );
  }
}

export default App;
