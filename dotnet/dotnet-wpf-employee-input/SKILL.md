---
name: dotnet-wpf-employee-input
description: >
  Add employee number (社員番号) input dialog to WPF apps with DPAPI-encrypted storage.
  Use when: building employee ID configuration.
license: MIT
metadata:
  author: RyoMurakami1983
  tags: [dotnet, wpf, csharp, mvvm, employee, dpapi, configuration]
  invocable: false
---

# Add Employee Number Input Dialog to WPF Applications

End-to-end workflow for adding an employee number (社員番号) input dialog to .NET WPF applications: 4-digit validation, DPAPI-encrypted storage via `SecureConfigService`, MVVM settings UI, and menu bar integration.

## When to Use This Skill

Use this skill when:
- Adding an employee number configuration dialog to a WPF application
- Storing employee IDs securely with DPAPI encryption (not plaintext)
- Building a settings dialog that validates fixed-length numeric input
- Providing a user-facing UI to set, update, and reset employee numbers
- Integrating employee identification into Dify API calls or other services

---

## Related Skills

- **`dotnet-wpf-secure-config`** — Required: DPAPI encryption foundation (apply first)
- **`dotnet-wpf-dify-api-integration`** — Uses employee number as `user` field in Dify API calls
- **`dotnet-oracle-wpf-integration`** — Shares SecureConfigService when used in the same app
- **`tdd-standard-practice`** — Test generated code with Red-Green-Refactor
- **`git-commit-practices`** — Commit each step as an atomic change

---

## Core Principles

1. **Security by Default** — Employee numbers stored via DPAPI; never in plaintext settings files (ニュートラル)
2. **MVVM Discipline** — ViewModel drives all save/load/reset logic; minimal code-behind (基礎と型)
3. **Validate Before Persist** — Format validation happens in ViewModel before calling SecureConfigService (基礎と型)
4. **Progressive Integration** — Prerequisites → ViewModel → View → Wiring → Menu, one layer at a time (継続は力)
5. **Reusable Pattern** — Dialog pattern applies to any single-field secure config input (成長の複利)

---

## Workflow: Add Employee Number Dialog to WPF

### Step 1 — Set Up Prerequisites

Use when adding employee number files to a project that already has `dotnet-wpf-secure-config` applied.

**Prerequisites** (must be completed first):
- `dotnet-wpf-secure-config` skill applied
- `Infrastructure/Configuration/` folder exists with:
  - `DpapiEncryptor.cs`
  - `SecureConfigService.cs`
  - `ISecureConfigService.cs`
  - `AppConfigModel.cs`

**Files to add** (employee-number-specific):

```
Presentation/
├── ViewModels/
│   └── EmployeeNumberConfigViewModel.cs  🆕
└── Views/
    ├── EmployeeNumberConfigDialog.xaml    🆕
    └── EmployeeNumberConfigDialog.xaml.cs 🆕
```

**NuGet packages** (if not already installed):

```powershell
Install-Package CommunityToolkit.Mvvm
Install-Package Microsoft.Extensions.DependencyInjection
```

> **Values**: 基礎と型 / 成長の複利

### Step 2 — Create ViewModel

Use when implementing the employee number input logic with validation, save, and reset.

Create `EmployeeNumberConfigViewModel` with format validation, load on open, save, and reset functionality. The ViewModel delegates all persistence to `ISecureConfigService`.

**EmployeeNumberConfigViewModel.cs**:

```csharp
public partial class EmployeeNumberConfigViewModel : ObservableObject
{
    private readonly ISecureConfigService _configService;

    [ObservableProperty] private string employeeNumber = string.Empty;
    [ObservableProperty] private string statusMessage = string.Empty;

    public EmployeeNumberConfigViewModel(ISecureConfigService configService)
        => _configService = configService;

    public async Task LoadConfigAsync()
    {
        var config = await _configService.LoadDifyConfigAsync();
        EmployeeNumber = config.EmployeeNumber;
        StatusMessage = "Settings loaded.";
    }

    [RelayCommand]
    private async Task SaveAsync()
    {
        // ✅ Validate format before persisting
        if (!IsValidEmployeeNumber(EmployeeNumber))
        { StatusMessage = "Enter a 4-digit employee number."; return; }

        var config = await _configService.LoadDifyConfigAsync();
        config.EmployeeNumber = EmployeeNumber.Trim();
        await _configService.SaveDifyConfigAsync(config);
        StatusMessage = "Saved.";
    }

    [RelayCommand]
    private async Task ResetAsync()
    {
        var config = await _configService.LoadDifyConfigAsync();
        config.EmployeeNumber = string.Empty;
        await _configService.SaveDifyConfigAsync(config);
        EmployeeNumber = string.Empty;
        StatusMessage = "Reset complete.";
    }

    /// <summary>
    /// Validates employee number format: exactly 4 digits.
    /// </summary>
    private static bool IsValidEmployeeNumber(string number)
        => !string.IsNullOrWhiteSpace(number)
        && number.Trim().Length == 4
        && number.Trim().All(char.IsDigit);
}
```

**Why validate in ViewModel**: Keeps View free of logic; validation is testable without a running WPF window. The `IsValidEmployeeNumber` method is `static` so it can be unit-tested in isolation.

> **Values**: 基礎と型 / ニュートラル

### Step 3 — Create XAML Dialog

Use when building the WPF window for employee number entry.

Create a compact modal dialog with input field, status message, and action buttons. All controls bind to ViewModel properties — no `x:Name` manipulation.

**EmployeeNumberConfigDialog.xaml**:

```xml
<Window Title="Employee Number Settings"
        Height="260" Width="420"
        WindowStartupLocation="CenterOwner"
        ResizeMode="NoResize"
        Loaded="Window_Loaded">
    <Grid Margin="20">
        <Grid.RowDefinitions>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="*"/>
            <RowDefinition Height="Auto"/>
        </Grid.RowDefinitions>

        <!-- Header -->
        <TextBlock Text="Employee Number"
                   FontSize="16" FontWeight="Bold"/>

        <!-- Input -->
        <StackPanel Grid.Row="1" Margin="0,10,0,0">
            <TextBlock Text="Employee Number *"/>
            <TextBox Text="{Binding EmployeeNumber, UpdateSourceTrigger=PropertyChanged}"
                     Margin="0,4,0,0"/>
            <TextBlock Text="Enter 4-digit number"
                       Foreground="Gray" FontSize="10" Margin="0,2,0,0"/>
        </StackPanel>

        <!-- Status -->
        <TextBlock Grid.Row="2"
                   Text="{Binding StatusMessage}"
                   Foreground="Blue"
                   VerticalAlignment="Bottom" Margin="0,0,0,8"/>

        <!-- Actions -->
        <StackPanel Grid.Row="3" Orientation="Horizontal"
                    HorizontalAlignment="Right">
            <Button Content="Save"
                    Command="{Binding SaveCommand}"
                    Margin="0,0,8,0" Padding="16,4"/>
            <Button Content="Reset"
                    Command="{Binding ResetCommand}"
                    Margin="0,0,8,0" Padding="16,4"/>
            <Button Content="Close"
                    Click="Close_Click"
                    Padding="16,4"/>
        </StackPanel>
    </Grid>
</Window>
```

**Why `UpdateSourceTrigger=PropertyChanged`**: Without it, WPF updates the binding only on focus loss. Real-time validation requires character-by-character updates to the ViewModel.

> **Values**: 基礎と型 / 成長の複利

### Step 4 — Wire Code-Behind

Use when connecting the dialog window to the ViewModel with minimal code-behind.

Code-behind handles only two things: loading config on `Window_Loaded` and closing the window. All business logic stays in the ViewModel.

**EmployeeNumberConfigDialog.xaml.cs**:

```csharp
public partial class EmployeeNumberConfigDialog : Window
{
    public EmployeeNumberConfigDialog(EmployeeNumberConfigViewModel viewModel)
    {
        InitializeComponent();
        DataContext = viewModel;
    }

    private async void Window_Loaded(object sender, RoutedEventArgs e)
        => await ((EmployeeNumberConfigViewModel)DataContext).LoadConfigAsync();

    private void Close_Click(object sender, RoutedEventArgs e)
        => Close();
}
```

**Why `Window_Loaded` for config load**: Loading in the constructor blocks the UI thread and delays window rendering. `Window_Loaded` fires after the window is displayed, allowing async load without visual delay.

> **Values**: 基礎と型 / 継続は力

### Step 5 — Integrate with Menu Bar

Use when adding a menu item to launch the employee number dialog from MainWindow.

Register the ViewModel in DI and launch the dialog from a menu command.

**App.xaml.cs** — Add DI registration:

```csharp
// App.xaml.cs — add to OnStartup
services.AddTransient<EmployeeNumberConfigViewModel>();
```

**MainWindow menu** — Add menu item:

```xml
<MenuItem Header="Settings">
    <MenuItem Header="Employee Number..."
              Command="{Binding OpenEmployeeNumberConfigCommand}"/>
</MenuItem>
```

**MainViewModel** — Add launch command:

```csharp
[RelayCommand]
private void OpenEmployeeNumberConfig()
{
    var vm = _serviceProvider.GetRequiredService<EmployeeNumberConfigViewModel>();
    new EmployeeNumberConfigDialog(vm) { Owner = Application.Current.MainWindow }
        .ShowDialog();
}
```

> **Values**: 成長の複利 / 継続は力

### Step 6 — Customize for Your Application

Use when adapting the employee number format to your organization's requirements.

⚠️ **Ask the user** what digit count and validation rules to use for their employee ID format.

Replace these defaults based on organizational requirements:

| Item | File | Default | What to Change |
|------|------|---------|----------------|
| Digit count | `IsValidEmployeeNumber` | 4 digits | Adjust `Length == 4` to match format |
| Validation rules | `IsValidEmployeeNumber` | Digits only | Add prefix/suffix rules if needed |
| Storage location | `DifyConfigModel` | `EmployeeNumber` property | Change property name if needed |
| Field label | `Dialog.xaml` | "Employee Number" | Localize or rename |
| Window title | `Dialog.xaml` | "Employee Number Settings" | Match your app's naming |

**Customization examples**:

```csharp
// 6-digit employee number
private static bool IsValidEmployeeNumber(string number)
    => !string.IsNullOrWhiteSpace(number)
    && number.Trim().Length == 6
    && number.Trim().All(char.IsDigit);

// Alphanumeric with prefix (e.g., "EMP-1234")
private static bool IsValidEmployeeNumber(string number)
    => !string.IsNullOrWhiteSpace(number)
    && Regex.IsMatch(number.Trim(), @"^EMP-\d{4}$");
```

> **Values**: ニュートラル / 基礎と型

---

## Good Practices

### 1. Validate Format Before Saving

**What**: Check digit count and character type in the ViewModel before calling `SaveDifyConfigAsync`.

**Why**: Prevents invalid data from reaching the config file; provides immediate user feedback.

**Values**: 基礎と型（バリデーションを型として定着）

### 2. Load Existing Value on Dialog Open

**What**: Call `LoadConfigAsync()` in `Window_Loaded` to populate the TextBox with the saved value.

**Why**: Users see their current setting and can verify or update it; avoids blank-field confusion.

**Values**: 継続は力（既存設定の継続性を保つ）

### 3. Provide Reset Functionality

**What**: Include a Reset button that clears the stored value via `SecureConfigService`.

**Why**: Users can remove their employee number without manually editing config files.

**Values**: ニュートラル（安全なリセット手段を標準提供）

---

## Common Pitfalls

### 1. Not Loading Config on Window_Loaded

**Problem**: Dialog opens with an empty TextBox even though a value is already saved.

**Solution**: Always call `LoadConfigAsync()` in the `Window_Loaded` event, not in the constructor.

```csharp
// ❌ WRONG — Blocks UI thread, may miss async completion
public EmployeeNumberConfigDialog(EmployeeNumberConfigViewModel vm)
{
    InitializeComponent();
    DataContext = vm;
    vm.LoadConfigAsync().Wait(); // Deadlock risk
}

// ✅ CORRECT — Async load after window renders
private async void Window_Loaded(object sender, RoutedEventArgs e)
    => await ((EmployeeNumberConfigViewModel)DataContext).LoadConfigAsync();
```

### 2. Missing UpdateSourceTrigger=PropertyChanged

**Problem**: Validation only triggers when the TextBox loses focus, not on each keystroke.

**Solution**: Set `UpdateSourceTrigger=PropertyChanged` on the `TextBox` binding.

```xml
<!-- ❌ WRONG — Updates only on LostFocus -->
<TextBox Text="{Binding EmployeeNumber}"/>

<!-- ✅ CORRECT — Updates on every keystroke -->
<TextBox Text="{Binding EmployeeNumber, UpdateSourceTrigger=PropertyChanged}"/>
```

### 3. Forgetting to Persist via SecureConfigService

**Problem**: Updating the ViewModel property but not saving to `config.json`.

**Solution**: Always call `SaveDifyConfigAsync()` after modifying the config model.

```csharp
// ❌ WRONG — Property updated but not persisted
EmployeeNumber = "1234";

// ✅ CORRECT — Persist through SecureConfigService
var config = await _configService.LoadDifyConfigAsync();
config.EmployeeNumber = EmployeeNumber.Trim();
await _configService.SaveDifyConfigAsync(config);
```

---

## Anti-Patterns

### Storing Employee Number in Plaintext Settings File

**What**: Writing the employee number to `appsettings.json` or a custom `.txt` file.

**Why It's Wrong**: Plaintext files are readable by anyone with filesystem access; no encryption at rest.

**Better Approach**: Use `SecureConfigService` with DPAPI encryption to store in `%LOCALAPPDATA%`.

### Using Code-Behind for Save Logic

**What**: Putting save/validate/reset logic directly in `.xaml.cs` event handlers.

**Why It's Wrong**: Untestable without a running WPF window; violates MVVM separation; logic scattered across files.

**Better Approach**: Delegate all logic to ViewModel via `[RelayCommand]` and data binding. Code-behind handles only `Window_Loaded` and `Close_Click`.

---

## Quick Reference

### Implementation Checklist

- [ ] `dotnet-wpf-secure-config` skill applied (prerequisite)
- [ ] `AppConfigModel` has `EmployeeNumber` field (via `DifyConfigModel` or dedicated model)
- [ ] Create `EmployeeNumberConfigViewModel.cs` with Load / Save / Reset (Step 2)
- [ ] Create `EmployeeNumberConfigDialog.xaml` with bound controls (Step 3)
- [ ] Create `EmployeeNumberConfigDialog.xaml.cs` with minimal code-behind (Step 4)
- [ ] Register ViewModel in DI container (Step 5)
- [ ] Add menu item to launch dialog (Step 5)
- [ ] Customize digit count and validation for your format (Step 6)
- [ ] Test: save → close → reopen → verify value loads
- [ ] Test: enter invalid input → verify error message appears
- [ ] Test: reset → verify value cleared in both UI and config file

### Validation Decision Table

| Format | Validation Rule | Example |
|--------|----------------|---------|
| 4-digit numeric | `Length == 4 && All(IsDigit)` | `1234` |
| 6-digit numeric | `Length == 6 && All(IsDigit)` | `001234` |
| Alphanumeric prefix | `Regex(@"^EMP-\d{4}$")` | `EMP-1234` |
| Free-form | `!IsNullOrWhiteSpace` | Any non-empty string |

---

## Resources

- `dotnet-wpf-secure-config` — DPAPI encryption foundation used by this skill
- `dotnet-wpf-dify-api-integration` — Uses employee number as Dify API `user` field
- [CommunityToolkit.Mvvm Docs](https://learn.microsoft.com/en-us/dotnet/communitytoolkit/mvvm/)
- [Microsoft: Data Protection API (DPAPI)](https://docs.microsoft.com/windows/win32/seccng/data-protection-api)

---

## Changelog

### Version 1.0.0 (2026-02-15)
- Initial release: employee number input dialog skill
- 6-step workflow: Prerequisites → ViewModel → XAML → Code-Behind → Menu → Customize
- DPAPI-encrypted storage via SecureConfigService
- 4-digit validation with customization guidance
- MVVM pattern with CommunityToolkit.Mvvm

<!--
Japanese version available at references/SKILL.ja.md
日本語版は references/SKILL.ja.md を参照してください
-->
