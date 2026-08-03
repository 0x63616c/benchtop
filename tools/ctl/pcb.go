package main

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
)

// Every board is its own atopile project. Placement/routing is python
// (tools/place_and_render.py), and DRC, renders, gerbers and the GLB all come
// from kicad-cli. The registry gives the TUI a project -> board hierarchy.

const kicadCLIPath = "/Applications/KiCad.app/Contents/MacOS/kicad-cli"

type pcbBoardDef struct {
	Name    string
	Project string
	Help    string
}

var pcbBoards = []pcbBoardDef{
	{Name: "driver-board", Project: "split-flap", Help: "28BYJ-48 driver board v1"},
	{Name: "driver-board-nema", Project: "split-flap", Help: "NEMA 14 / TMC2209 driver board v2"},
	{Name: "blinds-board", Project: "blinds", Help: "roller-blind driver + snap-off hall tab"},
}

func findPCBBoard(name string) (pcbBoardDef, bool) {
	for _, board := range pcbBoards {
		if board.Name == name {
			return board, true
		}
	}
	return pcbBoardDef{}, false
}

// requestedPCBBoard resolves an explicit CLI board first, then PCB_BOARD, then
// the historical driver-board default. Registry validation makes a typo fail
// clearly instead of becoming a path to a half-existent board.
func requestedPCBBoard(explicit string) (string, error) {
	name := explicit
	if name == "" {
		name = os.Getenv("PCB_BOARD")
	}
	if name == "" {
		name = "driver-board"
	}
	if _, ok := findPCBBoard(name); !ok {
		names := make([]string, len(pcbBoards))
		for i, board := range pcbBoards {
			names[i] = board.Name
		}
		return "", fmt.Errorf("unknown PCB board %q (have: %s)", name, strings.Join(names, ", "))
	}
	return name, nil
}

func pcbDir(root, board string) string { return filepath.Join(root, "pcb", board) }

func pcbFile(root, board string) string {
	return filepath.Join(pcbDir(root, board), "layouts", "default", "default.kicad_pcb")
}

// kicadCLI prefers the app bundle (the cask half-installs — the binary is
// there but never gets symlinked onto PATH), then falls back to PATH.
func kicadCLI() (string, error) {
	if _, err := os.Stat(kicadCLIPath); err == nil {
		return kicadCLIPath, nil
	}
	if p, err := exec.LookPath("kicad-cli"); err == nil {
		return p, nil
	}
	return "", fmt.Errorf("kicad-cli not found — install with: brew install --cask kicad")
}

// pcbBuild runs the one-shot script: place -> DRC -> renders -> gerbers.
// quick stops after DRC, skipping the raytracer.
func pcbBuild(root, board string, quick bool) *exec.Cmd {
	args := []string{}
	if quick {
		args = append(args, "--quick")
	}
	cmd := exec.Command(filepath.Join(pcbDir(root, board), "tools", "build_outputs.sh"), args...)
	cmd.Dir = pcbDir(root, board)
	cmd.Env = append(os.Environ(), "PYTHONUNBUFFERED=1")
	return cmd
}

// pcbPlace re-runs placement/routing only — the fast inner loop, no kicad.
func pcbPlace(root, board string) *exec.Cmd {
	cmd := exec.Command(atoPython(), filepath.Join(pcbDir(root, board), "tools", "place_and_render.py"))
	cmd.Dir = pcbDir(root, board)
	cmd.Env = append(os.Environ(), "PYTHONUNBUFFERED=1")
	return cmd
}

// atoPython is atopile's interpreter — it bundles faebryk, which owns the
// kicad file format reader/writer the placement script uses.
func atoPython() string {
	home, err := os.UserHomeDir()
	if err != nil {
		return "python3"
	}
	return filepath.Join(home, ".local", "share", "uv", "tools", "atopile", "bin", "python")
}

// exportGLB writes the board as binary glTF for the 3D viewer.
func exportGLB(root, board, dest string) error {
	cli, err := kicadCLI()
	if err != nil {
		return err
	}
	out, err := exec.Command(cli, "pcb", "export", "glb",
		"-o", dest, "--include-tracks", "--include-pads", "--include-zones",
		"--subst-models", pcbFile(root, board)).CombinedOutput()
	if err != nil {
		return fmt.Errorf("glb export: %v — %s", err, out)
	}
	return nil
}

func runPcb(args []string) error {
	// just's `pcb cmd=""` default passes an empty string — treat as no args
	if len(args) == 0 || args[0] == "" {
		return runPcbMenu()
	}
	root, err := repoRoot()
	if err != nil {
		return err
	}
	passthru := func(cmd *exec.Cmd) error {
		cmd.Stdout, cmd.Stderr, cmd.Stdin = os.Stdout, os.Stderr, os.Stdin
		return cmd.Run()
	}
	explicitBoard := ""
	if len(args) > 1 {
		explicitBoard = args[1]
	}
	board, err := requestedPCBBoard(explicitBoard)
	if err != nil {
		return err
	}
	switch args[0] {
	case "view":
		return runPcbView(board)
	case "build":
		return passthru(pcbBuild(root, board, false))
	case "drc":
		return passthru(pcbBuild(root, board, true))
	case "place":
		return passthru(pcbPlace(root, board))
	default:
		return fmt.Errorf("unknown pcb command %q (have: view, build, drc, place)", args[0])
	}
}
