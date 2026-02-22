# Detailed DI Patterns — Reference

This file contains extended examples and advanced patterns for
`dotnet-extensions-dependency-injection`. See [../SKILL.md](../SKILL.md) for
the main skill.

---

## Layered Extension Composition

For larger applications, compose extensions hierarchically:

```csharp
// Top-level: Everything the app needs
public static class AppServiceCollectionExtensions
{
    public static IServiceCollection AddAppServices(this IServiceCollection services)
    {
        return services
            .AddDomainServices()
            .AddInfrastructureServices()
            .AddApiServices();
    }
}

// Domain layer
public static class DomainServiceCollectionExtensions
{
    public static IServiceCollection AddDomainServices(this IServiceCollection services)
    {
        return services
            .AddUserServices()
            .AddOrderServices()
            .AddProductServices();
    }
}

// Infrastructure layer
public static class InfrastructureServiceCollectionExtensions
{
    public static IServiceCollection AddInfrastructureServices(this IServiceCollection services)
    {
        return services
            .AddEmailServices()
            .AddPaymentServices()
            .AddStorageServices();
    }
}
```

---

## Akka.Hosting Integration

The same pattern works for Akka.NET actor configuration:

```csharp
public static class OrderActorExtensions
{
    public static AkkaConfigurationBuilder AddOrderActors(
        this AkkaConfigurationBuilder builder)
    {
        return builder
            .WithActors((system, registry, resolver) =>
            {
                var orderProps = resolver.Props<OrderActor>();
                var orderRef = system.ActorOf(orderProps, "orders");
                registry.Register<OrderActor>(orderRef);
            })
            .WithShardRegion<OrderShardActor>(
                typeName: "order-shard",
                (system, registry, resolver) =>
                    entityId => resolver.Props<OrderShardActor>(entityId),
                new OrderMessageExtractor(),
                ShardOptions.Create());
    }
}

// Usage in Program.cs
builder.Services.AddAkka("MySystem", (builder, sp) =>
{
    builder
        .AddOrderActors()
        .AddInventoryActors()
        .AddNotificationActors();
});
```

See `akka/hosting-actor-patterns` skill for complete Akka.Hosting patterns.

---

## Akka.NET Actor Scope Management

**Actors don't have automatic DI scopes.** If you need scoped services inside
an actor, inject `IServiceProvider` and create scopes manually.

### Pattern: Scope Per Message

```csharp
public sealed class AccountProvisionActor : ReceiveActor
{
    private readonly IServiceProvider _serviceProvider;
    private readonly IActorRef _mailingActor;

    public AccountProvisionActor(
        IServiceProvider serviceProvider,
        IRequiredActor<MailingActor> mailingActor)
    {
        _serviceProvider = serviceProvider;
        _mailingActor = mailingActor.ActorRef;

        ReceiveAsync<ProvisionAccount>(HandleProvisionAccount);
    }

    private async Task HandleProvisionAccount(ProvisionAccount msg)
    {
        // Create scope for this message processing
        using var scope = _serviceProvider.CreateScope();

        // Resolve scoped services
        var userManager = scope.ServiceProvider.GetRequiredService<UserManager<User>>();
        var orderRepository = scope.ServiceProvider.GetRequiredService<IOrderRepository>();

        // Do work with scoped services
        var user = await userManager.FindByIdAsync(msg.UserId);
        var order = await orderRepository.CreateAsync(msg.Order);

        // DbContext commits when scope disposes
    }
}
```

### Why This Pattern Works

1. **Each message gets fresh DbContext** — No stale entity tracking
2. **Proper disposal** — Connections released after each message
3. **Isolation** — One message's errors don't affect others
4. **Testable** — Can inject mock IServiceProvider

### Singleton Services in Actors

For stateless services, inject directly (no scope needed):

```csharp
public sealed class NotificationActor : ReceiveActor
{
    private readonly IEmailLinkGenerator _linkGenerator;  // Singleton - OK!
    private readonly IActorRef _mailingActor;

    public NotificationActor(
        IEmailLinkGenerator linkGenerator,  // Direct injection
        IRequiredActor<MailingActor> mailingActor)
    {
        _linkGenerator = linkGenerator;
        _mailingActor = mailingActor.ActorRef;

        Receive<SendWelcomeEmail>(Handle);
    }
}
```

### Akka.DependencyInjection Reference

- **Akka.DependencyInjection**: https://getakka.net/articles/actors/dependency-injection.html
- **Akka.Hosting**: https://github.com/akkadotnet/Akka.Hosting

---

## Akka.Hosting TestKit Integration

```csharp
public class OrderActorSpecs : Akka.Hosting.TestKit.TestKit
{
    protected override void ConfigureAkka(AkkaConfigurationBuilder builder, IServiceProvider provider)
    {
        // Reuse production Akka configuration
        builder.AddOrderActors();
    }

    protected override void ConfigureServices(IServiceCollection services)
    {
        // Reuse production service configuration
        services.AddOrderServices();

        // Override only external dependencies
        services.RemoveAll<IPaymentProcessor>();
        services.AddSingleton<IPaymentProcessor, FakePaymentProcessor>();
    }

    [Fact]
    public async Task OrderActor_ProcessesPayment()
    {
        var orderActor = ActorRegistry.Get<OrderActor>();
        orderActor.Tell(new ProcessOrder(orderId));

        ExpectMsg<OrderProcessed>();
    }
}
```

---

## Keyed Services (.NET 8+)

```csharp
public static IServiceCollection AddNotificationServices(this IServiceCollection services)
{
    // Register multiple implementations with keys
    services.AddKeyedSingleton<INotificationSender, EmailNotificationSender>("email");
    services.AddKeyedSingleton<INotificationSender, SmsNotificationSender>("sms");
    services.AddKeyedSingleton<INotificationSender, PushNotificationSender>("push");

    // Resolver that picks the right one
    services.AddScoped<INotificationDispatcher, NotificationDispatcher>();

    return services;
}
```
