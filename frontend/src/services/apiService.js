const API_BASE="http://localhost:8001/api"

export async function uploadPDF(formData){

const res=await fetch(`${API_BASE}/process-pdf`,{
method:"POST",
body:formData
})

return res.json()

}

export async function checkPython(formData){

const res=await fetch(`${API_BASE}/check-compliance`,{
method:"POST",
body:formData
})

return res.json()

}