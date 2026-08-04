package main

import (
	"bufio"
	"os/exec"
	"strconv"
	"strings"
	"time"
)

type artifactHistory struct {
	Created time.Time
	Updated time.Time
}

// artifactHistories reads every requested path in one git log. File paths
// match exactly; directory paths also match anything beneath the directory.
func artifactHistories(root string, paths map[string]string) map[string]artifactHistory {
	history := make(map[string]artifactHistory, len(paths))
	args := []string{"log", "--format=commit:%ct", "--name-only", "--"}
	seenPath := map[string]bool{}
	for _, path := range paths {
		if path != "" && !seenPath[path] {
			args = append(args, path)
			seenPath[path] = true
		}
	}
	if len(args) == 4 {
		return history
	}
	gitArgs := append([]string{"-C", root}, args...)
	out, err := exec.Command("git", gitArgs...).Output()
	if err != nil {
		return history
	}

	var commitTime time.Time
	scanner := bufio.NewScanner(strings.NewReader(string(out)))
	for scanner.Scan() {
		line := scanner.Text()
		if strings.HasPrefix(line, "commit:") {
			seconds, err := strconv.ParseInt(strings.TrimPrefix(line, "commit:"), 10, 64)
			if err == nil {
				commitTime = time.Unix(seconds, 0)
			}
			continue
		}
		if line == "" || commitTime.IsZero() {
			continue
		}
		for name, path := range paths {
			if line != path && !strings.HasPrefix(line, strings.TrimSuffix(path, "/")+"/") {
				continue
			}
			item := history[name]
			if item.Updated.IsZero() {
				item.Updated = commitTime
			}
			item.Created = commitTime
			history[name] = item
		}
	}
	return history
}

func cadSourcePath(source string) string {
	if source == "" {
		return ""
	}
	if strings.Contains(source, ".") {
		return "cad/" + strings.ReplaceAll(source, ".", "/") + ".py"
	}
	return "cad/splitflap_cad/" + source + ".py"
}

func relativeAge(then, now time.Time) string {
	if then.IsZero() {
		return "—"
	}
	age := now.Sub(then)
	if age < time.Minute {
		return "now"
	}
	switch {
	case age < time.Hour:
		return strconv.Itoa(int(age/time.Minute)) + "m ago"
	case age < 24*time.Hour:
		return strconv.Itoa(int(age/time.Hour)) + "h ago"
	case age < 30*24*time.Hour:
		return strconv.Itoa(int(age/(24*time.Hour))) + "d ago"
	case age < 365*24*time.Hour:
		return strconv.Itoa(int(age/(30*24*time.Hour))) + "mo ago"
	default:
		return strconv.Itoa(int(age/(365*24*time.Hour))) + "y ago"
	}
}
