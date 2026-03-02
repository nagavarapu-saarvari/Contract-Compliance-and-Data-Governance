import React from "react";
import {BrowserRouter as Router,Routes,Route} from "react-router-dom";

import Navbar from "./components/Navbar";
import RuleGeneration from "./pages/RuleGeneration";
import RuleCheck from "./pages/RuleCheck";

import "./App.css";

function App(){

return(

<Router>

<Navbar/>

<div className="container">

<Routes>

<Route path="/" element={<RuleGeneration/>}/>
<Route path="/rule-check" element={<RuleCheck/>}/>

</Routes>

</div>

</Router>

)

}

export default App