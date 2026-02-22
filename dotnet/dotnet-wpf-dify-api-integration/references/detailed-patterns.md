# Detailed Patterns — dotnet-wpf-dify-api-integration

Overflow content from [SKILL.md](../SKILL.md). Keep this file in sync with the main skill.

---

## SSE Stream Reader

Full implementation of `ReadSseStreamAsync` — parses Server-Sent Events from Dify's `/v1/workflows/run` endpoint and routes each event type to `IProgress<string>`.

```csharp
private async Task<string> ReadSseStreamAsync(
    HttpResponseMessage response, IProgress<string>? progress)
{
    using var reader = new StreamReader(await response.Content.ReadAsStreamAsync());
    string? result = null;

    while (!reader.EndOfStream)
    {
        var line = await reader.ReadLineAsync();
        if (string.IsNullOrWhiteSpace(line) || !line.StartsWith("data:")) continue;

        try
        {
            using var doc = JsonDocument.Parse(line[5..].Trim());
            var evt = doc.RootElement.GetProperty("event").GetString();
            switch (evt)
            {
                case "workflow_started":
                    progress?.Report("▶️ Workflow started"); break;
                case "node_started":
                    var title = doc.RootElement.GetProperty("data")
                        .GetProperty("title").GetString();
                    progress?.Report($"🔄 {title} running..."); break;
                case "node_finished":
                    var d = doc.RootElement.GetProperty("data");
                    var s = d.GetProperty("status").GetString();
                    var t = d.GetProperty("title").GetString();
                    progress?.Report(s == "succeeded" ? $"✅ {t} done" : $"❌ {t} failed");
                    break;
                case "workflow_finished":
                    result = doc.RootElement.GetProperty("data")
                        .GetProperty("outputs").GetRawText();
                    progress?.Report("✅ Workflow complete"); break;
            }
        }
        catch (JsonException) { continue; } // Skip malformed SSE lines
    }
    return result ?? throw new InvalidOperationException("No workflow output received.");
}
```

### Event Types

| Event | Action | Progress Message |
|-------|--------|-----------------|
| `workflow_started` | Log start | `▶️ Workflow started` |
| `node_started` | Show node title | `🔄 {title} running...` |
| `node_finished` | Show success/fail | `✅ {title} done` or `❌ {title} failed` |
| `workflow_finished` | Extract outputs | `✅ Workflow complete` |

### Key Design Decisions

- **`line[5..].Trim()`** — Strips the `data:` prefix from SSE lines before JSON parsing.
- **`catch (JsonException) { continue; }`** — Malformed SSE lines (heartbeats, partial data) are silently skipped.
- **`ResponseHeadersRead`** — Set on the calling method to avoid buffering the entire stream in memory.
- **`throw new InvalidOperationException`** — If no `workflow_finished` event arrives, the caller gets an explicit error rather than a null result.
