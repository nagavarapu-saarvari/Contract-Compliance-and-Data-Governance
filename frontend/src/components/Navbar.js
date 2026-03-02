import React from "react";
import {Link} from "react-router-dom";

function Navbar(){

return(

<div className="navbar">

<div className="logo">
<div className="shield"></div>
</div>

<div className="nav-links">

<Link to="/">Rule Generation</Link>
<Link to="/rule-check">Rule Check</Link>

</div>

</div>

)

}

export default Navbar