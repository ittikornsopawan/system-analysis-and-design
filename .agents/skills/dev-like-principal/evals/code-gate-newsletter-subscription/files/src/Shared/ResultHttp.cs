using Microsoft.AspNetCore.Mvc;
namespace Shop.Shared;

/// <summary>One mapping from Result to HTTP so status codes stay consistent across controllers.</summary>
public static class ResultHttp
{
    public static IActionResult ToHttp<T>(Result<T> result, int successStatus) =>
        result.IsSuccess
            ? new ObjectResult(result.Value) { StatusCode = successStatus }
            : new ObjectResult(new { errors = result.Errors }) { StatusCode = StatusFor(result.Errors[0].Type) };

    private static int StatusFor(ErrorType type) => type switch
    {
        ErrorType.Validation => 400,
        ErrorType.Rule => 422,
        ErrorType.NotFound => 404,
        _ => 409
    };
}
