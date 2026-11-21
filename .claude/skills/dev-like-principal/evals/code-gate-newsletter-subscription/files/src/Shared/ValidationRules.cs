namespace Shop.Shared;

/// <summary>Project-wide input rules shared by every feature, so each rule exists once.</summary>
public static class ValidationRules
{
    public static string NormalizeEmail(string? raw) => (raw ?? string.Empty).Trim().ToLowerInvariant();

    public static bool IsValidEmail(string normalized)
    {
        if (normalized.Length is 0 or > 254) return false;
        var at = normalized.IndexOf('@');
        return at > 0
            && at == normalized.LastIndexOf('@')
            && at < normalized.Length - 1
            && normalized[(at + 1)..].Contains('.');
    }
}
