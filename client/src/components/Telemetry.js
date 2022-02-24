import { useState } from "react";
import { Container } from "react-bootstrap";

const Telemetry = () => {

    const [showSettings, setShowSettings] = useState(false);

    return (
        <Container>
            <h1>Telemetry <a href="#"><img src="https://i.imgur.com/7T91kCB.png" onClick={()=>setShowSettings(true)}/></a></h1>
        </Container>
    )
}

export default Telemetry;