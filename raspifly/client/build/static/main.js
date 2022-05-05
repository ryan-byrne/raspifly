
const Telemetry = ({active}) => {

    const [data, setData] = React.useState({
        z_pos:0
    })

    React.useEffect(()=>{

        if (!active){ return }

        const source = new EventSource('/api/telemetry');
        source.onmessage = (e) => setData(JSON.parse(JSON.parse(e.data)));
        
    },[active]);

    return(
        <div>
            <h1>Telemetry</h1>
            <table className="table table-dark table-striped">
                <tbody>
                    {Object.entries(data).map(([key, value], idx)=>
                        <tr key={idx} className="table-dark">
                            <th className="table-dark">{key}</th>
                            <td className="table-dark">{value.toFixed(2)}</td>
                        </tr>
                    )}
                </tbody>
            </table>
        </div>
    )
}

const App = () => {

    const [status, setStatus] = React.useState({message:"stopped",variant:"info"});

    const handleStart = () => fetch("/api/start", {method:"POST"})
        .then( resp => setStatus({message:"started", variant:"info"}) )
        .catch( err => setStatus({message:"error", variant:"danger"}) )

    const handleStop = () => fetch("/api/stop", {method:"POST"})
        .then( resp => setStatus({message:"stopped", variant:"info"}) )
        .catch( err => setStatus({message:"error", variant:"error"}) )

    return(
        <div className="container-fluid">
            <div className="row">
                <div className="col">
                    <h1>Camera Feed</h1>
                </div>
                <div className="col">
                    <Telemetry active={status.message==="started"}/>
                </div>
            </div>
            <div className="row">
                <div className="col">
                    <h1>Control</h1>
                </div>
                <div className="col">
                    <h1>Settings</h1>
                </div>
            </div>
            <div className="row mt-5">
                {status.message === "stopped" ?
                    <button type="button" className={`btn btn-success`} onClick={handleStart}>Start</button> :
                    <button type="button" className={`btn btn-danger`} onClick={handleStop}>Stop</button>
                }
            </div>
        </div>
    )
}

root = ReactDOM.createRoot(document.getElementById('root'));

root.render(
    React.createElement(App),   
);