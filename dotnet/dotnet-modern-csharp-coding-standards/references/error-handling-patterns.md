# Error Handling Patterns（詳細リファレンス）

<!-- Parent skill: ../SKILL.md (dotnet-modern-csharp-coding-standards) -->

このファイルには、完全な `Result<T, TError>` 実装、Railway-Oriented Programming の例、そして Exception と Result type の使い分け指針をまとめています。

---

## `Result<T, TError>` の完全実装

依存ゼロの最小 `Result` type を `readonly record struct` として実装する例です。

```csharp
public readonly record struct Result<TValue, TError>
{
    private readonly TValue? _value;
    private readonly TError? _error;
    private readonly bool _isSuccess;

    private Result(TValue value)
    {
        _value = value;
        _error = default;
        _isSuccess = true;
    }

    private Result(TError error)
    {
        _value = default;
        _error = error;
        _isSuccess = false;
    }

    public bool IsSuccess => _isSuccess;
    public bool IsFailure => !_isSuccess;

    public TValue Value => _isSuccess
        ? _value!
        : throw new InvalidOperationException("Cannot access Value of a failed result");

    public TError Error => !_isSuccess
        ? _error!
        : throw new InvalidOperationException("Cannot access Error of a successful result");

    public static Result<TValue, TError> Success(TValue value) => new(value);
    public static Result<TValue, TError> Failure(TError error) => new(error);

    // Functor: success value を変換する
    public Result<TOut, TError> Map<TOut>(Func<TValue, TOut> mapper)
        => _isSuccess
            ? Result<TOut, TError>.Success(mapper(_value!))
            : Result<TOut, TError>.Failure(_error!);

    // Monad bind: 失敗しうる処理を連結する
    public Result<TOut, TError> Bind<TOut>(Func<TValue, Result<TOut, TError>> binder)
        => _isSuccess ? binder(_value!) : Result<TOut, TError>.Failure(_error!);

    // failure 時に既定値を返す
    public TValue GetValueOr(TValue defaultValue)
        => _isSuccess ? _value! : defaultValue;

    // 網羅的な matching
    public TResult Match<TResult>(
        Func<TValue, TResult> onSuccess,
        Func<TError, TResult> onFailure)
        => _isSuccess ? onSuccess(_value!) : onFailure(_error!);
}
```

---

## Error Type

error type も value semantics を持たせるため、`readonly record struct` として定義します。

```csharp
public readonly record struct OrderError(string Code, string Message);

// 共通 error code を定数として定義
public static class OrderErrorCodes
{
    public const string ValidationError = "VALIDATION_ERROR";
    public const string InsufficientInventory = "INSUFFICIENT_INVENTORY";
    public const string NotFound = "NOT_FOUND";
    public const string Unauthorized = "UNAUTHORIZED";
}
```

---

## Railway-Oriented Programming

失敗しうる複数の処理をつなぎ、最初のエラーで short-circuit させます。

```csharp
public sealed class OrderService(IOrderRepository repository)
{
    public async Task<Result<Order, OrderError>> CreateOrderAsync(
        CreateOrderRequest request,
        CancellationToken cancellationToken)
    {
        // 各ステップは failure 時に short-circuit する
        var validationResult = ValidateRequest(request);
        if (validationResult.IsFailure)
            return Result<Order, OrderError>.Failure(validationResult.Error);

        var inventoryResult = await CheckInventoryAsync(request.Items, cancellationToken);
        if (inventoryResult.IsFailure)
            return Result<Order, OrderError>.Failure(inventoryResult.Error);

        var order = new Order(
            OrderId.New(),
            new CustomerId(request.CustomerId),
            request.Items);

        await repository.SaveAsync(order, cancellationToken);
        return Result<Order, OrderError>.Success(order);
    }

    private Result<CreateOrderRequest, OrderError> ValidateRequest(CreateOrderRequest request)
    {
        if (string.IsNullOrWhiteSpace(request.CustomerId))
            return Result<CreateOrderRequest, OrderError>.Failure(
                new OrderError("VALIDATION_ERROR", "CustomerId is required"));

        if (request.Items.Count == 0)
            return Result<CreateOrderRequest, OrderError>.Failure(
                new OrderError("VALIDATION_ERROR", "Order must have at least one item"));

        return Result<CreateOrderRequest, OrderError>.Success(request);
    }
}
```

### Result を HTTP Response へマッピングする

```csharp
public IActionResult MapToActionResult(Result<Order, OrderError> result)
{
    return result.Match(
        onSuccess: order => new OkObjectResult(order),
        onFailure: error => error.Code switch
        {
            "VALIDATION_ERROR"       => new BadRequestObjectResult(error.Message),
            "INSUFFICIENT_INVENTORY" => new ConflictObjectResult(error.Message),
            "NOT_FOUND"              => new NotFoundObjectResult(error.Message),
            _                        => new ObjectResult(error.Message) { StatusCode = 500 }
        });
}
```

### `Bind` による合成

`Bind` を使うと、`Result` を返す処理を段階的に合成できます。

```csharp
public Result<OrderConfirmation, OrderError> ProcessOrder(CreateOrderRequest request)
{
    return ValidateRequest(request)
        .Bind(CheckInventory)
        .Bind(CalculateTotal)
        .Map(total => new OrderConfirmation(OrderId.New(), total));
}
```

---

## Exception と Result Type の使い分け

| 状況 | 使うもの | 理由 |
|-----------|-----------|-----------|
| Validation failure | `Result<T, TError>` | 想定内の失敗であり、呼び出し側が処理方針を決める |
| Business rule violation | `Result<T, TError>` | 通常のアプリケーションフローの一部 |
| Entity not found | `Result<T, TError>` | 期待される query 結果 |
| Invalid argument (programming bug) | `ArgumentException` | 呼び出し側コードのバグを示す |
| Network / I/O failure | Exception | 想定外のインフラ障害 |
| Null dereference | `NullReferenceException` | プログラミングバグなのでコードを直すべき |
| Out of memory | `OutOfMemoryException` | システムレベルの障害 |

### ガイドライン

1. **想定内のエラー** → `Result<T, TError>` を使います。これはメソッド契約の一部であり、呼び出し側が処理責任を持ちます。
2. **想定外のエラー** → Exception を使います。middleware や境界の `try/catch` など、グローバルなハンドラまで伝播させます。
3. ビジネスロジックで **`Exception` を丸ごと catch しない** でください。特定の型を捕まえるか、Result を返します。
4. **ループ内で throw しない** でください。繰り返し失敗しうる処理なら、Result の collection を返します。
5. **error type は value type にする**（`readonly record struct`）。よくある失敗経路で heap allocation を増やさないためです。
