"""Shared row/box/link builders used by the layered, supporting and domain diagram content."""

SANS, MONO = "sans", "mono"


def row(text, role=SANS):
    return (text, role)


def box(key, x, y, w, h, title, tag, rows, kind="backend", refs=None):
    return dict(id=key, x=x, y=y, w=w, h=h, title=title, tag=tag,
                rows=rows, kind=kind, refs=refs)


def link(source, target, points, label=None, color="muted", dashed=False):
    return dict(source=source, target=target, points=points,
                label=label, color=color, dashed=dashed)
