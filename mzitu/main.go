package main

import (
	"flag"
	"fmt"
	"github.com/zhangslob/mzitu/store"
	"github.com/zhangslob/mzitu/task"
	"github.com/zhangslob/mzitu/util"
	"log"
	"os"
	"os/signal"
	"path/filepath"
	"strconv"
	"strings"
	"sync"
	"syscall"
	"time"

	"github.com/PuerkitoBio/goquery"

	"github.com/zhangslob/mzitu/config"

)

var (
	wg                 sync.WaitGroup
	taskChan           = make(chan *task.Task, config.MaxAcceptURLCount)
	imgStore           store.Store
	failURLStore       store.URLStore
	failedURLContainer = util.NewBloomContainer()
	stopAcceptFlag     = false

	path          = ""
	channel       = ""
	page          = 0
	channelLabel  = ""
	failedURLFile = ""
	urlFile       = ""
)

func init() {
	menu := ""
	for k, v := range config.Channels {
		t := k
		if t == "" {
			t = "默认"
		}
		menu += t + ": " + v + "\n"
	}

	flag.StringVar(&path, "path", "", "图片保存目录路径（如 /usr/image、E:\\image）")
	flag.StringVar(&channel, "channel", "", "抓取内容类别编码\n"+menu)
	flag.IntVar(&page, "page", 0, "起始抓取页码")
	flag.StringVar(&failedURLFile, "failedURLFile", "", "请求失败的链接保存的文件路径")
	flag.StringVar(&urlFile, "urlFile", "", "要加载的链接文件路径，按行存储")
}

func main() {
	flag.Parse()

	c := make(chan os.Signal)
	signal.Notify(c, os.Interrupt, os.Kill, syscall.SIGUSR1, syscall.SIGUSR2)
	go func() {
		<-c
		stopAcceptFlag = true
		fmt.Println("接收到中断操作，正在等待剩余任务完成，保存数据....")
		exit()
	}()

	path = util.ParseHomeDir(strings.TrimSpace(path))
	if path == "" {
		log.Fatal("请指定保存目录路径")
	}
	if _, err := os.Stat(path); err != nil {
		if os.IsNotExist(err) {
			if err = os.MkdirAll(path, 0777); err != nil {
				log.Fatal("保存目录路径错误：", path)
			}
		}
	}

	// 失败链接存储文件没有指定，则使用程序默认数据文件
	if failedURLFile == "" {
		if currentDir, err := util.CurrentDir(); err != nil {
			log.Fatal("获取当前目录失败")
		} else {
			parentDir := filepath.Join(currentDir, config.DefaultDataFolderName)
			if err = os.MkdirAll(parentDir, 0777); err != nil {
				log.Fatal("创建数据目录失败：", parentDir)
			}
			failedURLFile = filepath.Join(parentDir, config.DefaultFailedURLFileName)
			if _, err := os.Create(failedURLFile); err != nil {
				log.Fatal("创建失败链接存储文件发生错误：", failedURLFile)
			}
			fmt.Println("失败链接存储文件：", failedURLFile)
		}
	}

	if exists, _ := util.FileExists(failedURLFile); !exists {
		log.Fatal("失败链接存储文件错误或不存在")
	}
	failURLStore = store.URLFileStore{
		FilePath: failedURLFile,
	}

	log.Println("-------START!-------")

	// 是否从外部文件加载链接
	var loadFormFile = false

	// 加载失败 URL 重新抓取，指定 -r 参数
	if util.SliceContains(os.Args, "-r") {
		if urls, err := failURLStore.ReadAll(); err != nil {
			log.Fatal("读取失败链接存储文件失败")
		} else {
			log.Println("正在从失败链接存储文件中恢复抓取任务...")
			for _, u := range urls {
				if u != "" {
					fmt.Println("Loading failed URL: ", u)
					taskChan <- task.NewTask(u)
				}
			}
			loadFormFile = true
		}
	} else if urlFile != "" {
		if exists, _ := util.FileExists(urlFile); !exists {
			log.Fatal("请求失败的链接保存的文件错误或不存在")
		}
		urlStore := store.URLFileStore{
			FilePath: urlFile,
		}
		if urls, err := urlStore.ReadAll(); err != nil {
			log.Println("正在从外部链接存储文件中获取抓取任务...")
			for _, u := range urls {
				if u != "" {
					fmt.Println("Loading URL: ", u)
					taskChan <- task.NewTask(u)
				}
			}
			loadFormFile = true
		}
	}

	// 如果从外部文件加载，就不从默认 URL 执行
	if !loadFormFile {
		ok := false
		if channelLabel, ok = config.Channels[channel]; !ok {
			log.Fatal("没有找到指定的频道")
		}

		imgStore = store.FileStore{
			SavePath: filepath.Join(path, channelLabel),
		}

		url := config.BaseURL
		if channel != "" {
			url += channel + "/"
		}
		if page > 0 {
			url += "page/" + strconv.Itoa(page)
		}

		taskChan <- task.NewTask(url)
	}

	run()

	for !failedURLContainer.IsEmpty() {
		fmt.Printf("发现有 %d 条链接请求失败，是否重新抓取？Y/y - [是]", failedURLContainer.Size())
		answer := ""
		_, _ = fmt.Scanln(&answer)
		if "y" == strings.TrimSpace(strings.ToLower(answer)) {
			failedURLs := failedURLContainer.All()
			failedURLContainer.Reset()
			for _, u := range failedURLs {
				taskChan <- task.NewTask(u)
			}
			run()
		} else {
			break
		}
	}

	exit()
}

func run() {
	wg.Add(1)
	go func() {
		defer wg.Done()
		for {
			select {
			case t, ok := <-taskChan:
				if !ok {
					break
				}
				if stopAcceptFlag {
					// save to failed url file
					failedURLContainer.Add(t.Url)
				} else {
					time.Sleep(time.Duration(config.TaskDelayMills) * time.Millisecond)
					wg.Add(1)
					go func(t *task.Task) {
						defer wg.Done()
						execute(t)
					}(t)
				}
			}
		}
	}()
	wg.Wait()
}

func exit() {
	if !failedURLContainer.IsEmpty() && failURLStore != nil {
		fmt.Printf("正在保存请求失败的链接到文件 [%s] 中...\n", failedURLFile)
		if err := failURLStore.Save(failedURLContainer.All()); err != nil {
			fmt.Println("保存失败链接到文件中失败！")
		} else {
			fmt.Println("失败链接保存完毕！")
		}
	}

	log.Println("-------END!-------")
	os.Exit(0)
}

func execute(t *task.Task) {
	body, err := t.Request()
	if err != nil {
		log.Printf(err.Error())
		retry(t)
		return
	}
	doc, err := goquery.NewDocumentFromReader(body)
	if err != nil {
		log.Printf(err.Error())
		retry(t)
		return
	}
	if processGalleryPage(doc, t) {
		return
	}
	if processListPage(doc, t) {
		return
	}
	retry(t)
}

func processGalleryPage(doc *goquery.Document, t *task.Task) bool {
	currentNode := doc.Find(".main-image")
	if currentNode.Size() <= 0 {
		return false
	}

	imgUrl, _ := currentNode.Find("p img").Attr("src")
	desc, _ := currentNode.Find("p img").Attr("alt")
	if imgUrl != "" {
		saveImage(t.Url, imgUrl, util.FilterFilename(desc))
	}

	// 只要第一页的时候才采集所有图片 URL
	selection := doc.Find(".pagenavi>span").First()
	if selection.Text() == "1" {
		selection = doc.Find(".pagenavi").Find("a").Last()
		text := selection.Find("span").Text()
		selection = selection.Prev()
		if strings.TrimSpace(text) == "下一页»" && selection != nil {
			// 获取最后一页的页码
			lastPageStr := selection.Text()
			urlRef, _ := selection.Attr("href")
			lastPageNum, err := strconv.Atoi(lastPageStr)
			if err == nil && urlRef != "" && lastPageNum > 1 {
				urlRef = urlRef[0 : strings.LastIndex(urlRef, "/")+1]
				for i := 2; i <= lastPageNum; i++ {
					nextUrl := urlRef + strconv.Itoa(i)
					//taskChan <- task.NewTask(nextUrl)
					execute(task.NewTask(nextUrl))
				}
			}
		}
	}
	return true
}

func processListPage(doc *goquery.Document, t *task.Task) bool {
	currentNode := doc.Find(".postlist")
	if currentNode.Size() <= 0 {
		return false
	}

	if tags := currentNode.Find("dl.tags"); tags.Size() > 0 {
		curTitle := ""
		tags.Children().Each(func(i int, s *goquery.Selection) {
			if s.Is("dt") {
				curTitle = s.Text()
				return
			}
			a := s.Find("a")
			tagLink, _ := a.Attr("href")
			if tagLink != "" {
				taskChan <- task.NewTask(tagLink)
			}
		})
	} else {
		var index = 0
		var nextPage string
		// 使用此循环方式来避免无法直接获取到 nav 元素
		currentNode.Children().Each(func(i int, s *goquery.Selection) {
			if index == 0 {
				s.Find("li>a").Each(func(idx int, sel *goquery.Selection) {
					detailUrl, exists := sel.Attr("href")
					if !exists || detailUrl == "" {
						return
					}
					detailUrl = strings.TrimPrefix(detailUrl, "/")
					taskChan <- task.NewTask(detailUrl)
				})
			} else if index == 1 {
				nextPage, _ = s.Find(".next").Attr("href")
			}
			index++
		})

		if nextPage == "" {
			log.Println("Page end!", t.Url)
		} else {
			log.Println("Next page ", nextPage)
			taskChan <- task.NewTask(nextPage)
		}
	}
	return true
}

func saveImage(pageUrl, imgUrl, folder string) {
	fragment := strings.TrimPrefix(pageUrl, config.BaseURL)
	fragments := strings.Split(fragment, "/")
	idx := "1"
	fragLen := len(fragments)
	if fragLen == 0 {
		return
	}
	if fragLen > 1 {
		idx = fragments[1]
	}

	respBody, err := (&task.Task{
		Url:     imgUrl,
		Referer: pageUrl,
	}).Request()
	if err != nil {
		return
	}

	folder = strings.TrimSpace(folder) + "_" + fragments[0]
	ext := filepath.Ext(imgUrl)
	if err := imgStore.Save(respBody, filepath.Join(folder, idx+ext)); err != nil {
		log.Printf(err.Error())
	}
}

func retry(t *task.Task) {
	if t.Retry >= config.MaxRetryCount {
		log.Printf("Request timeout %s [SKIP]", t.Url)
		failedURLContainer.Add(t.Url)
		return
	}
	t.Retry++
	time.Sleep(time.Duration(config.RetrySleepSecond) * time.Second)
	taskChan <- t
}