import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Cpu } from "lucide-react";

function ModelSelector() {

  return (
    <Card className="border-l-4 border-l-primary-500">
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2">
          <Cpu className="h-5 w-5 text-primary-600" />
          <CardTitle className="text-base">LLM Model</CardTitle>
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex items-center gap-2 rounded-lg bg-gradient-to-r from-primary-50 to-primary-100 px-4 py-3 border border-primary-200">
          <div className="h-3 w-3 rounded-full bg-green-500 animate-pulse"></div>
          <span className="font-semibold text-primary-700">GPT-4.1 Mini</span>
        </div>
      </CardContent>
    </Card>
  );
}

export default ModelSelector;