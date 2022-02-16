import { Button, Container, Form, ListGroup, ListGroupItem, Offcanvas, Table } from 'react-bootstrap';
import {useEffect, useRef, useState} from 'react';

var requestAnimationFrame = window.requestAnimationFrame || window.mozRequestAnimationFrame ||
                            window.webkitRequestAnimationFrame || window.msRequestAnimationFrame;

var cancelAnimationFrame = window.cancelAnimationFrame || window.mozCancelAnimationFrame;

var requestId;

const Controller = (props) => {

  const [options, setOptions] = useState(navigator.getGamepads());
  const [gamepad, setGamepad] = useState({});
  const [keyboardControl, setKeyboardControl] = useState(null);

  const refreshGamepads = () => setOptions(navigator.getGamepads());

  useEffect(()=>{
    window.addEventListener("gamepadconnected", (e) => options.map(g=>g.id).includes(e.gamepad.id)?null:setOptions([...options, e.gamepad]));
    window.addEventListener("gamepaddisconnected", (e) => setOptions([...options.filter(g=>g.id!==e.gamepad.id)]));
    window.addEventListener("keydown", (e) => console.log(e.key));
    window.addEventListener("keyup", (e) => console.log(e.key));
  },[options])

  useEffect(()=>{

    const controlLoop = async () => {

      const payload = {};
  
      const resp = await fetch('/api/control', {
        method:"POST",
        headers:{
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body:JSON.stringify(payload)
      })

      requestId = requestAnimationFrame(controlLoop);

    }

    if (!gamepad.id && !keyboardControl){
      cancelAnimationFrame(requestId);
      return;
    } else {
      requestId = requestAnimationFrame(controlLoop);
    }

  },[gamepad, keyboardControl])
  
  console.log(keyboardControl);

  return (
    <Offcanvas show={props.show} onHide={props.handleHide}>
      <Offcanvas.Header closeButton>
        <Offcanvas.Title>
          Controller Settings
        </Offcanvas.Title>
      </Offcanvas.Header>
      <Offcanvas.Body>
        <Form.Group>
          <Form.Check label="Use Keyboard as Controller" checked={keyboardControl!=null} onClick={()=>setKeyboardControl(!keyboardControl?{}:null)}/>
        </Form.Group>
        <Form.Group>
          {options.length} Gamepad(s) Connected
          <Button size="sm" className="m-3" onClick={refreshGamepads}>Refresh</Button>
          <ListGroup className="mb-3">
            {options.map((gpad, idx)=>
              <ListGroupItem action key={idx} variant={gpad.id==gamepad.id?"info":null} onClick={()=>setGamepad(gpad.id===gamepad.id?{}:options[idx])}
                disabled={keyboardControl!=null}>
                {gpad.id}
              </ListGroupItem>  
            )}
          </ListGroup>
        </Form.Group>
      </Offcanvas.Body>
    </Offcanvas>
  )
}

export default Controller;