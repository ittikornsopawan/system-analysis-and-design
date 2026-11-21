namespace Shop.Shared;

public enum ErrorType { Validation, Rule, NotFound, Conflict }

public sealed record Error(string Code, string Message, ErrorType Type);

public class Result
{
    protected Result(IReadOnlyList<Error> errors) => Errors = errors;
    public IReadOnlyList<Error> Errors { get; }
    public bool IsSuccess => Errors.Count == 0;
    public static Result Success() => new([]);
    public static Result Failure(params Error[] errors) => new(errors);
}

public sealed class Result<T> : Result
{
    private Result(T? value, IReadOnlyList<Error> errors) : base(errors) => Value = value;
    public T? Value { get; }
    public static Result<T> Success(T value) => new(value, []);
    public static new Result<T> Failure(params Error[] errors) => new(default, errors);
}
