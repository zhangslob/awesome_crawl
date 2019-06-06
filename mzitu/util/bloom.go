package util

import (
	"github.com/willf/bloom"
	"sync"
)

type bloomContainer struct {
	lock 		sync.RWMutex
	filter		*bloom.BloomFilter
	items		[]string
}

func NewBloomContainer() *bloomContainer {
	n := uint(1000)
	return &bloomContainer{
		filter: bloom.New(20*n, 5),
		items:	[]string{},
	}
}

func (b *bloomContainer) Add(item string) {
	b.lock.Lock()
	defer b.lock.Unlock()
	if !b.filter.TestAndAdd([]byte(item)) {
		b.items = append(b.items, item)
	}
}

func (b *bloomContainer) Reset() {
	b.lock.Lock()
	defer b.lock.Unlock()
	b.filter.ClearAll()
	b.items = []string{}
}

func (b *bloomContainer) All() []string {
	b.lock.Lock()
	defer b.lock.Unlock()
	return b.items
}

func (b *bloomContainer) Size() int {
	b.lock.Lock()
	defer b.lock.Unlock()
	return len(b.items)
}

func (b *bloomContainer) IsEmpty() bool {
	return b.Size() == 0
}

