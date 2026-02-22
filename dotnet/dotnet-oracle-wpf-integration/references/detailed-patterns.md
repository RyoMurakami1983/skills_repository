# Detailed Implementation Patterns

Extended code examples for `dotnet-oracle-wpf-integration`. See [SKILL.md](../SKILL.md) for the workflow overview.

---

## Step 3 — OracleConfigViewModel

Full implementation of the MVVM ViewModel and dialog for Oracle connection settings.

### OracleConfigViewModel.cs

```csharp
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

namespace YourApp.Presentation.ViewModels
{
    public partial class OracleConfigViewModel : ObservableObject
    {
        private readonly ISecureConfigService _configService;

        [ObservableProperty] private string userId = string.Empty;
        [ObservableProperty] private string password = string.Empty;
        [ObservableProperty] private string dataSource = string.Empty;
        [ObservableProperty] private string statusMessage = string.Empty;
        [ObservableProperty] private bool isSaving;

        public OracleConfigViewModel(ISecureConfigService configService)
            => _configService = configService;

        public async Task LoadConfigAsync()
        {
            try
            {
                var config = await _configService.LoadOracleConfigAsync();
                UserId = config.UserId;
                DataSource = config.DataSource;
                Password = config.GetDecryptedPassword();
            }
            catch (InvalidOperationException)
            {
                // DPAPI decryption fails if user profile or machine changed
                Password = string.Empty;
                StatusMessage = "Failed to decrypt stored password. Please re-enter.";
            }
        }

        private bool ValidateFields()
        {
            if (string.IsNullOrWhiteSpace(UserId)
                || string.IsNullOrWhiteSpace(Password)
                || string.IsNullOrWhiteSpace(DataSource))
            { StatusMessage = "All fields are required."; return false; }
            return true;
        }

        [RelayCommand]
        private async Task SaveAsync()
        {
            if (!ValidateFields()) return;
            IsSaving = true;
            try
            {
                var config = new OracleConfigModel
                    { UserId = UserId, DataSource = DataSource };
                config.SetPassword(Password);
                await _configService.SaveOracleConfigAsync(config);
                StatusMessage = "Saved.";
            }
            catch (Exception ex) { StatusMessage = $"Save failed: {ex.Message}"; }
            finally { IsSaving = false; }
        }

        [RelayCommand]
        private async Task TestConnectionAsync()
        {
            if (!ValidateFields()) return;
            StatusMessage = "Testing connection...";
            try
            {
                string connStr = $"User Id={UserId};Password={Password};"
                    + $"Data Source={DataSource};Connection Timeout=10;";
                await Task.Run(() =>
                {
                    using var conn = new Oracle.ManagedDataAccess.Client
                        .OracleConnection(connStr);
                    conn.Open();
                    using var cmd = conn.CreateCommand();
                    cmd.CommandText = "SELECT SYSDATE FROM DUAL";
                    cmd.ExecuteScalar();
                });
                StatusMessage = "✅ Connection successful!";
            }
            catch (Exception ex)
            { StatusMessage = $"❌ Connection failed: {ex.Message}"; }
        }
    }
}
```

### OracleConfigDialog.xaml.cs

Minimal code-behind — PasswordBox bridging only (WPF does not support two-way binding on PasswordBox):

```csharp
public partial class OracleConfigDialog : Window
{
    public OracleConfigDialog(OracleConfigViewModel viewModel)
    {
        InitializeComponent();
        DataContext = viewModel;
        Loaded += async (_, _) => await viewModel.LoadConfigAsync();
        // PasswordBox does not support two-way binding natively
        viewModel.PropertyChanged += (_, e) =>
        { if (e.PropertyName == nameof(viewModel.Password)) PasswordBox.Password = viewModel.Password; };
        PasswordBox.PasswordChanged += (_, _) => viewModel.Password = PasswordBox.Password;
    }
    private void Close_Click(object sender, RoutedEventArgs e) => Close();
}
```
