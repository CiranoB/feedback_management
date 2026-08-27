const AUTH_TOKEN_STORAGE_KEY = "feedback_auth_token";
const authTokenInput = document.querySelector("#auth-token-input");

function getAuthToken() {
  return authTokenInput ? authTokenInput.value : "";
}

// Only write requests (POST/PATCH/...) need this header; viewing stays open.
function authHeaders(extraHeaders = {}) {
  return { ...extraHeaders, "X-API-Key": getAuthToken() };
}

if (authTokenInput) {
  authTokenInput.value = localStorage.getItem(AUTH_TOKEN_STORAGE_KEY) || "";
  authTokenInput.addEventListener("input", () => {
    localStorage.setItem(AUTH_TOKEN_STORAGE_KEY, authTokenInput.value);
  });
}
