import React,{useState} from "react";
import {uploadPDF} from "../services/apiService";
import RulesTable from "./RulesTable";
import ProgressBar from "./ProgressBar";

function PdfUpload(){

const [file,setFile]=useState(null)
const [rules,setRules]=useState([])
const [loading,setLoading]=useState(false)

const handleUpload=async()=>{

if(!file) return

const formData=new FormData()
formData.append("file",file)

setLoading(true)

const res=await uploadPDF(formData)

setRules(res.rules)

setLoading(false)

}

return(

<div>

<div className="section">

<input type="file"
accept=".pdf"
onChange={(e)=>setFile(e.target.files[0])}
/>

<button onClick={handleUpload}>
Generate Rules
</button>

{loading && <ProgressBar/>}

</div>

<RulesTable rules={rules}/>

</div>

)

}

export default PdfUpload