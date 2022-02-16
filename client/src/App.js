
import { useState } from 'react';
import { Button } from 'react-bootstrap';
import Controller from './components/Controller';

const App = () => {

  const [offcanvas, setOffcanvas] = useState();

  const handleGet = () => fetch("/api/telemetry")
    .then(resp=> resp.json())
    .then(data=>console.log(data))
    .catch(err=>console.error(err))

  return (
    <div className="App">
      <Button onClick={()=>setOffcanvas('controller')}>Controller</Button>
      <Controller show={offcanvas==='controller'} handleHide={()=>setOffcanvas()}/>
    </div>
  );
}

export default App;
