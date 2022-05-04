
const App = () => {

    const [status, setStatus] = React.useState({message:"",variant:""});

    const handleStart = () => fetch("/api/start", {method:"POST"})
        .then( resp => setStatus({message:resp.text, variant:"success"}) )
        .catch( err => setStatus({message:err.error, variant:"error"}) )

    const handleStop = () => fetch("/api/stop", {method:"POST"})
        .then( resp => setStatus({message:resp.text, variant:"success"}) )
        .catch( err => setStatus({message:err.error, variant:"error"}) )

    return(
        <div>
            <button onClick={handleStart}>Start</button>
            <button onClick={handleStop}>Stop</button>
            <div className={status.variant}>{status.message}</div>
        </div>
    )
}

root = ReactDOM.createRoot(document.getElementById('root'));

root.render(
    React.createElement(App),   
);