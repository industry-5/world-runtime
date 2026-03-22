export function createRuntimeClient(basePath = "/api/v1/runtime/call") {
  async function postJson(path, payload) {
    const response = await fetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    let body = null;
    try {
      body = await response.json();
    } catch (error) {
      throw new Error(`Runtime returned non-JSON response (${response.status})`);
    }

    if (!response.ok || body?.ok === false) {
      const message = body?.error?.message || body?.error || `HTTP ${response.status}`;
      throw new Error(String(message));
    }

    return body;
  }

  async function callRuntimeMethod(method, params = {}) {
    const payload = { method, params };
    const response = await postJson(basePath, payload);
    return response.result;
  }

  return {
    callRuntimeMethod,
  };
}
