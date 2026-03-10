import React, { useState, useRef, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Cpu, ChevronDown } from "lucide-react";

function ModelSelector() {

  const models = [
    { id: "gpt-4.1-mini", name: "GPT-4.1 Mini" }
  ];

  const [selectedModel, setSelectedModel] = useState(models[0]);
  const [open, setOpen] = useState(false);

  const dropdownRef = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {

    const handleClickOutside = (event) => {

      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setOpen(false);
      }

    };

    document.addEventListener("mousedown", handleClickOutside);

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };

  }, []);

  return (
    <Card className="border-l-4 border-l-primary-400">

      <CardHeader className="pb-3">

        <div className="flex items-center gap-2">
          <Cpu className="h-5 w-5 text-primary-400" />
          <CardTitle className="text-base">LLM Model</CardTitle>
        </div>

      </CardHeader>

      <CardContent>

        <div ref={dropdownRef} className="relative">

          {/* Selected Model */}
          <div
            onClick={() => setOpen(!open)}
            className="flex items-center justify-between gap-2 rounded-lg bg-primary-50 px-4 py-3 border border-primary-200 cursor-pointer hover:border-primary-300 transition-colors"
          >

            <span className="font-semibold text-primary-700">
              {selectedModel.name}
            </span>

            <ChevronDown
              className={`h-4 w-4 text-primary-500 transition-transform duration-200 ${
                open ? "rotate-180" : ""
              }`}
            />

          </div>

          {/* Dropdown */}
          {open && (

            <div className="absolute mt-2 w-full rounded-lg border border-primary-200 bg-white shadow-md overflow-hidden z-10">

              {models.map((model) => (

                <div
                  key={model.id}
                  onClick={() => {
                    setSelectedModel(model);
                    setOpen(false);
                  }}
                  className="flex items-center gap-2 px-4 py-3 hover:bg-primary-50 cursor-pointer transition-colors"
                >

                  <span className="font-medium text-slate-700">
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