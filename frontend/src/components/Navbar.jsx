import React from "react";
import { User } from "lucide-react";
import { Button } from "./ui/button";

function Navbar() {
  return (
    <nav className="sticky top-0 z-50 w-full border-b border-slate-200 bg-white shadow-sm">
      <div className="flex h-16 items-center justify-between px-6 lg:px-8">
        {/* Logo Section */}
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-primary-400 to-primary-600 text-white font-bold text-lg">
            Q
          </div>
          <div className="flex flex-col">
            <h1 className="text-lg font-bold text-primary-700">Questkart</h1>
            <p className="text-xs text-slate-500">Compliance & Governance</p>
          </div>
        </div>

        {/* Title */}
        <div className="flex-1 text-center">
          <h2 className="text-xl font-semibold text-slate-800">
            Contract Compliance & Data Governance
          </h2>
        </div>

        {/* User Icon */}
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="icon"
            className="rounded-full bg-slate-100 hover:bg-slate-200"
          >
            <User className="h-5 w-5 text-primary-600" />
          </Button>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
