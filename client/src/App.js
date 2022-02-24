
import { useState } from 'react';
import { Button } from 'react-bootstrap';

import Control from './components/Control';
import Communication from './components/Communication';
import Telemetry from './components/Telemetry';

const App = () => {

  const [settings, setSettings] = useState();

  const handleGet = () => fetch("/api/telemetry")
    .then(resp=> resp.json())
    .then(data=>console.log(data))
    .catch(err=>console.error(err))

  return (
    <div className="App">
      <Control/>
      <Telemetry/>
      <Communication/>
    </div>
  );
}

export default App;
