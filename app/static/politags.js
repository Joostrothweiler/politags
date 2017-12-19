"use strict"

// $(document).ready(function(){
//     $('[data-toggle="popover"]').popover()
// })

// alert("this is javascript");

//need to get the article id from the dom


let article = document.getElementById("article_container")
let articleId = article.getAttribute("article_id")

console.log(articleId)

// var xhttp = new XMLHttpRequest()
// xhttp.open("POST", "http://localhost:5555/api/articles/questions", true)
// xhttp.setRequestHeader("Content-type", "application/json")
// xhttp.send(articleId)
// console.log(xhttp.responseText)
// var response = JSON.parse(xhttp.responseText)
//
// alert(response)


$(document).ready(function() {
    $.ajax({
        type: "POST",
        dataType: "json",
        url: "http://localhost:5555/api/articles/questions",
        data: articleId,
        success: function () {
            console.log('hi')
        }
    })
})