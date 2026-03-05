import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";

function OutputPanel({ output }) {

  return (
    <Card className="border-l-4 border-l-primary-500">
      <CardHeader>
        <CardTitle className="text-base">Output</CardTitle>
      </CardHeader>
      <CardContent>
        <pre className="bg-slate-900 text-slate-100 p-4 rounded-lg overflow-x-auto text-xs font-mono">
          {output}
        </pre>
      </CardContent>
    </Card>
  );
}

export default OutputPanel;