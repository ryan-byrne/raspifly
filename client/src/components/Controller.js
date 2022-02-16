import { Button, Container, Form, ListGroup, ListGroupItem, Offcanvas, Table } from 'react-bootstrap';
import {useEffect, useState} from 'react';

const xboxController = {
  x:{type:'axes',idx:0},
  y:{type:'axes',idx:1},
  z_up:{type:'buttons',idx:4},
  z_down:{type:'buttons',idx:5},
  roll:{type:'axes',idx:3},
  pitch:{type:'axes',idx:4},
  yaw_right:{type:'axes',idx:2},
  yaw_left:{type:'axes',idx:5},
}

const Controller = (props) => {

  const [gamepads, setGamepads] = useState([]);
  const [selected, setSelected] = useState(0);

  const [surfaces, setSurfaces] = useState({buttons:[], axes:[]})

  const controllerLoop = () => {

    if (!gamepads[selected]){
      return
    }

    var gamepad = gamepads[selected];

    setSurfaces({
      buttons:gamepad.buttons.map(b=>b.pressed), 
      axes:gamepad.axes
    })

    requestAnimationFrame(controllerLoop);

  }

  const refreshGamepads = () => setGamepads(navigator.getGamepads());

  const handleRoleSelect = (e) => console.log(e.target.value);

  useEffect(()=>{
    setSelected(0);
    window.addEventListener("gamepadconnected", (e) => 
      gamepads.map(g=>g.id).includes(e.gamepad.id)?null:setGamepads([...gamepads, e.gamepad]));
    window.addEventListener("gamepaddisconnected", (e) => setGamepads([...gamepads.filter(g=>g.id!==e.gamepad.id)]));
  },[gamepads, setSelected])

  useEffect(()=>gamepads[selected]?controllerLoop():null,[gamepads, selected])

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
        Axes:
        <Table>
          <thead>
            <tr><th>Index</th><th>Value</th><th>Role</th></tr>
          </thead>
          <tbody>
            {surfaces.axes.map((a, idx)=>
              <tr>
                <td>{idx}</td>
                <td>{a}</td>
                <td>
                </td>
              </tr>
            )}
          </tbody>
        </Table>
        Buttons:
        <Table className='text-center'>
          <thead><th>Index</th><th>Pressed</th><th>Role</th></thead>
          <tbody>
            {surfaces.buttons.map((b, idx)=>
              <tr>
                <td>{idx}</td>
                <td>{b?"Active":"No"}</td>
                <td>
                </td>
              </tr>
            )}
          </tbody>
        </Table>
      </Offcanvas.Body>
    </Offcanvas>
  )
}

export default Controller;