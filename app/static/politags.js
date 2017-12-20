"use strict"

let article = document.getElementById("article_container")

let articleObject = {
    "date": "2010-01-30T00:00:00",
    "date_granularity": 12,
    "description": "<img srcset=\"https://d2vry01uvf8h31.cloudfront.net/_processed_/0/0/csm_178405088_4_dunl_546dcd1cc5.jpg 1.5x\" class=\"placeholder-image\" src=\"https://d2vry01uvf8h31.cloudfront.net/_processed_/0/0/csm_178405088_4_dunl_6562388c8b.jpg\" width=\"1110\" height=\"572\" alt=\"\" title=\"178405088_4_dunl\"/>\n\t\t\t\t\t\t\t\t\n\t\t\t\t\t\t\t<p><span id=\"dnn_ctr33769_ArticleDetails_ctl00_lblDescription\" class=\"normalbold\">&#160;&#13; <p align=\"justify\">Naar aanleiding van diverse publicaties in de media, betreffende voormalig wethouder van Dijk en diens handelen in zijn hoedanigheid&#160; van werknemer/directeur van Louppen B.V., heeft de CDA fractie op maandag 12 juni jongstleden een aantal schriftelijke vragen aan het college gesteld. </p></span>&#13; </p><p align=\"justify\">Naar aanleiding van diverse publicaties in de media, betreffende voormalig wethouder van Dijk en diens handelen in zijn hoedanigheid&#160; van werknemer/directeur van Louppen B.V., heeft de CDA fractie op maandag 12 juni jongstleden een aantal schriftelijke vragen aan het college gesteld. </p><p/>&#13; <p><span id=\"dnn_ctr33769_ArticleDetails_ctl00_lblArticle\" class=\"normal\">&#13; <p>Naar aanleiding van diverse publicaties in de media, betreffende voormalig wethouder van Dijk en diens handelen in zijn hoedanigheid&#160; van werknemer/directeur van Louppen B.V., heeft de CDA fractie op maandag 12 juni jongstleden een aantal schriftelijke vragen aan het college gesteld. Als grootste fractie in onze raad, achten wij het onze taak om zo spoedig mogelijk helderheid in deze kwestie te krijgen. Het betrof onder ander de navolgende vragen (met daarachter in het kort de beantwoording via het college):<br/>1.&#160;Kunt U aangeven of de toenmalige coalitie bekend was met de nevenfunctie van de heer van Dijk en zo ja, sinds wanneer? De coalitie werd in januari 2004 op de hoogte gebracht van de nieuwe functie (directeur ad interim sinds november 2003). Binnen het college waren de collega wethouders sinds juli/augustus 2003 op de hoogte van het feit dat de heer van Dijk een functie binnen de Louppen Groep had aanvaard.<br/>2.&#160;Is het correct dat het handelen van de heer van Dijk niet heeft geleid tot financi&#235;le schade, juridische verplichtingen of andere nadelige gevolgen voor de gemeente Vaals?",
    "enrichments": {},
    "location": "Vaals",
    "meta": {
        "_index": "pfl_combined_index",
        "_score": 18.702293,
        "_type": "item",
        "collection": "CDA",
        "highlight": {
            "description": [
                " wethouder <em>van</em> <em>Dijk</em> en diens handelen in zijn hoedanigheid&#160; <em>van</em> werknemer/directeur <em>van</em> Louppen B.V",
                " media, betreffende voormalig wethouder <em>van</em> <em>Dijk</em> en diens handelen in zijn hoedanigheid&#160; <em>van</em>",
                ", betreffende voormalig wethouder <em>van</em> <em>Dijk</em> en diens handelen in zijn hoedanigheid&#160; <em>van</em> werknemer/directeur",
                " toenmalige coalitie bekend was met de nevenfunctie <em>van</em> de heer <em>van</em> <em>Dijk</em> en zo ja, sinds wanneer? De coalitie",
                " het feit dat de heer <em>van</em> <em>Dijk</em> een functie binnen de Louppen Groep had aanvaard.<br/>2.&#160;Is het"
            ],
            "title": [
                "\n\t\t\t\t\t\t\t\t51. Dhr. <em>van</em> <em>Dijk</em>\n\t\t\t\t\t\t\t"
            ]
        },
        "original_object_id": "https://www.cda.nl/limburg/vaals/actueel/nieuws/51-dhr-van-dijk-1/",
        "original_object_urls": {
            "html": "https://www.cda.nl/limburg/vaals/actueel/nieuws/51-dhr-van-dijk-1/"
        },
        "pfl_url": "https://api.poliflw.nl/v0/cda_archives_vaals/0ccfc69dba4a64e3cf3a5fd1ca1faa0446a24843",
        "processing_finished": "2017-12-07T23:39:30.990206",
        "processing_started": "2017-12-07T21:06:51.056808",
        "rights": "Undefined",
        "source_id": "cda_archives_vaals"
    },
    "parties": [
        "CDA"
    ],
    "source": "Partij nieuws",
    "title": "\n\t\t\t\t\t\t\t\t51. Dhr. van Dijk\n\t\t\t\t\t\t\t",
    "type": "Partij"
}


console.log(articleObject)


//On click we call the API to receive the question

$(function() {
    $.ajax({
        type: "POST",
        contentType: "application/json",
        url: "http://localhost:5555/api/articles/questions",
        data: JSON.stringify(articleObject),
        success: function (response) {
            printQuestionAnswers(response)
            console.log(response)
        },
        error: function (error) {
            console.log(error);
        }
    })
})


function printQuestionAnswers(response) {
    let message = "Question is: "
    message = message.concat(response["question"])
    message = message.concat(" And possible answers are:")
    message = message.concat(response["possible_answers"])
    hiliter(response["text"], article, response["question_id"])
    article.append(message)
}


$('#yes').click(function() {
    let answer = {"response" : "yes"}
    postAnswer(answer)
})

$('#no').click(function() {
    let answer = {"response" : "no"}
    postAnswer(answer)
})


function postAnswer(answer, questionId) {
    $.ajax({
        type: "POST",
        contentType: "application/json",
        url: "http://localhost:5555/api/questions/" + questionId,
        data: JSON.stringify(answer),
        success: function (response) {
            console.log(response)
        },
        error: function (error) {
            console.log(error);
        }
    })

}

//this function highlights a word in the text using bootstrap's mark
function hiliter(word, element, questionId) {
    var regexp = new RegExp(word, 'g');
    var replace = '<mark id="'+ questionId + '">' + word + '</mark>';
    element.innerHTML = element.innerHTML.replace(regexp, replace);
}



