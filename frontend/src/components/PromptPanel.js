import React, { useState } from "react";
import { Card, CardContent } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";
import { Sparkles, Send, Loader } from "lucide-react";

function PromptPanel({ selectedDoc }) {

  const [prompt, setPrompt] = useState("");
  const [statusMessage, setStatusMessage] = useState("");
  const [rules, setRules] = useState([]);
  const [showGuided, setShowGuided] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const guidedPrompts = [
    "Generate governance rules from the selected contract",
    "Extract enforceable business policies from the contract",
    "Identify data sharing restrictions in the agreement",
    "List all compliance obligations present in the document"
  ];

  const selectGuidedPrompt = (text) => {
    setPrompt(text);
    setShowGuided(false);
  };

  const handleSubmit = async () => {

    if (!selectedDoc) {
      alert("Please select a document first");
      return;
    }

    setPrompt("")
    setRules([]);
    setStatusMessage("Parsing PDF...");
    setIsLoading(true);

    try {
      const response = await fetch(
        `http://localhost:8001/generate_rules/${selectedDoc}`,
        { method: "POST" }
      );

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {

        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split("\n");

        lines.forEach(line => {

    if (!line.trim()) return;

    if (line.startsWith("{")) {

      const parsed = JSON.parse(line);

      if (parsed.type === "rules") {

        setRules(parsed.rules);
        setStatusMessage("");

      }

    } else {

      setStatusMessage(line);

    }

    });

      }
    } catch (error) {
      console.error(error);
      setStatusMessage("Error processing document");
    } finally {
      setIsLoading(false);
    }

  };

  return (
    <div className="flex flex-col h-full bg-gradient-to-br from-slate-50 to-primary-50 p-6 gap-4">

      {/* STATUS OR TABLE */}
      <Card className="flex-1 overflow-hidden shadow-lg border-l-4 border-l-primary-500">
        <CardContent className="h-full p-6 overflow-auto">
          {rules.length === 0 && statusMessage && (
            <div className="flex flex-col items-center justify-center h-full gap-4">
              {isLoading && (
                <Loader className="h-8 w-8 text-primary-600 animate-spin" />
              )}
              <p className="text-lg font-medium text-slate-700">{statusMessage}</p>
            </div>
          )}

          {rules.length === 0 && !statusMessage && (
            <div className="flex flex-col items-center justify-center h-full gap-4 text-slate-500">
              <Sparkles className="h-12 w-12 text-primary-300" />
              <p className="text-center">
                {selectedDoc 
                  ? "Select a guided prompt or enter a custom prompt to generate rules" 
                  : "Select a document to get started"}
              </p>
            </div>
          )}

          {rules.length > 0 && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-slate-800">Generated Rules</h3>
              <div className="border border-slate-200 rounded-lg overflow-hidden">
                <Table>
                  <TableHeader>
                    <TableRow className="bg-slate-100">
                      <TableHead className="font-semibold">Rule ID</TableHead>
                      <TableHead className="font-semibold">Title</TableHead>
                      <TableHead className="font-semibold">Description</TableHead>
                      <TableHead className="font-semibold">Category</TableHead>
                      <TableHead className="font-semibold">Effect</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {rules.map((rule, index) => (
                      <TableRow key={index} className="hover:bg-primary-50">
                        <TableCell className="font-mono text-sm text-primary-600">{rule.rule_id}</TableCell>
                        <TableCell className="font-medium">{rule.title}</TableCell>
                        <TableCell className="text-sm text-slate-600 max-w-xs truncate">{rule.description}</TableCell>
                        <TableCell>
                          <span className="inline-block px-3 py-1 rounded-full text-xs font-medium bg-primary-100 text-primary-700">
                            {rule.action_category}
                          </span>
                        </TableCell>
                        <TableCell>
                          <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${
                            rule.effect === "Allow" 
                              ? "bg-green-100 text-green-700" 
                              : "bg-red-100 text-red-700"
                          }`}>
                            {rule.effect}
                          </span>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* GUIDED PROMPTS */}
      {showGuided && (
        <Card className="shadow-lg border-l-4 border-l-primary-500 animate-in fade-in slide-in-from-bottom-4">
          <CardContent className="p-4">
            <p className="text-sm font-semibold text-slate-600 mb-3">Suggested Prompts:</p>
            <div className="grid grid-cols-1 gap-2">
              {guidedPrompts.map((text, index) => (
                <button
                  key={index}
                  onClick={() => selectGuidedPrompt(text)}
                  className="p-3 text-left text-sm text-slate-700 bg-slate-50 hover:bg-primary-100 border border-slate-200 rounded-lg transition-colors duration-200"
                >
                  ✨ {text}
                </button>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* INPUT WITH ICONS */}
      <Card className="shadow-lg border-l-4 border-l-primary-500">
        <CardContent className="p-4">
          <div className="flex gap-2 items-center">
            <div className="flex-1 relative">
              <Input
                type="text"
                placeholder="Enter your prompt..."
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && !isLoading && prompt.trim() && selectedDoc && handleSubmit()}
                disabled={isLoading}
                className="flex-1 pr-20"
              />
              <div className="absolute right-2 top-1/2 -translate-y-1/2 flex gap-1">
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setShowGuided(!showGuided)}
                  className="text-primary-600 hover:bg-primary-100 h-8 w-8"
                  disabled={isLoading}
                  title="Suggested prompts"
                >
                  <Sparkles className="h-4 w-4" />
                </Button>
                <Button
                  size="icon"
                  onClick={handleSubmit}
                  disabled={!prompt.trim() || isLoading || !selectedDoc}
                  className="h-8 w-8"
                  title="Submit (Enter)"
                >
                  {isLoading ? (
                    <Loader className="h-4 w-4 animate-spin" />
                  ) : (
                    <Send className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

    </div>
  );
}

export default PromptPanel;
