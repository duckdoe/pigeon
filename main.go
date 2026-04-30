package main

import "fmt"

func main(){
	numbers := []int{1,2,3}
	for i :=  range 12{
		numbers = append(numbers, i)
	}

	fmt.Println(numbers)
}