# SimilarityCalculator.cs (Full Reference)

This file contains the full example implementation referenced from `SKILL.md`.

```csharp
namespace Mercury.Domain.Matching
{
    public static class SimilarityCalculator
    {
        /// <summary>
        /// Normalized Levenshtein similarity (0.0 = completely different, 1.0 = identical).
        /// Strings are normalized before comparison (lowercase, whitespace removed).
        /// </summary>
        public static double StringSimilarity(string? s1, string? s2)
        {
            var a = Normalize(s1);
            var b = Normalize(s2);
            if (a.Length == 0 && b.Length == 0) return 1.0;
            if (a.Length == 0 || b.Length == 0) return 0.0;
            int maxLen = Math.Max(a.Length, b.Length);
            int distance = LevenshteinDistance(a, b);
            return 1.0 - (double)distance / maxLen;
        }

        /// <summary>
        /// Exact match for monetary values. Use decimal to avoid floating-point errors.
        /// Returns 1.0 if equal, 0.0 otherwise.
        /// </summary>
        public static double NumericSimilarityDecimal(decimal a, decimal b)
            => a == b ? 1.0 : 0.0;

        /// <summary>
        /// Tolerance-based comparison for dimensions (width, height, weight).
        /// Parses strings to double; returns similarity based on relative difference.
        /// </summary>
        public static double NumericSimilarityDouble(string? s1, string? s2)
        {
            if (!double.TryParse(Normalize(s1), out var a)
                || !double.TryParse(Normalize(s2), out var b))
                return 0.0;

            if (a == 0 && b == 0) return 1.0;
            double maxVal = Math.Max(Math.Abs(a), Math.Abs(b));
            if (maxVal == 0) return 1.0;
            double diff = Math.Abs(a - b) / maxVal;
            return Math.Max(0.0, 1.0 - diff);
        }

        private static string Normalize(string? value)
            => (value ?? string.Empty).Trim().Replace(" ", "").Replace("　", "").ToLowerInvariant();

        private static int LevenshteinDistance(string s1, string s2)
        {
            int m = s1.Length, n = s2.Length;
            var dp = new int[m + 1, n + 1];
            for (int i = 0; i <= m; i++) dp[i, 0] = i;
            for (int j = 0; j <= n; j++) dp[0, j] = j;
            for (int i = 1; i <= m; i++)
                for (int j = 1; j <= n; j++)
                {
                    int cost = s1[i - 1] == s2[j - 1] ? 0 : 1;
                    dp[i, j] = Math.Min(
                        Math.Min(dp[i - 1, j] + 1, dp[i, j - 1] + 1),
                        dp[i - 1, j - 1] + cost);
                }
            return dp[m, n];
        }
    }
}
```
