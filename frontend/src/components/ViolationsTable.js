import React from "react";

function ViolationsTable({result}){

if(!result) return null

if(result.compliance_status==="safe"){

return <div className="safe">✔ No Violations Detected</div>

}

return(

<div>

<div className="violation">
⚠ Violations Detected
</div>

{result.violations.map((block,index)=>(

<div key={index} className="section">

<h4>{block.block_scope} : {block.block_name}</h4>

<div className="code-block">
{block.code}
</div>

<table>

<thead>
<tr>
<th>Rule</th>
<th>Reason</th>
</tr>
</thead>

<tbody>

{block.violations.map((v,i)=>(
<tr key={i}>
<td>{v.rule_id}</td>
<td>{v.reason}</td>
</tr>
))}

</tbody>

</table>

</div>

))}

</div>

)

}

export default ViolationsTable