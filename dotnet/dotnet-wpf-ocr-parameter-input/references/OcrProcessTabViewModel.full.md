# OcrProcessTabViewModel.cs (Full Reference)

This is the full example referenced from `SKILL.md`.

```csharp
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using System;
using System.Collections.ObjectModel;
using System.Threading.Tasks;

namespace YourApp.ViewModels
{
    public partial class OcrProcessTabViewModel : ObservableObject
    {
        private readonly IOcrUseCase _useCase;

        // --- Input fields (customize per use case from Step 1) ---
        [ObservableProperty] private string selectedCategory = "";
        [ObservableProperty] private string selectedType = "";
        [ObservableProperty] private string remarks = "";

        // --- Progress tracking (fixed pattern) ---
        [ObservableProperty] private int progressValue;
        [ObservableProperty] private string progressMessage = "";
        [ObservableProperty] private bool isProcessing;
        [ObservableProperty] private bool canStartOcr;

        // --- Collections ---
        public ObservableCollection<string> CategoryItems { get; } = new();
        public ObservableCollection<string> TypeItems { get; } = new();
        public ObservableCollection<ProgressLogItem> ProgressItems { get; } = new();

        /// <summary>
        /// Raised when OCR completes. Parent ViewModel subscribes to handle results.
        /// </summary>
        public event EventHandler<IEnumerable<object>>? OcrCompleted;

        public OcrProcessTabViewModel(IOcrUseCase useCase)
            => _useCase = useCase;

        [RelayCommand(CanExecute = nameof(CanStartOcr))]
        private async Task StartOcrAsync()
        {
            IsProcessing = true;
            ProgressValue = 0;
            ProgressItems.Clear();

            var progress = new Progress<(int percent, string message)>(p =>
            {
                ProgressValue = p.percent;
                ProgressMessage = p.message;
                ProgressItems.Add(new ProgressLogItem(DateTime.Now, "🔄", p.message, "Running"));
            });

            try
            {
                var results = await _useCase.ExecuteAsync(/* params */, progress);
                ProgressItems.Add(new ProgressLogItem(DateTime.Now, "✅", "OCR completed", "Done"));
                ProgressValue = 100;
                OcrCompleted?.Invoke(this, results);
            }
            catch (Exception ex)
            {
                ProgressItems.Add(new ProgressLogItem(DateTime.Now, "❌", ex.Message, "Error"));
            }
            finally
            {
                IsProcessing = false;
            }
        }

        /// <summary>
        /// Called by parent ViewModel when a PDF is uploaded.
        /// Enables the Start button.
        /// </summary>
        public void OnPdfUploaded(string pdfPath)
        {
            CanStartOcr = !string.IsNullOrWhiteSpace(pdfPath);
            StartOcrCommand.NotifyCanExecuteChanged();
        }

        public void Reset()
        {
            ProgressItems.Clear();
            ProgressValue = 0;
            ProgressMessage = "";
            CanStartOcr = false;
            StartOcrCommand.NotifyCanExecuteChanged();
        }
    }
}
```
