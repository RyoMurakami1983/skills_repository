# Detailed Patterns — Playwright + Blazor

Supplementary code examples for `dotnet-playwright-blazor`.
See [../SKILL.md](../SKILL.md) for the main workflow.

## Cookie-Based Authentication (Faster Login)

```csharp
[Fact]
public async Task AuthenticatedAccess_ViaCookie()
{
    var page = await _fixture.Browser.NewPageAsync();

    // Inject authentication cookie to skip login UI
    await page.Context.AddCookiesAsync(new[]
    {
        new Cookie
        {
            Name = ".AspNetCore.Cookies",
            Value = GenerateAuthCookie("alice"),
            Url = baseUrl,
            Secure = true,
            HttpOnly = true
        }
    });

    await page.GotoAsync($"{baseUrl}/dashboard");

    var username = await page.TextContentAsync("[data-test='user-name']");
    Assert.Equal("alice", username);
}

private string GenerateAuthCookie(string username)
{
    // Generate a valid authentication cookie
    // Requires access to your app's cookie encryption keys
    // OR use a test endpoint that generates valid cookies
    // OR perform actual login once and reuse the cookie
}
```

## OAuth / External Provider Mocking

```csharp
// Intercept OAuth redirect and return mock response
await page.RouteAsync("**/signin-microsoft", async route =>
{
    await route.FulfillAsync(new()
    {
        Status = 302,
        Headers = new Dictionary<string, string>
        {
            ["Location"] = $"{baseUrl}/signin-callback?code=mock_auth_code"
        }
    });
});
```

## Testing Real-Time Updates (SignalR)

Blazor Server uses SignalR for real-time communication:

```csharp
[Fact]
public async Task RealTimeUpdates()
{
    // Open two browser contexts (simulating two users)
    var page1 = await _fixture.Browser.NewPageAsync();
    var page2 = await _fixture.Browser.NewPageAsync();

    await page1.GotoAsync($"{baseUrl}/drawing");
    await page2.GotoAsync($"{baseUrl}/drawing");

    // User 1 draws something
    await page1.ClickAsync("[data-test='draw-button']");
    await page1.Mouse.ClickAsync(100, 100);

    // User 2 should see the update
    await page2.WaitForSelectorAsync("[data-test='drawing-canvas']");

    var canvas1 = await page1.GetByTestId("drawing-canvas")
        .GetAttributeAsync("data-strokes");
    var canvas2 = await page2.GetByTestId("drawing-canvas")
        .GetAttributeAsync("data-strokes");

    Assert.Equal(canvas1, canvas2);
}
```

## Screenshot and Visual Testing

```csharp
[Fact]
public async Task CaptureScreenshots()
{
    var page = await _fixture.Browser.NewPageAsync();
    await page.GotoAsync(baseUrl);

    // Full page screenshot
    await page.ScreenshotAsync(new()
    {
        Path = "screenshots/homepage.png",
        FullPage = true
    });

    // Element screenshot
    var header = page.Locator("header");
    await header.ScreenshotAsync(new()
    {
        Path = "screenshots/header.png"
    });

    // Desktop viewport
    await page.SetViewportSizeAsync(1920, 1080);
    await page.ScreenshotAsync(new()
    {
        Path = "screenshots/desktop.png"
    });

    // Mobile viewport
    await page.SetViewportSizeAsync(375, 667);
    await page.ScreenshotAsync(new()
    {
        Path = "screenshots/mobile.png"
    });
}
```

## Click and Touch Interactions

```csharp
[Fact]
public async Task ClickInteractions()
{
    var page = await _fixture.Browser.NewPageAsync();
    await page.GotoAsync(baseUrl);

    // Right-click
    await page.ClickAsync("[data-test='context-menu']", new()
    {
        Button = MouseButton.Right
    });

    // Double-click
    await page.DblClickAsync("[data-test='item']");

    // Hover then click dropdown
    var menu = page.Locator("#profile-menu");
    await menu.HoverAsync();
    await menu.GetByText("Sign out").ClickAsync();

    // Touch events (mobile emulation)
    await page.EmulateMediaAsync(new() { Media = Media.Screen });
    await page.Touchscreen.TapAsync(150, 300);
}
```

## Custom Wait Helpers

```csharp
public static class PlaywrightExtensions
{
    public static async Task WaitForBlazorAsync(this IPage page)
    {
        // Wait for Blazor runtime to finish initializing
        await page.EvaluateAsync(@"
            () => new Promise(resolve => {
                if (typeof Blazor !== 'undefined') {
                    resolve();
                } else {
                    const interval = setInterval(() => {
                        if (typeof Blazor !== 'undefined') {
                            clearInterval(interval);
                            resolve();
                        }
                    }, 100);
                }
            })
        ");
    }

    public static async Task WaitForNoSpinnersAsync(
        this IPage page,
        int timeout = 5000)
    {
        var locator = page.Locator(".spinner, .loading");
        await locator.WaitForAsync(new()
        {
            State = WaitForSelectorState.Hidden,
            Timeout = timeout
        });
    }

    public static async Task FillWithValidationAsync(
        this IPage page,
        string selector,
        string value)
    {
        await page.FillAsync(selector, value);

        // Trigger blur to activate Blazor's EditForm validation
        await page.Locator(selector).BlurAsync();
        await Task.Delay(100);
    }
}
```

## HTTPS with Dev Certificates

```csharp
public async Task InitializeAsync()
{
    _playwright = await Playwright.CreateAsync();

    _browser = await _playwright.Chromium.LaunchAsync(new()
    {
        Headless = true,
        // Ignore certificate errors for local dev certs
        Args = new[] { "--ignore-certificate-errors" }
    });
}
```

Export and trust the dev certificate for stricter setups:

```bash
dotnet dev-certs https --export-path cert.pfx -p YourPassword
```

## Parallelization Considerations

Blazor Server uses SignalR websockets. Multiple Playwright tests can saturate connections:

```csharp
// Limit parallel execution for Blazor Server tests
[Collection("Blazor Server")]
public class BlazorServerTests { }

// In AssemblyInfo.cs or test startup
[assembly: CollectionBehavior(MaxParallelThreads = 2)]
```

Blazor WebAssembly doesn't have this limitation and can run fully parallel.
