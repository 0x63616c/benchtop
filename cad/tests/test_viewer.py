"""Nested viewer groups and relative animation path resolution."""

from build123d import Box, Pos

from splitflap_cad.viewer import Scene


def test_nested_group_keeps_tree_name_and_location():
    child = Scene().add(Box(1, 2, 3), "part", color="orange")
    root = Scene().add_group(child, "moving", loc=Pos(4, 5, 6))
    group = root.show_args()["objects"][0]
    assert group.name == "moving"
    assert group[0].name == "part"
    assert group.loc is not None


def test_animation_resolves_unique_relative_path(monkeypatch):
    calls = []

    class FakeAnimation:
        paths = ["/nas-storage/bay-1/moving", "/nas-storage/bay-1/moving/door"]

        def add_track(self, path, action, times, values):
            calls.append((path, action, times, values))

        def animate(self, speed):
            calls.append(("animate", speed))

    monkeypatch.setattr("ocp_vscode.Animation", FakeAnimation)
    monkeypatch.setattr("ocp_vscode.set_port", lambda port: calls.append(("port", port)))
    scene = Scene().track("bay-1/moving/door", "rz", (0, 1), (0, -28))
    scene.play_animation(3939)

    assert calls == [
        ("port", 3939),
        ("/nas-storage/bay-1/moving/door", "rz", [0, 1], [0, -28]),
        ("animate", 1.0),
    ]
