"""Scene — what a model looks like in the viewer.

One abstraction replaces the hand-maintained parallel
objects/names/colors/alphas lists (which silently desync): builders
`add()` each display object with its styling in one call, `show_args()`
produces the kwargs for ocp_vscode.show().
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class AnimationTrack:
    """One relative ocp-vscode animation track within a Scene hierarchy."""

    target: str
    action: str
    times: tuple[float, ...]
    values: tuple


@dataclass
class Scene:
    _objects: list = field(default_factory=list)
    _names: list = field(default_factory=list)
    _colors: list = field(default_factory=list)
    _alphas: list = field(default_factory=list)
    _tracks: list[AnimationTrack] = field(default_factory=list)
    _animation_speed: float = 1.0

    def add(self, obj, name: str, color: str | None = None, alpha: float = 1.0, loc=None):
        """Add one display object; loc (a Location/Pos/Rot) poses it."""
        self._objects.append(loc * obj if loc is not None else obj)
        self._names.append(name)
        self._colors.append(color)
        self._alphas.append(alpha)
        return self

    def add_group(self, scene: "Scene", name: str, loc=None):
        """Add a nested, independently movable group to the viewer tree."""
        from ocp_tessellate import Color, OCP_Part, OCP_PartGroup

        children = []
        for obj, child_name, color, alpha in zip(
            scene._objects,
            scene._names,
            scene._colors,
            scene._alphas,
            strict=True,
        ):
            if isinstance(obj, OCP_PartGroup):
                obj.name = child_name
                children.append(obj)
                continue
            if color is None:
                raise ValueError(f"group child {child_name!r} needs a color")
            children.append(
                OCP_Part(
                    obj.wrapped,
                    name=child_name,
                    color=Color(color, alpha),
                )
            )

        group_loc = None if loc is None else loc.wrapped
        self._objects.append(OCP_PartGroup(children, name=name, loc=group_loc))
        self._names.append(name)
        self._colors.append(None)
        self._alphas.append(1.0)
        return self

    def track(self, target: str, action: str, times, values):
        """Animate the unique group/object path ending in ``target``."""
        self._tracks.append(
            AnimationTrack(target, action, tuple(times), tuple(values))
        )
        return self

    def animation_speed(self, speed: float):
        self._animation_speed = speed
        return self

    def play_animation(self, port: int):
        """Resolve relative paths after show(), then start the animation."""
        if not self._tracks:
            return

        import io
        from contextlib import redirect_stdout

        from ocp_vscode import Animation, set_port

        set_port(port)
        # Animation() prints every viewer path. Large grouped models can have
        # hundreds, so keep the live-view log focused on actionable output.
        with redirect_stdout(io.StringIO()):
            animation = Animation()
        for track in self._tracks:
            suffix = f"/{track.target.strip('/')}"
            matches = [path for path in animation.paths if path.endswith(suffix)]
            if len(matches) != 1:
                raise ValueError(
                    f"animation target {track.target!r} matched {matches or 'nothing'}"
                )
            animation.add_track(
                matches[0], track.action, list(track.times), list(track.values)
            )
        animation.animate(self._animation_speed)

    def show_args(self) -> dict:
        """kwargs for ocp_vscode.show(). colors included only when used;
        a scene that colors anything must color everything (no silent
        positional mismatches)."""
        kwargs = dict(objects=self._objects, names=self._names)
        if any(c is not None for c in self._colors):
            missing = [n for n, c in zip(self._names, self._colors) if c is None]
            assert not missing, f"scene colors some objects but not: {missing}"
            kwargs["colors"] = self._colors
        if any(a != 1.0 for a in self._alphas):
            kwargs["alphas"] = self._alphas
        return kwargs
