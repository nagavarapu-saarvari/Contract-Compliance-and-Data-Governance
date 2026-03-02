async function uploadFile() {

    const fileInput = document.getElementById("fileInput");
    const output = document.getElementById("output");

    const file = fileInput.files[0];

    if (!file) {
        alert("Please select a file first");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    output.innerHTML = "<p>Processing...</p>";

    try {

        const response = await fetch("/upload", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        renderResults(data);

    } catch (error) {

        output.innerHTML = "<p style='color:red;'>Error processing file</p>";

    }
}

function renderResults(data) {

    const output = document.getElementById("output");

    if (data.rules) {
        renderRules(data.rules);
        return;
    }

    if (data.status === "safe") {
        output.innerHTML = "<h3>✅ No Violations Detected</h3>";
        return;
    }

    if (data.violations) {
        renderViolations(data.violations);
    }
}

function renderRules(rules) {

    let html = "<h3>Generated Rules</h3>";

    html += "<table border='1' cellpadding='8'>";
    html += "<tr><th>Rule ID</th><th>Title</th><th>Description</th><th>Effect</th></tr>";

    rules.forEach(rule => {
        html += `
        <tr>
            <td>${rule.rule_id}</td>
            <td>${rule.title}</td>
            <td>${rule.description}</td>
            <td>${rule.effect}</td>
        </tr>
        `;
    });

    html += "</table>";

    document.getElementById("output").innerHTML = html;
}

function renderViolations(violations) {

    let html = "<h3>Violations Detected</h3>";

    html += "<table border='1' cellpadding='8'>";
    html += "<tr><th>Scope</th><th>Function</th><th>Rule</th><th>Reason</th></tr>";

    violations.forEach(v => {

        v.violations.forEach(rule => {

            html += `
            <tr>
                <td>${v.scope}</td>
                <td>${v.name}</td>
                <td>${rule.rule_id}</td>
                <td>${rule.reason}</td>
            </tr>
            `;

        });

    });

    html += "</table>";

    document.getElementById("output").innerHTML = html;
}