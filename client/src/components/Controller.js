import { Button, Container, ListGroup, ListGroupItem, Offcanvas } from 'react-bootstrap';
import {useEffect, useState} from 'react';
import { isAccordionItemSelected } from 'react-bootstrap/esm/AccordionContext';

const Controller = (props) => {

  const [gamepads, setGamepads] = useState([]);
  const [selected, setSelected] = useState(0);
  const [state, setState] = useState({buttons:[], axes:[]});

  const controllerLoop = () => {

    if (!gamepads[selected]){
      return
    }

    var gamepad = gamepads[selected];

    setState({
      buttons:gamepad.buttons.map(b=>b.value), 
      axes:gamepad.axes
    })

    requestAnimationFrame(controllerLoop);

  }

  const refreshGamepads = () => setGamepads(navigator.getGamepads());

  useEffect(()=>{
    setSelected(0);
    window.addEventListener("gamepadconnected", (e) => 
      gamepads.map(g=>g.id).includes(e.gamepad.id)?null:setGamepads([...gamepads, e.gamepad]));
    window.addEventListener("gamepaddisconnected", (e) => setGamepads([...gamepads.filter(g=>g.id!==e.gamepad.id)]));
  },[gamepads, setSelected])

  useEffect(()=>
    gamepads[selected]?controllerLoop():null
  ,[gamepads, selected])

  return (
    <Offcanvas show={props.show} onHide={props.handleHide}>
      <Offcanvas.Header closeButton>
        <Offcanvas.Title>
          Controller Settings
        </Offcanvas.Title>
      </Offcanvas.Header>
      <Offcanvas.Body>
        {gamepads.length} Gamepad(s) Connected
        <Button size="sm" className="m-3" onClick={refreshGamepads}>Refresh</Button>
        <ListGroup className="mb-3">
          {gamepads.map((gpad, idx)=>
            <ListGroupItem action key={idx} variant={selected===idx?"info":null} onClick={()=>setSelected(idx)}>
              {gpad.id}
            </ListGroupItem>  
          )}
        </ListGroup>
        Buttons:
        <ul>
          {state.buttons.map(b=><li>{b}</li>)}
        </ul>
        Axes:
        <ul>
          {state.axes.map(b=><li>{b}</li>)}
        </ul>
      </Offcanvas.Body>
    </Offcanvas>
  )
}

export default Controller;