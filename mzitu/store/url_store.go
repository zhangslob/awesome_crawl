package store

import (
	"bufio"
	"fmt"
	"io"
	"os"
)

type (
	URLStore interface {
		Save(urls []string) error
		ReadAll() ([]string, error)
	}

	URLFileStore struct {
		URLStore
		FilePath string
	}
)

func (u URLFileStore) Save(urls []string) error {
	f, err := os.Create(u.FilePath)
	if err != nil {
		return fmt.Errorf("create file error: %s", err.Error())
	}
	defer func() { _ = f.Close() }()

	w := bufio.NewWriter(f)
	for _, v := range urls {
		lineStr := fmt.Sprintf("%s", v)
		_, _ = fmt.Fprintln(w, lineStr)
	}
	return w.Flush()
}

func (u URLFileStore) ReadAll() ([]string, error) {
	f, err := os.Open(u.FilePath)
	if err != nil {
		return nil, fmt.Errorf("create file err: %s", err.Error())
	}
	defer func() { _ = f.Close() }()

	rd := bufio.NewReader(f)
	var urls []string
	for {
		line, err := rd.ReadString('\n')
		if err != nil || io.EOF == err {
			break
		}
		urls = append(urls, line)
	}
	return urls, nil
}






