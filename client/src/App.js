const App = () => {

  const handleGet = () => fetch("/api/telemetry")
    .then(resp=> resp.json())
    .then(data=>console.log(data))
    .catch(err=>console.error(err))

  return (
    <div className="App">
      <button onClick={handleGet}>Get API</button>
    </div>
  );
}

export default App;
