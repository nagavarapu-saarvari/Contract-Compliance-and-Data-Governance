import React from "react";

function DocumentList({ documents, selectedDoc, setSelectedDoc }) {

  return (
    <div className="card">

      <h3>Uploaded Documents</h3>

      {documents.map((doc) => (

        <div key={doc.id}>

          <input
            type="radio"
            checked={selectedDoc === doc.id}
            onChange={() => setSelectedDoc(doc.id)}
          />

          {doc.filename}

        </div>

      ))}

    </div>
  );
}

export default DocumentList;