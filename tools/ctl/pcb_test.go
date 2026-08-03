package main

import (
	"os"
	"path/filepath"
	"testing"
)

func TestPCBRegistryPointsAtProjectsAndBoards(t *testing.T) {
	root, err := repoRoot()
	if err != nil {
		t.Skip("not in a repo")
	}
	cat, err := loadCatalog(root)
	if err != nil {
		t.Fatal(err)
	}
	seen := map[string]bool{}
	for _, board := range pcbBoards {
		if seen[board.Name] {
			t.Fatalf("duplicate PCB board %q", board.Name)
		}
		seen[board.Name] = true
		if cat.Projects[board.Project] == "" {
			t.Fatalf("%s: unknown project %q", board.Name, board.Project)
		}
		if _, err := os.Stat(filepath.Join(pcbDir(root, board.Name), "main.ato")); err != nil {
			t.Fatalf("%s: %v", board.Name, err)
		}
	}
}

func TestRequestedPCBBoardPrecedenceAndValidation(t *testing.T) {
	t.Setenv("PCB_BOARD", "blinds-board")
	if got, err := requestedPCBBoard(""); err != nil || got != "blinds-board" {
		t.Fatalf("environment selection = %q, %v", got, err)
	}
	if got, err := requestedPCBBoard("driver-board-nema"); err != nil || got != "driver-board-nema" {
		t.Fatalf("explicit selection = %q, %v", got, err)
	}
	if _, err := requestedPCBBoard("missing-board"); err == nil {
		t.Fatal("unknown board should fail")
	}
}

func TestPCBPickersGroupBoardsByProject(t *testing.T) {
	root, err := repoRoot()
	if err != nil {
		t.Skip("not in a repo")
	}
	cat, err := loadCatalog(root)
	if err != nil {
		t.Fatal(err)
	}
	projects := pcbProjectScreen("view", cat)
	if projects.id != "pcb-project" || !contains(projects.names, "split-flap") || !contains(projects.names, "blinds") {
		t.Fatalf("PCB project picker = %+v", projects)
	}
	splitFlap := pcbBoardScreen("view", "split-flap")
	if !contains(splitFlap.names, "driver-board") || !contains(splitFlap.names, "driver-board-nema") {
		t.Fatalf("split-flap boards = %v", splitFlap.names)
	}
	if contains(splitFlap.names, "blinds-board") {
		t.Fatal("blinds board leaked into split-flap picker")
	}
	blinds := pcbBoardScreen("view", "blinds")
	if len(blinds.names) != 1 || blinds.names[0] != "blinds-board" {
		t.Fatalf("blinds boards = %v", blinds.names)
	}
}

func TestPCBViewerAssetsCanBeSharedWithoutSharingGLB(t *testing.T) {
	root, err := repoRoot()
	if err != nil {
		t.Skip("not in a repo")
	}
	viewerDir, err := pcbViewerAssetsDir(root, "driver-board-nema")
	if err != nil {
		t.Fatal(err)
	}
	want := filepath.Join(pcbDir(root, "driver-board"), "tools", "viewer")
	if viewerDir != want {
		t.Fatalf("NEMA viewer assets = %q, want shared %q", viewerDir, want)
	}
}
