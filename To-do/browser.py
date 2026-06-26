# Create standalone browser
with anchor_client.browser.create() as standalone_browser:
    page = standalone_browser.contexts[0].pages[0]
    page.goto("https://httpbin.org/ip")
    print("Current URL:", page.url)
