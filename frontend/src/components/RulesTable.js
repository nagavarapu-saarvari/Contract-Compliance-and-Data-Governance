import React from "react";

function RulesTable({rules}){

if(!rules || rules.length===0) return null

return(

<table>

<thead>
<tr>
<th>Rule ID</th>
<th>Title</th>
<th>Description</th>
<th>Effect</th>
</tr>
</thead>

<tbody>

{rules.map(rule=>(
<tr key={rule.rule_id}>
<td>{rule.rule_id}</td>
<td>{rule.title}</td>
<td>{rule.description}</td>
<td>
<span className={`badge ${rule.effect}`}>
{rule.effect}
</span>
</td>
</tr>
))}

</tbody>

</table>

)

}

export default RulesTable