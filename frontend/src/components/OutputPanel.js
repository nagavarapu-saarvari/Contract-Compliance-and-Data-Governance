import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";

function OutputPanel({ output }) {
  return (
    <Card className="border-l-4 border-l-primary-400 bg-primary-50">

      <CardHeader className="pb-3">
        <CardTitle className="text-base text-slate-800">
          Output
        </CardTitle>
      </CardHeader>

      <CardContent>

        <div className="max-h-[420px] overflow-y-auto rounded-lg bg-slate-900 text-slate-100 p-4 shadow-inner">

          <pre className="text-xs font-mono whitespace-pre-wrap break-words">
            {output || "No output generated yet."}
          </pre>

        </div>

      </CardContent>

    </Card>
  );
}

export default OutputPanel;