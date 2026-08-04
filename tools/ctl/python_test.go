package main

import "testing"

func TestParseCatalog(t *testing.T) {
	data := []byte(`{"projects":{"split-flap":"modular display"},` +
		`"models":{"assembly":"full unit","holder":"flap jig"},` +
		`"model_projects":{"assembly":"split-flap","holder":"split-flap"},` +
		`"model_sources":{"assembly":"assembly","holder":"holder"},` +
		`"printable":["holder"],"printable_projects":{"holder":"split-flap"},` +
		`"printable_sources":{"holder":"holder"},` +
		`"render_projects":{},"src_to_model":{"holder":"holder","params":""}}`)
	c, err := parseCatalog(data)
	if err != nil {
		t.Fatal(err)
	}
	if c.Projects["split-flap"] != "modular display" ||
		c.Models["holder"] != "flap jig" || c.ModelProjects["holder"] != "split-flap" ||
		c.ModelSources["holder"] != "holder" ||
		c.Printable[0] != "holder" || c.PrintableProjects["holder"] != "split-flap" ||
		c.PrintableSources["holder"] != "holder" ||
		c.SrcToModel["holder"] != "holder" {
		t.Fatalf("bad parse: %+v", c)
	}
}

func TestParseCatalogGarbage(t *testing.T) {
	if _, err := parseCatalog([]byte("not json")); err == nil {
		t.Fatal("want error on garbage")
	}
}
