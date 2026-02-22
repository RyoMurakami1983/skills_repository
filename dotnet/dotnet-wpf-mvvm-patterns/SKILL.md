---
name: dotnet-wpf-mvvm-patterns
description: >
  Build WPF applications using CommunityToolkit.Mvvm with proper MVVM separation,
  commanding, validation, and dialog patterns.
  Use when implementing new WPF views or refactoring code-behind into ViewModel-first architecture.
metadata:
  author: RyoMurakami1983
  tags: [wpf, mvvm, csharp, communitytoolkit, xaml, dotnet]
  invocable: false
---

# WPF MVVM Patterns

A workflow for building WPF applications with clean MVVM architecture using CommunityToolkit.Mvvm. Covers the fundamental patterns that every WPF module needs: observable properties, commanding, validation, and ViewModel composition.

## When to Use This Skill

Use this skill when:
- Creating a new WPF view with ViewModel-first architecture
- Refactoring code-behind logic into proper MVVM separation
- Implementing async commands with CanExecute gating
- Adding field-level validation to WPF forms
- Composing parent-child ViewModel hierarchies
- Needing MVVM-compliant dialog return patterns

Do **not** use when:
- Building console or Web API applications (no XAML involved)
- Working with Blazor or MAUI (different UI frameworks)
- The view is purely static with no user interaction

## Related Skills

- **`dotnet-wpf-secure-config`** — Config dialog using MVVM patterns from this skill
- **`dotnet-wpf-employee-input`** — Single-field dialog applying validation patterns
- **`dotnet-wpf-dify-api-integration`** — API client with async commanding
- **`dotnet-oracle-wpf-integration`** — Repository pattern with MVVM settings UI

---

## Dependencies

- .NET 8+ (or .NET 9)
- CommunityToolkit.Mvvm 8.x (`dotnet add package CommunityToolkit.Mvvm`)
- Microsoft.Extensions.DependencyInjection (for DI registration)

---

## Core Principles

1. **ViewModel owns all state** — Views bind to ViewModel properties; no business logic in code-behind (基礎と型)
2. **Commands replace event handlers** — Every button click is a `[RelayCommand]`, never a `Click="Button_Click"` (基礎と型)
3. **Validation is declarative** — Use `ObservableValidator` with data annotations, not ad-hoc string checks (ニュートラルな視点)
4. **Composition over inheritance** — Build complex screens from small, focused ViewModels (成長の複利)
5. **Async by default** — All I/O-bound commands use `[RelayCommand]` on `async Task` methods (継続は力)

---

## Workflow: Implement MVVM in a WPF Module

### Step 1: Set Up the ViewModel Base

Create a ViewModel class using CommunityToolkit.Mvvm source generators. This is the foundation for all subsequent steps.

Use when starting a new WPF view or converting existing code-behind to MVVM.

> **Values**: 基礎と型 — The `[ObservableProperty]` and `[RelayCommand]` attributes eliminate boilerplate while enforcing correct patterns.

```csharp
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

namespace MyApp.ViewModels;

public partial class CustomerViewModel : ObservableObject
{
    [ObservableProperty]
    private string _name = string.Empty;

    [ObservableProperty]
    private string _email = string.Empty;

    // Generated: public string Name { get; set; } with PropertyChanged
    // Generated: public string Email { get; set; } with PropertyChanged

    // React to property changes
    partial void OnNameChanged(string value)
    {
        // Runs after Name is set — update dependent state here
        SaveCommand.NotifyCanExecuteChanged();
    }
}
```

**Key rules:**
- Inherit from `ObservableObject` (no validation) or `ObservableValidator` (with validation)
- Use `[ObservableProperty]` on private fields — the generator creates public properties
- Field naming: `_camelCase` → generates `PascalCase` property
- Use `partial void OnXxxChanged()` for side effects, never manual `PropertyChanged` raising

### Step 2: Add Commands

Replace all event handlers with commands. Sync commands use `[RelayCommand]`, async commands use `[RelayCommand]` on `async Task` methods.

Use when the view has buttons, menu items, or any user-triggered actions.

> **Values**: 温故知新 — The ICommand pattern has been the backbone of MVVM since WPF's inception. CommunityToolkit modernizes the implementation while preserving the principle.

```csharp
public partial class CustomerViewModel : ObservableObject
{
    [ObservableProperty]
    private string _name = string.Empty;

    [ObservableProperty]
    private bool _isBusy;

    // Sync command with CanExecute
    [RelayCommand(CanExecute = nameof(CanSave))]
    private void Save()
    {
        // Save logic here
    }

    private bool CanSave() => !string.IsNullOrWhiteSpace(Name);

    // Async command — automatically sets IsBusy-like behavior
    [RelayCommand]
    private async Task LoadDataAsync(CancellationToken token)
    {
        IsBusy = true;
        try
        {
            // Async I/O here
            await Task.Delay(1000, token);
        }
        finally
        {
            IsBusy = false;
        }
    }
}
```

**XAML binding:**

```xml
<Button Content="Save"
        Command="{Binding SaveCommand}"
        IsEnabled="{Binding SaveCommand.CanBeBoundTo, FallbackValue=True}" />

<Button Content="Load"
        Command="{Binding LoadDataCommand}" />

<!-- Show spinner while loading -->
<ProgressBar IsIndeterminate="True"
             Visibility="{Binding IsBusy, Converter={StaticResource BoolToVisibility}}" />
```

**Key rules:**
- `[RelayCommand]` on `private void Xxx()` → generates `XxxCommand`
- `[RelayCommand]` on `private async Task XxxAsync()` → generates `XxxCommand` (drop the Async suffix)
- `CanExecute` references a `bool`-returning method — call `XxxCommand.NotifyCanExecuteChanged()` when conditions change
- Async commands automatically prevent double-execution while running

### Step 3: Add Validation

Use `ObservableValidator` with data annotations for field-level validation. This integrates with WPF's `INotifyDataErrorInfo`.

Use when the view has input fields that need validation before saving.

> **Values**: ニュートラルな視点 — Declarative validation rules are objective and testable. They remove subjective ad-hoc checks from code-behind.

```csharp
using System.ComponentModel.DataAnnotations;

public partial class CustomerViewModel : ObservableValidator
{
    [ObservableProperty]
    [NotifyDataErrorInfo]
    [Required(ErrorMessage = "Name is required.")]
    [MinLength(2, ErrorMessage = "Name must be at least 2 characters.")]
    private string _name = string.Empty;

    [ObservableProperty]
    [NotifyDataErrorInfo]
    [EmailAddress(ErrorMessage = "Invalid email format.")]
    private string _email = string.Empty;

    [RelayCommand(CanExecute = nameof(CanSave))]
    private void Save()
    {
        ValidateAllProperties();
        if (HasErrors) return;

        // Proceed with save
    }

    private bool CanSave() => !HasErrors && !string.IsNullOrWhiteSpace(Name);
}
```

**XAML with validation display:**

```xml
<TextBox Text="{Binding Name, UpdateSourceTrigger=PropertyChanged,
                ValidatesOnDataErrors=True}" />

<!-- Show validation errors -->
<TextBlock Text="{Binding (Validation.Errors)[0].ErrorContent,
                  ElementName=NameTextBox}"
           Foreground="Red"
           Visibility="{Binding (Validation.HasError),
                        ElementName=NameTextBox,
                        Converter={StaticResource BoolToVisibility}}" />
```

**Key rules:**
- Inherit from `ObservableValidator` instead of `ObservableObject`
- Add `[NotifyDataErrorInfo]` alongside `[ObservableProperty]` for validated fields
- Call `ValidateAllProperties()` before save operations
- Check `HasErrors` in `CanExecute` methods

### Step 4: Register with Dependency Injection

Register ViewModels and Views in the DI container. Use constructor injection for services.

Use when the application uses `Microsoft.Extensions.DependencyInjection` (recommended for all non-trivial apps).

> **Values**: 成長の複利 — DI enables testable ViewModels and swappable implementations. The investment pays dividends across the entire application lifecycle.

```csharp
// App.xaml.cs
public partial class App : Application
{
    private readonly IServiceProvider _serviceProvider;

    public App()
    {
        var services = new ServiceCollection();

        // Register services
        services.AddSingleton<ICustomerRepository, CustomerRepository>();
        services.AddSingleton<IDialogService, DialogService>();

        // Register ViewModels
        services.AddTransient<CustomerViewModel>();
        services.AddTransient<MainViewModel>();

        // Register Views
        services.AddTransient<MainWindow>();

        _serviceProvider = services.BuildServiceProvider();
    }

    protected override void OnStartup(StartupEventArgs e)
    {
        var mainWindow = _serviceProvider.GetRequiredService<MainWindow>();
        mainWindow.Show();
    }
}
```

```csharp
// ViewModel with injected dependencies
public partial class CustomerViewModel : ObservableObject
{
    private readonly ICustomerRepository _repository;

    public CustomerViewModel(ICustomerRepository repository)
    {
        _repository = repository;
    }

    [RelayCommand]
    private async Task LoadAsync(CancellationToken token)
    {
        var customers = await _repository.GetAllAsync(token);
        // ...
    }
}
```

**Key rules:**
- ViewModels are `Transient` (new instance per request) unless shared state is needed
- Services (repositories, API clients) are `Singleton` or `Scoped`
- Views receive their ViewModel via constructor: `public MainWindow(MainViewModel vm) { DataContext = vm; }`
- Never use `ServiceLocator` pattern — always constructor injection

### Step 5: Compose Parent-Child ViewModels

Build complex screens by composing ViewModels. Parents own child collections; children communicate up via events or the Messenger.

Use when a view contains sub-views (tabs, lists with detail panels, master-detail layouts).

> **Values**: 余白の設計 — Small, focused ViewModels leave room for change. A monolithic ViewModel becomes rigid; composed ones adapt.

```csharp
public partial class MainViewModel : ObservableObject
{
    [ObservableProperty]
    private ObservableCollection<CustomerViewModel> _customers = [];

    [ObservableProperty]
    private CustomerViewModel? _selectedCustomer;

    [RelayCommand]
    private void AddCustomer()
    {
        var newCustomer = new CustomerViewModel { Name = "New Customer" };
        Customers.Add(newCustomer);
        SelectedCustomer = newCustomer;
    }

    [RelayCommand]
    private void RemoveCustomer()
    {
        if (SelectedCustomer is null) return;
        Customers.Remove(SelectedCustomer);
        SelectedCustomer = Customers.FirstOrDefault();
    }
}
```

**XAML master-detail:**

```xml
<Grid>
    <Grid.ColumnDefinitions>
        <ColumnDefinition Width="250" />
        <ColumnDefinition Width="*" />
    </Grid.ColumnDefinitions>

    <!-- Master list -->
    <ListBox Grid.Column="0"
             ItemsSource="{Binding Customers}"
             SelectedItem="{Binding SelectedCustomer}"
             DisplayMemberPath="Name" />

    <!-- Detail panel -->
    <ContentControl Grid.Column="1"
                    Content="{Binding SelectedCustomer}" />
</Grid>
```

**Key rules:**
- Parent ViewModel owns child collections as `ObservableCollection<T>`
- Use `[ObservableProperty]` for `SelectedItem` binding
- For cross-ViewModel communication, prefer `WeakReferenceMessenger` over direct references
- Keep child ViewModels self-contained — they should not reference their parent

---

## Best Practices

- Start every new view with Step 1 (ViewModel base) before writing any XAML
- Use `[ObservableProperty]` exclusively — never write manual `OnPropertyChanged` calls
- Keep ViewModels under 200 lines; extract services for complex logic
- Test ViewModels without XAML by calling commands and asserting property changes
- Use `CancellationToken` in all async commands for proper cancellation support

## Common Pitfalls

1. **Business logic in code-behind**
   - ❌ `private void Button_Click(object sender, RoutedEventArgs e) { SaveToDatabase(); }`
   - ✅ `[RelayCommand] private async Task SaveAsync() { await _repo.SaveAsync(); }`
   - Why: Code-behind cannot be unit tested. ViewModels can.

2. **Forgetting `NotifyCanExecuteChanged()`**
   - ❌ Changing `Name` but Save button stays disabled
   - ✅ `partial void OnNameChanged(string value) { SaveCommand.NotifyCanExecuteChanged(); }`
   - Why: WPF does not re-evaluate CanExecute automatically when properties change.

3. **Using `ObservableObject` when validation is needed**
   - ❌ `public partial class FormVm : ObservableObject` with manual error string
   - ✅ `public partial class FormVm : ObservableValidator` with `[NotifyDataErrorInfo]`
   - Why: `ObservableValidator` integrates with WPF's built-in validation display pipeline.

4. **Manual `PropertyChanged` raising with source generators**
   - ❌ `OnPropertyChanged("Name");` alongside `[ObservableProperty]`
   - ✅ Remove manual calls — the generator handles it
   - Why: Double-raising causes redundant UI updates and subtle bugs.

5. **Monolithic ViewModel with 500+ lines**
   - ❌ One ViewModel with all properties, commands, and child logic
   - ✅ Parent ViewModel composing child ViewModels (Step 5)
   - Why: Large ViewModels resist change and make testing painful.

## Anti-Patterns

- **ServiceLocator in ViewModels** — Use constructor injection, not `App.Current.Services.GetService<T>()`
- **Two-way binding everything** — Only use `TwoWay` for user input fields; display-only fields use `OneWay` (default)
- **Passing View references to ViewModel** — ViewModel must never know about `Window`, `UserControl`, or any XAML type
- **God ViewModel** — One ViewModel per view is fine for simple screens, but complex screens need composition (Step 5)

---

## Quick Reference

### CommunityToolkit.Mvvm Cheat Sheet

| Pattern | Attribute/Class | Generated |
|---------|----------------|-----------|
| Observable property | `[ObservableProperty]` on `private string _name` | `public string Name { get; set; }` + `PropertyChanged` |
| Property change hook | `partial void OnNameChanged(string value)` | Called after `Name` setter |
| Sync command | `[RelayCommand]` on `private void Save()` | `public IRelayCommand SaveCommand` |
| Async command | `[RelayCommand]` on `private async Task LoadAsync()` | `public IAsyncRelayCommand LoadCommand` |
| CanExecute | `[RelayCommand(CanExecute = nameof(CanSave))]` | Gated command |
| Validation | `[NotifyDataErrorInfo]` + `[Required]` | `INotifyDataErrorInfo` impl |
| Base (no validation) | `ObservableObject` | — |
| Base (with validation) | `ObservableValidator` | — |

### Decision Table

| Situation | Pattern | Step |
|-----------|---------|------|
| New view with input fields | ObservableValidator + commands | Steps 1-3 |
| Display-only view | ObservableObject + load command | Steps 1-2 |
| View with sub-views/tabs | Parent-child composition | Step 5 |
| View needs external services | DI registration | Step 4 |
| Converting code-behind | Extract to ViewModel | Steps 1-2 |

---

## FAQ

**Q: When should I use `ObservableObject` vs `ObservableValidator`?**
A: Use `ObservableValidator` when the view has user input that needs validation. Use `ObservableObject` for display-only or command-only ViewModels.

**Q: How do I show dialogs from a ViewModel?**
A: Inject an `IDialogService` interface. The implementation (in the View layer) handles `Window.ShowDialog()`. The ViewModel calls `_dialogService.ShowConfirmation("message")` and receives a `bool` result.

**Q: Should I use `Messenger` or direct events?**
A: Use `WeakReferenceMessenger` for cross-ViewModel communication when ViewModels don't have a direct parent-child relationship. For parent-child, direct property binding is simpler.

**Q: How do I handle window closing from a ViewModel?**
A: Use an `ICloseable` interface or `WeakReferenceMessenger.Send(new CloseWindowMessage())`. The View subscribes in code-behind with a one-line handler.
