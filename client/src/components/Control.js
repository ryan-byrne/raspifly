import { Alert, Badge, Button, Collapse, Container, Fade, Form, ListGroup, ListGroupItem, Offcanvas, ToggleButton } from 'react-bootstrap';
import {useEffect, useState} from 'react';

var requestAnimationFrame = window.requestAnimationFrame || window.mozRequestAnimationFrame ||
                            window.webkitRequestAnimationFrame || window.msRequestAnimationFrame;

var cancelAnimationFrame = window.cancelAnimationFrame || window.mozCancelAnimationFrame;

var requestId;

const Keyboard = (props) => {

  const [pressedKeys, setPressedKeys] = useState({
    ArrowDown:false, ArrowUp:false, ArrowRight:false, ArrowLeft:false, a:false, s:false, d:false, w:false
  });

  const handleKeyChange = ({type, key}) => setPressedKeys(pressedKeys => ({...pressedKeys, [key]: type==="keydown"})); 

  useEffect(()=>{
    window.addEventListener("keydown", handleKeyChange);
    window.addEventListener("keyup", handleKeyChange);
    return () => {
      window.removeEventListener("keydown", handleKeyChange);
      window.removeEventListener("keyup", handleKeyChange);
    };
  },[]);

  useEffect(()=>props.setPayload({
    x:pressedKeys.ArrowLeft?-0.5:pressedKeys.ArrowRight?0.5:0,
    y:pressedKeys.ArrowDown?-0.5:pressedKeys.ArrowUp?0.5:0,
    z:pressedKeys.s?-0.5:pressedKeys.w?0.5:0,
    yaw:pressedKeys.a?-0.5:pressedKeys.d?0.5:0,
  }),[pressedKeys])

  return(
    <Container>

    </Container>
  )
}

const Gamepad = () => {

}

const Settings = (props) => {

  const [options, setOptions] = useState(navigator.getGamepads());
  const refreshGamepads = () => setOptions(navigator.getGamepads());

  const handleConnect = (e) => options.map(g=>g.id).includes(e.gamepad.id)?null:setOptions([...options, e.gamepad]);
  const handleDisconnect = (e) => setOptions([...options.filter(g=>g.id!==e.gamepad.id)]);

  useEffect(()=>{
    window.addEventListener("gamepadconnected", handleConnect);
    window.addEventListener("gamepaddisconnected", handleDisconnect);
    return () => {
      window.addEventListener("gamepadconnected", handleConnect);
      window.addEventListener("gamepaddisconnected", handleDisconnect);
    }
  },[]);

  return (
    <Offcanvas show={props.show} onHide={props.handleHide}>
      <Offcanvas.Header closeButton>
        <Offcanvas.Title>
          Control Settings
        </Offcanvas.Title>
      </Offcanvas.Header>
      <Offcanvas.Body>
        <Collapse in={false}>
          <>
            <Alert variant="warning">No Device Selected</Alert>
          </>
        </Collapse>
      <Form.Group>
        {options.length} Gamepad(s) Connected
        <Button size="sm" className="m-3" onClick={refreshGamepads}>Refresh</Button>
        <ListGroup>
          <Form.Text>Select a Gamepad:</Form.Text>
          {options.map((gamepad, idx)=>
            <ListGroup.Item action disabled={false} key={idx} id={idx} onClick={()=>props.setDevice(gamepad)}>
              {gamepad.id}
            </ListGroup.Item>
          )}
          <ListGroup.Item action onClick={()=>props.setDevice({id:"keyboard"})} id="keyboard" onClick={()=>props.setDevice({id:'keyboard'})}>
            Use Keyboard
          </ListGroup.Item>
        </ListGroup>
      </Form.Group>
      </Offcanvas.Body>
    </Offcanvas>
  )
}

const Control = (props) => {

  const [showSettings, setShowSettings] = useState(true);
  const [device, setDevice] = useState();

  return (
    <Container className='controller-container'>
      <h1>Control <a href="#"><img src="https://i.imgur.com/7T91kCB.png" onClick={()=>setShowSettings(true)}/></a></h1>
      <p>Device: {device?<Badge bg="success">{device.id}</Badge>:<Badge bg="danger">None</Badge>}</p>
      <p>Hello</p>
      <Settings show={showSettings} handleHide={()=>setShowSettings(false)} setDevice={setDevice} device={device}/>
    </Container>
    
  )
}

export default Control;