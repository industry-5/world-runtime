import { bootstrapStudioApp } from "./app/bootstrap.js";

function main() {
  const root = document.getElementById("app");
  if (!root) {
    throw new Error("Missing #app root element");
  }
  bootstrapStudioApp(root);
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", main, { once: true });
} else {
  main();
}
