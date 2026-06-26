// Create session and connect it later
const sessionResponse = await anchorClient.sessions.create();
const sessionId = sessionResponse.data.id;

const browser = await anchorClient.browser.connect(sessionId);
const context = browser.contexts()[0];
const page = context.pages()[0];
await page.goto("https://reddit.com/r/programming");

console.log("Current URL:", page.url());

browser.close();
