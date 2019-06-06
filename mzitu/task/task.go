package task

import (
	"github.com/zhangslob/mzitu/config"
	"io"
	"math/rand"
	"net/http"
	"time"
)

type Task struct {
	Url 		string
	Referer 	string
	Retry 		int
}

func NewTask(url string) *Task {
	return &Task{
		Url: url,
	}
}

func (t *Task) Request() (io.Reader, error) {
	client := &http.Client{}
	req, err := http.NewRequest("GET", t.Url, nil)
	if err != nil {
		return nil, err
	}

	r := rand.New(rand.NewSource(time.Now().UnixNano()))
	req.Header.Set("Accept-Language", "zh-CN,zh;q=0.8")
	req.Header.Set("User-Agent", config.UserAgents[r.Intn(len(config.UserAgents))])
	if t.Referer != "" {
		req.Header.Set("Accept", "image/webp,image/*,*/*;q=0.8")
		req.Header.Set("Referer", t.Referer)
	} else {
		req.Header.Set("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8")
		req.Header.Set("Cache-Control", "max-age=0")
		req.Header.Set("Referer", config.BaseURL)
	}

	if resp, err := client.Do(req); err != nil {
		return nil, err
	} else {
		return resp.Body, nil
	}
}








