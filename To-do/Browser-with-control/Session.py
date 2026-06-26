# Browser task with session control
browser_task = anchor_client.agent.browser_task(
    "go to github.com/trending and find the most popular JavaScript repository"
)

print("Session ID:", browser_task["session_id"])

# Access the Playwright browser instance
playwright_browser = browser_task["playwright_browser"]
with playwright_browser as browser:
    page = browser.contexts[0].pages[0]

    # Direct Playwright manipulation
    page.goto("https://stackoverflow.com/")
    print("Current URL:", page.url)

    # Wait for task completion
    task_result = browser_task["task_result_task"]
    print("Final result:", task_result)
