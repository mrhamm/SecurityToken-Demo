import { BrowserRouter as Router, Route, Switch } from "react-router-dom";
import { Home, Navigation, Minter, CrowdSale, Register, Exchange } from "./components"



function App() {
  return (
    <div className="App">

      <Router>
        <Navigation/>  
        <Switch>
          <Route path="/" exact component = {() => <Home/>}/>
          <Route path="/Minter" exact component = {()=> <Minter/>}/>
          <Route path="/CrowdSale" exact component = {() => <CrowdSale/>}/>
          <Route path="/Register" exact component = {() => <Register/>}/>
          <Route path="/Exchange" exact component ={()=> <Exchange/>}/>
          
        </Switch>
      </Router>

    </div>
  );
}

export default App;
