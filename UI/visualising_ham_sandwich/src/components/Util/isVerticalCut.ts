export function isVerticalCut(
    cut: any
): cut is { is_vertical: boolean; x_intercept: number | null } {
    return typeof cut === "object" && cut !== null && "is_vertical" in cut;
}