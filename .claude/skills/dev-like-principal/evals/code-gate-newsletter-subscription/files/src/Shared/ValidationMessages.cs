namespace Shop.Shared;

/// <summary>The standard 400 message forms, so every endpoint words validation failures the same way.</summary>
public static class ValidationMessages
{
    public static string Required(string field) => $"{field} is required.";
    public static string MaxLength(string field, int max) => $"{field} must be at most {max} characters.";
    public static string Email(string field) => $"{field} must be a valid email address.";
}
