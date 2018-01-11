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

//On opening the website we call the API to receive the question
$(getQuestion());


function getQuestion() {
    /**
     * Gets the question for the current article by calling the Politags API and updates html accordingly
     */
    $.ajax({
        type: "POST",
        contentType: "application/json",
        url: "http://localhost:5555/api/articles/questions",
        data: JSON.stringify(articleObject),

        success: function (response) {
            console.log(response);
            if ($.isEmptyObject(response['error']) === true) {

                let question = response['question'];
                let questionId = response['question_id'];
                let possibleAnswers = response['possible_answers'];
                let entityText = response['text'];
                let countResponses = response['count_responses'];

                highlightEntity(article, entityText, questionId);
                renderQuestion(question, questionId, possibleAnswers);
                updateCounter(countResponses)
            }
            else {
                updateCounter(response['count_responses']);
                console.log(response['error'])
            }
        },

        error: function (error) {
            console.log(error);
        }
    })
}


// this function posts the answer to a certain question
function postResponse(response, questionId) {
    /**
     * Posts a response to the politags API
     * @param: response: the response to a question
     * @param: questionId: the question that response answers
     */
    $.ajax({
        type: "POST",
        contentType: "application/json",
        url: "http://localhost:5555/api/questions/" + questionId,
        data: JSON.stringify(response),
        success: function (response) {
            console.log(response);
            updateCounter();
            showFeedback()
        },
        error: function (error) {
            console.log(error);
        }
    })


}

/**
 * This piece of code checks for a click on the responseButton class and posts the response to politags
 */
$('body').on('click', '.responseButton', function () {
        let response = $(this).attr("id");
        let questionId = $(this).attr("question_id");
        postResponse(response, questionId)
    }
);


function highlightEntity(element, entity, questionId) {
    /**
     * This function highlights an entity in a given html element and saves the question we want to ask for this entity
     * @param: element: the element in which we want to highlight the entity
     * @param: entity: the entity we want to highlight
     * @param: questionId: the questionId we want to store in the highlight so we know later on where to render the question
     */
    let regexp = new RegExp(entity);
    let replace = '<mark id="' + questionId + '" style="background-color: transparent !important;\n' +
        '            background-image: linear-gradient(to bottom, rgba(189, 228, 255, 1), rgba(189, 228, 255, 1));\n' +
        '            border-radius: 5px;"><strong>' + entity + '</strong></mark>';
    element.innerHTML = element.innerHTML.replace(regexp, replace)
}


function renderQuestion(question, questionId, possibleAnswers) {
    /**
     * This function renders a question in the html and presents the possible answers
     * @param: question: the question and its metadata
     * @param: questionId: the id for the question
     * @param: possibleAnswers: the possible answers for this question
     */
    let buttonsHtml = generatePolarButtons(questionId, possibleAnswers);

    $('#' + questionId).parent().after(
        '<div id = "question" class="panel panel-danger" style="margin-top: 5px; margin-bottom: 5px; padding-top: 0px; padding-bottom: 15px; border-radius: 1em; text-align: center; box-shadow: none; border-width: 3px">' +
        '   <div id="text" class="panel-body">' + question +
        '   </div>' +
        buttonsHtml +
        '</div>'
    )
}


function updateCounter(countResponses) {
    /**
     * This function updates the counter based on the amount of recorded responses
     * @param: countResponses: the total amount of responses in the politags database
     */
    let count = $('#count').text();

    if ($.isEmptyObject(count)) {
        $('#count').text(countResponses.toString())
    }
    else {
        let countInt = parseInt(count);
        $('#count').html((countInt + 1).toString())
    }

    blinkHeart()
}

function blinkHeart() {
    /**
     * this function blinks the heart in the counter
     */
    $('#counter-heart').addClass("fa-heart").removeClass("fa-heart-o");

    setTimeout(function () {
        $('#counter-heart').addClass("fa-heart-o").removeClass("fa-heart")
    }, 1000)
}


function generatePolarButtons(questionId, possibleAnswers) {
    /**
     * This function generates the HTML buttons for a polar question
     * @param: questionId: id of the question
     * @param: possibleAnswers: the possible answers one can pass to the politags api
     */
    let buttonsHtml = '';

    buttonsHtml += '<button id=' + possibleAnswers[0]['id'] + ' question_id=' + questionId + ' type="button" class="btn btn-success responseButton">JA&nbsp</button>\n';
    buttonsHtml += '<button id=' + possibleAnswers[1]['id'] + ' question_id=' + questionId + ' type="button" class="btn btn-danger responseButton">NEE</button>\n';

    return buttonsHtml
}


function showFeedback() {
    /**
     * This function performs all the actions to show feedback when a question is responded to
     */
    $('#question').removeClass('panel-danger').addClass('panel-success');
    $('.responseButton').remove();
    $('#text').html('Awesome! Samen maken we politiek nieuws beter doorzoekbaar!').after('<i class="fa fa-heart-o fa-2x text-danger">');

    setTimeout(function () {
        $('mark').contents().unwrap();
        $('strong').contents().unwrap();
        $('#question').slideUp("swing", function () {
            $(this).remove()
        })
    }, 4000)

}

