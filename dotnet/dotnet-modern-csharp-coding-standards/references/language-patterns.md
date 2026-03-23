# Language Patterns（詳細リファレンス）

<!-- Parent skill: ../SKILL.md (dotnet-modern-csharp-coding-standards) -->

このファイルには、メイン skill から参照する `record`、パターンマッチング、nullable reference types、文字列処理パターンの完全版サンプルをまとめています。

---

## 不変データのための Records（C# 9+）

DTO、メッセージ、イベント、ドメインエンティティには `record` 型を使います。

```csharp
// シンプルな不変 DTO
public record CustomerDto(string Id, string Name, string Email);

// コンストラクタで validation する record
public record EmailAddress
{
    public string Value { get; init; }

    public EmailAddress(string value)
    {
        if (string.IsNullOrWhiteSpace(value) || !value.Contains('@'))
            throw new ArgumentException("Invalid email address", nameof(value));
        Value = value;
    }
}

// 計算プロパティを持つ record
public record Order(string Id, decimal Subtotal, decimal Tax)
{
    public decimal Total => Subtotal + Tax;
}

// collection を持つ record — IReadOnlyList を使う
public record ShoppingCart(
    string CartId,
    string CustomerId,
    IReadOnlyList<CartItem> Items)
{
    public decimal Total => Items.Sum(item => item.Price * item.Quantity);
}
```

**`record class` と `record struct` の使い分け:**
- `record class`（既定）: エンティティ、集約、複数プロパティを持つ DTO などの参照型
- `record struct`: 値オブジェクト向けの値型（次のセクション参照）

---

## 値オブジェクトは `readonly record struct`

値オブジェクトは、パフォーマンスと value semantics のため **常に `readonly record struct`** を使います。

```csharp
// 単一値の value object
public readonly record struct OrderId(string Value)
{
    public OrderId(string value) : this(
        !string.IsNullOrWhiteSpace(value)
            ? value
            : throw new ArgumentException("OrderId cannot be empty", nameof(value)))
    { }

    public override string ToString() => Value;
}

// 複数値の value object
public readonly record struct Money(decimal Amount, string Currency)
{
    public Money(decimal amount, string currency) : this(
        amount >= 0 ? amount : throw new ArgumentException("Amount cannot be negative", nameof(amount)),
        ValidateCurrency(currency))
    { }

    private static string ValidateCurrency(string currency)
    {
        if (string.IsNullOrWhiteSpace(currency) || currency.Length != 3)
            throw new ArgumentException("Currency must be a 3-letter code", nameof(currency));
        return currency.ToUpperInvariant();
    }

    public Money Add(Money other)
    {
        if (Currency != other.Currency)
            throw new InvalidOperationException($"Cannot add {Currency} to {other.Currency}");
        return new Money(Amount + other.Amount, Currency);
    }

    public override string ToString() => $"{Amount:N2} {Currency}";
}

// factory pattern を使う複雑な value object
public readonly record struct PhoneNumber
{
    public string Value { get; }

    private PhoneNumber(string value) => Value = value;

    public static Result<PhoneNumber, string> Create(string input)
    {
        if (string.IsNullOrWhiteSpace(input))
            return Result<PhoneNumber, string>.Failure("Phone number cannot be empty");

        var digits = new string(input.Where(char.IsDigit).ToArray());

        if (digits.Length < 10 || digits.Length > 15)
            return Result<PhoneNumber, string>.Failure("Phone number must be 10-15 digits");

        return Result<PhoneNumber, string>.Success(new PhoneNumber(digits));
    }

    public override string ToString() => Value;
}

// 範囲 validation を持つ percentage value object
public readonly record struct Percentage
{
    private readonly decimal _value;
    public decimal Value => _value;

    public Percentage(decimal value)
    {
        if (value < 0 || value > 100)
            throw new ArgumentOutOfRangeException(nameof(value), "Percentage must be between 0 and 100");
        _value = value;
    }

    public decimal AsDecimal() => _value / 100m;

    public static Percentage FromDecimal(decimal decimalValue)
    {
        if (decimalValue < 0 || decimalValue > 1)
            throw new ArgumentOutOfRangeException(nameof(decimalValue), "Decimal must be between 0 and 1");
        return new Percentage(decimalValue * 100);
    }

    public override string ToString() => $"{_value}%";
}

// 強い型付けをした ID
public readonly record struct CustomerId(Guid Value)
{
    public static CustomerId New() => new(Guid.NewGuid());
    public override string ToString() => Value.ToString();
}

// 単位付き quantity
public readonly record struct Quantity(int Value, string Unit)
{
    public Quantity(int value, string unit) : this(
        value >= 0 ? value : throw new ArgumentException("Quantity cannot be negative"),
        !string.IsNullOrWhiteSpace(unit) ? unit : throw new ArgumentException("Unit cannot be empty"))
    { }

    public override string ToString() => $"{Value} {Unit}";
}
```

**値オブジェクトに `readonly record struct` を使う理由:**
- **Value semantics**: 参照ではなく内容で等価比較できる
- **Stack allocation**: GC 圧力を抑えつつ高性能
- **Immutability**: `readonly` により意図しない変更を防げる
- **Pattern matching**: `switch` 式と自然に組み合わせられる

### 重要: 暗黙的変換は禁止

暗黙的変換演算子は、型のすり替えを静かに許してしまうため、値オブジェクトの目的を壊します。

```csharp
// ❌ 誤り — コンパイル時の型安全性を壊す
public readonly record struct UserId(Guid Value)
{
    public static implicit operator UserId(Guid value) => new(value);  // 禁止
    public static implicit operator Guid(UserId value) => value.Value; // 禁止
}

// implicit operator があると、これは静かにコンパイルされてしまう:
void ProcessUser(UserId userId) { }
ProcessUser(Guid.NewGuid());  // 意図は PostId だったかもしれないのに通ってしまう

// ✅ 正しい — すべての変換を明示する
public readonly record struct UserId(Guid Value)
{
    public static UserId New() => new(Guid.NewGuid());
    // 作成: new UserId(guid) または UserId.New()
    // 取り出し: userId.Value
}
```

明示的変換にすると、境界をまたぐ変換が必ずコード上に現れます。

```csharp
// API 境界 — 明示的に変換して受け取る
var userId = new UserId(request.UserId);

// Database 境界 — 明示的に値を取り出して渡す
await _db.ExecuteAsync(sql, new { UserId = userId.Value });
```

---

## Pattern Matching（C# 8–12）

モダンなパターンマッチングを活用して、より簡潔で表現力の高いコードにします。

```csharp
// property pattern を使う switch expression
public string GetPaymentMethodDescription(PaymentMethod payment) => payment switch
{
    { Type: PaymentType.CreditCard, Last4: var last4 } => $"Credit card ending in {last4}",
    { Type: PaymentType.BankTransfer, AccountNumber: var account } => $"Bank transfer from {account}",
    { Type: PaymentType.Cash } => "Cash payment",
    _ => "Unknown payment method"
};

// relational operator を組み合わせた property pattern
public decimal CalculateDiscount(Order order) => order switch
{
    { Total: > 1000m } => order.Total * 0.15m,
    { Total: > 500m }  => order.Total * 0.10m,
    { Total: > 100m }  => order.Total * 0.05m,
    _ => 0m
};

// relational pattern と logical pattern
public string ClassifyTemperature(int temp) => temp switch
{
    < 0             => "Freezing",
    >= 0 and < 10   => "Cold",
    >= 10 and < 20  => "Cool",
    >= 20 and < 30  => "Warm",
    >= 30           => "Hot",
    _ => throw new ArgumentOutOfRangeException(nameof(temp))
};

// list pattern（C# 11+）
public bool IsValidSequence(int[] numbers) => numbers switch
{
    []                                             => false,
    [_]                                            => true,
    [var first, .., var last] when first < last     => true,
    _                                              => false
};

// null check を含む type pattern
public string FormatValue(object? value) => value switch
{
    null                         => "null",
    string s                     => $"\"{s}\"",
    int i                        => i.ToString(),
    double d                     => d.ToString("F2"),
    DateTime dt                  => dt.ToString("yyyy-MM-dd"),
    Money m                      => m.ToString(),
    IEnumerable<object> coll     => $"[{string.Join(", ", coll)}]",
    _                            => value.ToString() ?? "unknown"
};

// 複雑なロジックで pattern を組み合わせる
public record OrderState(bool IsPaid, bool IsShipped, bool IsCancelled);

public string GetOrderStatus(OrderState state) => state switch
{
    { IsCancelled: true }                => "Cancelled",
    { IsPaid: true, IsShipped: true }    => "Delivered",
    { IsPaid: true, IsShipped: false }   => "Processing",
    { IsPaid: false }                    => "Awaiting Payment",
    _                                    => "Unknown"
};

// value object を含む tuple pattern matching
public decimal CalculateShipping(Money total, Country destination) => (total, destination) switch
{
    ({ Amount: > 100m }, _)                  => 0m,       // 送料無料
    (_, { Code: "US" or "CA" })              => 5m,       // 北米
    (_, { Code: "GB" or "FR" or "DE" })      => 10m,      // 欧州
    _                                        => 25m       // その他海外
};
```

---

## Nullable Reference Types（C# 8+）

プロジェクト全体で nullable reference types を有効にし、null を明示的に扱います。

```xml
<!-- In .csproj -->
<PropertyGroup>
    <Nullable>enable</Nullable>
</PropertyGroup>
```

```csharp
public class UserService
{
    // 既定では non-nullable
    public string GetUserName(User user) => user.Name;

    // 明示的に nullable を返す
    public string? FindUserName(string userId)
    {
        var user = _repository.Find(userId);
        return user?.Name;
    }

    // null-forgiving operator（多用しない）
    public string GetRequiredConfigValue(string key)
    {
        var value = Configuration[key];
        return value!;  // null ではないと確信できる場合だけ使う
    }
}

// null check を含む pattern matching
public decimal GetDiscount(Customer? customer) => customer switch
{
    null                   => 0m,
    { IsVip: true }        => 0.20m,
    { OrderCount: > 10 }   => 0.10m,
    _                      => 0.05m
};

// null-coalescing のパターン
public string GetDisplayName(User? user) =>
    user?.PreferredName ?? user?.Email ?? "Guest";

// ArgumentNullException.ThrowIfNull を使う guard clause（C# 11+）
public void ProcessOrder(Order? order)
{
    ArgumentNullException.ThrowIfNull(order);
    // このスコープでは order は non-nullable とみなせる
    Console.WriteLine(order.Id);
}
```

---

## 文字列処理パターン

文字列パースでは、不要な allocation を避けるため `ReadOnlySpan<char>` を優先します。

```csharp
// Span ベースの key-value parsing
public bool TryParseKeyValue(ReadOnlySpan<char> line, out string key, out string value)
{
    key = string.Empty;
    value = string.Empty;

    int colonIndex = line.IndexOf(':');
    if (colonIndex == -1) return false;

    key = new string(line.Slice(0, colonIndex).Trim());
    value = new string(line.Slice(colonIndex + 1).Trim());
    return true;
}
```

複雑な文字列組み立てには `string.Create` または `StringBuilder` を使い、ループ内で `+` 連結しないでください。
