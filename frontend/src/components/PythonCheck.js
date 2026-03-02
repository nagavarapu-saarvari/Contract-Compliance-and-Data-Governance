import React,{useState} from "react";
import {checkPython} from "../services/apiService";
import ViolationsTable from "./ViolationsTable";
import ProgressBar from "./ProgressBar";

function PythonCheck(){

const [file,setFile]=useState(null)
const [result,setResult]=useState(null)
const [loading,setLoading]=useState(false)

const handleCheck=async()=>{

if(!file) return

const formData=new FormData()
formData.append("file",file)

setLoading(true)

const res=await checkPython(formData)

setResult(res)

setLoading(false)

}

return(

<div>

<div className="section">

<input type="file"
accept=".py"
onChange={(e)=>setFile(e.target.files[0])}
/>

<button onClick={handleCheck}>
Check Compliance
</button>

{loading && <ProgressBar/>}

</div>

<ViolationsTable result={result}/>

</div>

)

}

export default PythonCheck