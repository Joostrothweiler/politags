"use strict";

let article = document.getElementById("article_container");

let articleObject =
   {
      "date": "2017-12-01T00:00:00",
      "date_granularity": 12,
      "description": "<div class=\"node-content clearfix\"> &#13;\n  &#13;\n\t <p>Afgelopen dinsdag besloot de gemeenteraad om eindelijk een fatsoenlijk tarief te gaan betalen voor de huishoudelijke zorg.<br/>\nAlle gemeenten moeten per 1 april 2018 aan thuiszorgorganisaties het in de cao geregelde loon vergoeden van de bij hen werkende thuiszorgmedewerkers.</p>\n<p>Dankzij talrijke acties in het hele land&#160; - ook in Amersfoort met steun vanuit de lokale SP-afdeling -&#160; is dit resultaat bereikt:&#160; eindelijk &#8220;loon naar werken!&#8220;.</p>\n<p>SP-raadslid Bets Beltman maakte tijdens de raadsvergadering van de gelegenheid gebruik om de thuiszorg-medewerkers in Amersfoort te feliciteren met hun succes. Dit werd haar door de andere partijen niet echt in dank afgenomen &#8211; het was toch &#8216;maar een hamerstuk &#8216; en&#160; zij wilden liever wat vroeger naar huis&#8230;.</p>\n<p>Ook de wethouder, Fleur Imming van de PvdA,&#160; hield zich stil.</p>\n         <div class=\"zie-ook\">&#13;\n      <strong>Zie ook:</strong>&#13;\n      <ul>&#13;\n                            <li><a href=\"/dossier/thuiszorg\">Dossier: Thuiszorg</a></li>&#13;\n              </ul>&#13;\n    </div>&#13;\n    </div>&#13;\n&#13;\n\t\t\n",
      "enrichments": {},
      "location": "Amersfoort",
      "meta": {
        "pfl_url": "https://api.poliflw.nl/v0/cda_archives_vaals/4e8f2c46403d40023c701c94455eb7c502c16593",
        "collection": "SP",
        "original_object_id": "http://amersfoort.sp.nl/nieuws/2017/12/succes-thuiszorg-acties-ook-in-amersfoort-verzilverd",
        "original_object_urls": {
          "html": "http://amersfoort.sp.nl/nieuws/2017/12/succes-thuiszorg-acties-ook-in-amersfoort-verzilverd"
        },
        "processing_finished": "2017-12-05T20:56:11.729632",
        "processing_started": "2017-12-05T20:24:15.921745",
        "rights": "Undefined",
        "source_id": "sp_archives_amersfoort"
      },
      "parties": [
        "SP"
      ],
      "source": "Partij nieuws",
      "title": "SUCCES THUISZORG-ACTIES OOK IN AMERSFOORT VERZILVERD!",
      "type": "Partij"
    };

//On click we call the API to receive the question

$(getQuestion())

function getQuestion() {
    $.ajax({
        type: "POST",
        contentType: "application/json",
        url: "http://localhost:5555/api/articles/questions",
        data: JSON.stringify(articleObject),
        success: function (response) {
            console.log(response);
            if ($.isEmptyObject(response['error']) === true)  {
                showQuestion(response)
            }
            else {
                console.log(response['error'])
            }
        },
        error: function (error) {
            console.log(error);
        }
    })
}

// this function posts the answer to a certain question
function postResponse(questionResponse, questionId) {
    $.ajax({
        type: "POST",
        contentType: "application/json",
        url: "http://localhost:5555/api/questions/" + questionId,
        data: JSON.stringify(questionResponse),
        success: function (response) {
            console.log(response);
            showFeedback()
        },
        error: function (error) {
            console.log(error);
        }
    })

}


function showQuestion(apiresponse) {
    let question = apiresponse['question'];
    let questionId = apiresponse['question_id'];
    let possibleAnswers = apiresponse['possible_answers'];
    let entityText = apiresponse['text'];

    highlighter(article, entityText, questionId);
    appendDiv(questionId, question, possibleAnswers)
}


// this function highlights a word in the text using bootstrap's mark
function highlighter(element, word, questionId) {
    var regexp = new RegExp(word);
    var replace = '<mark id="' + questionId + '"><strong>' + word + '</strong></mark>';
    element.innerHTML = element.innerHTML.replace(regexp, replace)
}

function appendDiv(questionId, question, possibleAnswers) {
    let buttonsHtml = generateButtons(questionId, possibleAnswers);

    $('#' + questionId).parent().after(
        '<div id = "yesnoquestion" class="panel panel-danger" style="margin-top: 5px; margin-bottom: 5px; padding-top: 0px; padding-bottom: 15px; border-radius: 1em; text-align: center; box-shadow: none; border-width: 3px">' +
        '   <div id="text" class="panel-body">' + question +
        '   </div>' +
        buttonsHtml +
        '</div>'
    )
}


function generateButtons(questionId, possibleAnswers) {
    let buttonsHtml = '';

    if (possibleAnswers.length == 2) {
        buttonsHtml += '<button id='+ possibleAnswers[0]['id'] +' question_id='+ questionId +' type="button" class="btn btn-success responseButton">JA&nbsp</button>\n'
        buttonsHtml += '<button id='+ possibleAnswers[1]['id'] +' question_id='+ questionId +' type="button" class="btn btn-danger responseButton">NEE</button>\n'
    }

    return buttonsHtml
}


$('body').on('click', '.responseButton', function () {
    let response = $(this).attr("id");
    let questionId = $(this).attr("question_id");
    postResponse(response, questionId)
    }
);


function showFeedback() {
    $('#yesnoquestion').removeClass('panel-danger').addClass('panel-success')
    $('.responseButton').remove()
    $('#text').text('Bedankt! Door jouw bijdrage wordt politiek nieuws transparanter!').after('<i class="fa fa-heart-o text-danger" style="font-size: 25px"><i>')
    setTimeout(function() {
        $('mark').contents().unwrap()
        $('strong').contents().unwrap()
        $('#yesnoquestion').slideUp("swing", function() {
            $(this).remove()
        })
    }, 3000)

}

