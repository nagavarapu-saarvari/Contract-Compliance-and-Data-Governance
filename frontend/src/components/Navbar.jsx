import React from "react";
import { User } from "lucide-react";
import { Button } from "./ui/button";
import logo from "../assets/questkart-logo.png";

function Navbar() {
  return (
    <nav className="fixed top-0 left-0 w-full z-50 border-b border-slate-200 bg-white shadow-sm">
      <div className="flex h-16 items-center justify-between px-6 lg:px-8">

        {/* Logo Section */}
        <div className="flex items-center gap-3">

          <img
            src={logo}
            alt="Questkart Logo"
            className="h-10 w-auto object-contain"
          />

        </div>

        {/* Center Title */}
        <div className="flex-1 text-center">
          <h2 className="text-xl font-bold">
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
            <User className="h-5 w-5 text-primary-400" />
          </Button>
        </div>

      </div>
    </nav>
  );
}

export default Navbar;