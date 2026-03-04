import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Cpu, ChevronDown } from "lucide-react";

function ModelSelector() {

  const models = [
    { id: "gpt-4.1-mini", name: "GPT-4.1 Mini" }
  ];

  const [selectedModel, setSelectedModel] = useState(models[0]);
  const [open, setOpen] = useState(false);

  return (
    <Card className="border-l-4 border-l-primary-500">
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2">
          <Cpu className="h-5 w-5 text-primary-600" />
          <CardTitle className="text-base">LLM Model</CardTitle>
        </div>
      </CardHeader>

      <CardContent>
        <div className="relative">

          {/* Selected model */}
          <div
            onClick={() => setOpen(!open)}
            className="flex items-center justify-between gap-2 rounded-lg bg-gradient-to-r from-primary-50 to-primary-100 px-4 py-3 border border-primary-200 cursor-pointer"
          >
            <div className="flex items-center gap-2">


              <span className="font-semibold text-primary-700">
                {selectedModel.name}
              </span>

            </div>

            <ChevronDown className="h-4 w-4 text-primary-600" />
          </div>

          {/* Dropdown */}
          {open && (
            <div className="absolute mt-2 w-full rounded-lg border border-primary-200 bg-white shadow-lg overflow-hidden">

              {models.map((model) => (
                <div
                  key={model.id}
                  onClick={() => {
                    setSelectedModel(model);
                    setOpen(false);
                  }}
                  className="flex items-center gap-2 px-4 py-3 hover:bg-primary-50 cursor-pointer"
                >

                  <span className="font-medium text-gray-700">
                    {model.name}
                  </span>
                </div>
              ))}

            </div>
          )}

        </div>
      </CardContent>
    </Card>
  );
}

export default ModelSelector;