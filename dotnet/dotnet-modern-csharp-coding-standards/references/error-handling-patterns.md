# Error Handling Patterns — Detailed Reference

<!-- Parent skill: ../SKILL.md (dotnet-modern-csharp-coding-standards) -->

This file contains the full `Result<T, TError>` implementation, railway-oriented programming examples, and guidance on when to use exceptions vs Result types.

---

## Result<T, TError> Full Implementation

A minimal, zero-dependency Result type as `readonly record struct`:

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

    // Functor: transform the success value
    public Result<TOut, TError> Map<TOut>(Func<TValue, TOut> mapper)
        => _isSuccess
            ? Result<TOut, TError>.Success(mapper(_value!))
            : Result<TOut, TError>.Failure(_error!);

    // Monad bind: chain operations that may fail
    public Result<TOut, TError> Bind<TOut>(Func<TValue, Result<TOut, TError>> binder)
        => _isSuccess ? binder(_value!) : Result<TOut, TError>.Failure(_error!);

    // Provide a default on failure
    public TValue GetValueOr(TValue defaultValue)
        => _isSuccess ? _value! : defaultValue;

    // Exhaustive matching
    public TResult Match<TResult>(
        Func<TValue, TResult> onSuccess,
        Func<TError, TResult> onFailure)
        => _isSuccess ? onSuccess(_value!) : onFailure(_error!);
}
```

---

## Error Types

Define error types as `readonly record struct` for value semantics:

```csharp
public readonly record struct OrderError(string Code, string Message);

// Common error codes as constants
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

Chain multiple operations that may each fail, short-circuiting on the first error:

```csharp
public sealed class OrderService(IOrderRepository repository)
{
    public async Task<Result<Order, OrderError>> CreateOrderAsync(
        CreateOrderRequest request,
        CancellationToken cancellationToken)
    {
        // Each step short-circuits on failure
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

### Mapping Results to HTTP Responses

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

### Chaining with Bind

Use `Bind` to compose multiple Result-returning operations:

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

## When to Use Exceptions vs Result Types

| Situation | Mechanism | Rationale |
|-----------|-----------|-----------|
| Validation failure | `Result<T, TError>` | Expected — caller must decide how to handle |
| Business rule violation | `Result<T, TError>` | Part of normal application flow |
| Entity not found | `Result<T, TError>` | Expected query outcome |
| Invalid argument (programming bug) | `ArgumentException` | Indicates a bug in the calling code |
| Network / I/O failure | Exception | Unexpected infrastructure error |
| Null dereference | `NullReferenceException` | Programming bug — fix the code |
| Out of memory | `OutOfMemoryException` | System-level failure |

### Guidelines

1. **Expected errors** → `Result<T, TError>`. The caller is responsible for handling them. They are part of the method's contract.
2. **Unexpected errors** → Exceptions. They bubble up to a global handler (middleware, try/catch at the boundary).
3. **Never catch `Exception`** in business logic. Catch specific types or use Result.
4. **Never throw in a loop**. If an operation may fail repeatedly, return a collection of Results.
5. **Error types should be value types** (`readonly record struct`) — no heap allocation for the common error path.
