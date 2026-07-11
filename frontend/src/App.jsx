import React from "react";
import InteractionForm from "./components/InteractionForm";
import ChatPanel from "./components/ChatPanel";

// Split-screen layout: read-only form (~65%) + AI chat (~35%) — BRD 8.1.
export default function App() {
  return (
    <>
      <div className="page-accent" />
      <div className="split">
        <section className="left-panel">
          <InteractionForm />
        </section>
        <section className="right-panel">
          <ChatPanel />
        </section>
      </div>
    </>
  );
}
