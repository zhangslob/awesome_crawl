package store

import (
	"bytes"
	"fmt"
	"github.com/labstack/gommon/log"
	"io"
	"io/ioutil"
	"os"
	"path/filepath"
	"strings"
)

type (
	Store interface {
		Save(data io.Reader, fileName string) error
	}

	FileStore struct {
		Store
		SavePath string
	}
)

func (f FileStore) Save(data io.Reader, fileName string) error {
	body, err := ioutil.ReadAll(data)
	if err != nil {
		return fmt.Errorf("read data failed: %s", err.Error())
	}

	fullPath := filepath.Join(f.SavePath, fileName)
	parentDir := fullPath[0:strings.LastIndex(fullPath, "/")]
	err = os.MkdirAll(parentDir, 0777)
	if err != nil {
		return fmt.Errorf("create directory failed: %s", err.Error())
	}

	out, err := os.Create(fullPath)
	if err != nil {
		return fmt.Errorf("create file failed: %s", err.Error())
	}

	bs, err := io.Copy(out, bytes.NewReader(body))
	if err != nil {
		return fmt.Errorf("save file failed: %s", err.Error())
	}

	log.Printf("Saved file [%d bytes] %s", bs, fileName)
	return nil
}







