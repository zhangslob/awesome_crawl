package util

import (
	"os"
	"os/user"
	"path/filepath"
	"regexp"
	"strings"
)

func FilterFilename(name string) string {
	name = strings.TrimSpace(name)
	reg, err := regexp.Compile("[\\\\/:*?\"<>| ]")
	if err != nil {
		return name
	}
	return reg.ReplaceAllString(name, "_")
}

func ParseHomeDir(path string) string {
	if strings.Index(path, "~") != 0 {
		return path
	}
	u, err := user.Current()
	if err != nil {
		return path
	}
	return u.HomeDir + path[1:]
}

func FileExists(file string) (bool, error) {
	_, err := os.Stat(file)
	if err == nil {
		return true, nil
	}
	if os.IsNotExist(err) {
		return false, nil
	}
	return false, err
}

func SliceContains(s []string, elem string) bool {
	for _, v := range s {
		if elem == v {
			return true
		}
	}
	return false
}

func IsDir(file string) (bool, error) {
	s, err := os.Stat(file)
	if err != nil {
		return false, err
	}
	return s.IsDir(), nil
}

func CurrentDir() (string, error) {
	dir, err := filepath.Abs(filepath.Dir(os.Args[0]))
	if err != nil {
		return "", err
	}
	return strings.Replace(dir, "\\", "/", -1), nil
}









