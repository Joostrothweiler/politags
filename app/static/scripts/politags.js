"use strict"

const LOGGING = true

let article = document.getElementById("article_container");

let articleObject =
    {
        "date": "2017-12-01T00:00:00",
        "date_granularity": 12,
        "description": "<div class=\"node-content clearfix\"> &#13;\n  &#13;\n\t <p>Afgelopen dinsdag besloot de gemeenteraad om eindelijk een fatsoenlijk tarief te gaan betalen voor de huishoudelijke zorg.<br/>\nAlle gemeenten moeten per 1 april 2018 aan thuiszorgorganisaties het in de cao geregelde loon vergoeden van de bij hen werkende thuiszorgmedewerkers.</p>\n<p>Dankzij talrijke acties in het hele land&#160; - ook in Amersfoort met steun vanuit de lokale SP-afdeling -&#160; is dit resultaat bereikt:&#160; eindelijk &#8220;loon naar werken!&#8220;.</p>\n<p>SP-raadslid Bets Beltman maakte tijdens de raadsvergadering van de gelegenheid gebruik om de thuiszorg-medewerkers in Amersfoort te feliciteren met hun succes. Dit werd haar door de andere partijen niet echt in dank afgenomen &#8211; het was toch &#8216;maar een hamerstuk &#8216; en&#160; zij wilden liever wat vroeger naar huis&#8230;.</p>\n<p>Ook de wethouder, Fleur Imming van de PvdA,&#160; hield zich stil.</p>\n         <div class=\"zie-ook\">&#13;\n      <strong>Zie ook:</strong>&#13;\n      <ul>&#13;\n                            <li><a href=\"/dossier/thuiszorg\">Dossier: Thuiszorg</a></li>&#13;\n              </ul>&#13;\n    </div>&#13;\n    </div>&#13;\n&#13;\n\t\t\n",
        "enrichments": {},
        "location": "Amersfoort",
        "id": "4e8f2c46403d40023c701c94455eb7c502c16593",
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


let initialTopics;

$('.js-example').select2 (
    {
        width: 'element',
        theme: 'bootstrap'
    }
);

$('.js-example').on('click' , function() {
 $('select[data-customize-setting-link]').select2("close")
} );

$.fn.select2.amd.require(['select2/selection/search'], function (Search) {
    var oldRemoveChoice = Search.prototype.searchRemoveChoice;

    Search.prototype.searchRemoveChoice = function () {
        oldRemoveChoice.apply(this, arguments);
        this.$search.val('');
    };

    $('#test').select2({
        width:'300px'
    });
});


//On opening the website we call the API to receive the question
$(getQuestion());


/**
 * Gets the question for the current article by calling the Politags API and updates html accordingly
 */
function getQuestion() {
    let apiObject = addCookieIdToObject(articleObject);

    $.ajax({
        type: "POST",
        contentType: "application/json",
        url: "http://localhost:5555/api/articles/questions",
        data: JSON.stringify(apiObject),

        success: function (response) {
            if (LOGGING) {
                console.log("the API response returned by Politags:")
                console.log(response)
            }

            let countResponsesTotal = response['count_verifications'];
            let countResponsesPersonal = response['count_verifications_personal'];
            let countResponsesToday = response['count_verifications_today'];
            updateCounters(countResponsesTotal, countResponsesPersonal, countResponsesToday);

            if ($.isEmptyObject(response['error']) === true) {

                let question = response['question'];
                let questionLinkingId = response['question_linking_id'];
                let possibleAnswers = response['possible_answers'];
                let entityText = response['text'];

                highlightEntity(article, entityText, questionLinkingId);
                renderQuestion(question, questionLinkingId, possibleAnswers)
            }
            else if (LOGGING) {
                console.log(response['error'])
            }

            if (response['topic_response'] == false) {
                fillTopicContainer();

                initialTopics = response['topics'];

                fillSelect2(initialTopics)
            }
            else if (LOGGING) {
                console.log("topic question already answered");
                deleteTopicQuestion()
            }

        },

        error: function (error) {
            if (LOGGING) {
                console.log(error)
            }
        }
    })
}


/**
 * Posts a response to the politags API
 * @param: response: the response to a question
 * @param: questionLinkingId: the question that response answers
 */
function postEntityVerification(response, questionLinkingId) {
    response = addCookieIdToObject(response);

    $.ajax({
        type: "POST",
        contentType: "application/json",
        url: "http://localhost:5555/api/questions/" + questionLinkingId,
        data: JSON.stringify(response),
        success: function (response) {
            if (LOGGING) {
                console.log("This API response was sent to politags:");
                console.dir(response);
            }
            updateCounters();
            showEntityFeedback()
        },
        error: function (error) {
            if (LOGGING) {
                console.log(error);
            }
        }
    })
}


/**
 * Posts a response to the politags API
 * @param: response: the response to a question
 * @param: questionLinkingId: the question that response answers
 */
function postTopicVerification(postedTopics) {
    let topicResponse = generateTopicResponse(initialTopics, postedTopics);

    let response = {
        "topic_response": topicResponse
    };

    let postObject = addCookieIdToObject(response);

    $.ajax({
        type: "POST",
        contentType: "application/json",
        url: "http://localhost:5555/api/topics/" + articleObject.id,
        data: JSON.stringify(postObject),
        success: function () {
            for (let i=0; i<topicResponse.length; i++) {
               updateCounters()
            }
         showTopicFeedback()
        },
        error: function (error) {
            if (LOGGING) {
                console.log(error);
            }
        }
    })
}


/**
 * Adds a list op topics to the select2 item
 * @param topics: topics for the select to be filled with
 */
function fillSelect2(topics) {
    $('.js-example').select2(
        {
            data: topics,
            theme: 'bootstrap',
            width: 'element'
        }
    )
}


/**
 * This function highlights an entity in a given html element and saves the question we want to ask for this entity
 * @param: element: the element in which we want to highlight the entity
 * @param: entity: the entity we want to highlight
 * @param: questionLinkingId: the questionLinkingId we want to store in the highlight so we know later on where to render the question
 */
function highlightEntity(element, entity, questionLinkingId) {
    let regexp = new RegExp(entity);
    let replace = '<mark id="' + questionLinkingId + '" style="background-color: transparent !important;\n' +
        '            background-image: linear-gradient(to bottom, rgba(189, 228, 255, 1), rgba(189, 228, 255, 1));\n' +
        '            border-radius: 5px;"><strong>' + entity + '</strong></mark>';
    element.innerHTML = element.innerHTML.replace(regexp, replace)
}


/**
 * This function renders a question in the html and presents the possible answers
 * @param: question: the question and its metadata
 * @param: questionLinkingId: the id for the question
 * @param: possibleAnswers: the possible answers for this question
 */
function renderQuestion(question, questionLinkingId, possibleAnswers) {
    let buttonsHtml = generatePolarButtons(questionLinkingId, possibleAnswers);

    $('#' + questionLinkingId).parent().after(
        '<div id = "question" class="panel panel-danger" style="margin-top: 5px; margin-bottom: 5px; padding-top: 0px; padding-bottom: 15px; border-radius: 1em; text-align: center; box-shadow: none; border-width: 3px">' +
        '   <div id="text" class="panel-body">' + question +
        '   </div>' +
        buttonsHtml +
        '</div>'
    )
}


/**
 * This function updates the counter based on the amount of recorded verifications
 * @param: countResponses: the total amount of verifications in the politags database
 */
function updateCounters(countResponsesTotal, countResponsesPersonal, countResponsesToday) {
    let counterTotal = $('#response-counter-total');
    let counterPersonal = $('#response-counter-personal');
    let counterToday =  $('#response-counter-today');

    increaseCounter(counterTotal, countResponsesTotal);
    increaseCounter(counterPersonal, countResponsesPersonal);
    increaseCounter(counterToday, countResponsesToday);

    blinkCalendar();
    blinkStar();
    blinkHeart()
}


/**
 * This function increases a counter by 1 or sets the value to value
 * @param counter: the object that counts in html
 * @param value: the value it should be set at
 */
function increaseCounter(counter, value) {
     if (counter.text() == "") {
         counter.html(value)
    }
    else {
         let countTotalInt = parseInt(counter.text());
         counter.html((countTotalInt + 1).toString())
    }
}


/**
 * this function blinks the hearts in the counter
 */
function blinkHeart() {
    $('.fa-heart-o').addClass("fa-heart").removeClass("fa-heart-o");

    setTimeout(function () {
        $('.fa-heart').addClass("fa-heart-o").removeClass("fa-heart")
    }, 1000)
}


/**
 * This function blinks the stars
 */
function blinkStar() {
    $('.fa-star-o').addClass("fa-star").removeClass("fa-star-o");

    setTimeout(function () {
        $('.fa-star').addClass("fa-star-o").removeClass("fa-star")
    }, 1000)
}


/**
 * This function blinks the calendars
 */
function blinkCalendar() {
    $('.fa-calendar-o').addClass("fa-calendar").removeClass("fa-calendar-o");

    setTimeout(function () {
        $('.fa-calendar').addClass("fa-calendar-o").removeClass("fa-calendar")
    }, 1000)
}


/**
 * This function generates the HTML buttons for a polar question
 * @param: questionId: id of the question
 * @param: possibleAnswers: the possible answers one can pass to the politags api
 */
function generatePolarButtons(questionId, possibleAnswers) {
    let buttonsHtml = '';

    buttonsHtml += '<button id=' + possibleAnswers[0]['id'] + ' question_id=' + questionId + ' type="button" class="btn btn-success responseButton">JA&nbsp</button>\n';
    buttonsHtml += '<button id=' + possibleAnswers[1]['id'] + ' question_id=' + questionId + ' type="button" class="btn btn-danger responseButton">NEE</button>\n';
    buttonsHtml += '<button id=' + possibleAnswers[2]['id'] + ' question_id=' + questionId + ' type="button" class="btn btn-default responseButton">WEET IK NIET</button>\n';


    return buttonsHtml
}


/**
 * This function performs all the actions to show feedback when an entity question is responded to
 */
function showEntityFeedback() {
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

/**
 * This function performs all the actions to show feedback when a topic question is responded to
 */
function showTopicFeedback() {
    $('#topic-content').replaceWith('<div class="panel panel-success" style="margin-top: 5px; margin-bottom: 5px; padding-top: 0px; padding-bottom: 15px; border-radius: 1em; text-align: center; box-shadow: none; border-width: 3px">' +
        '<div id="text" class="panel-body">' + 'Awesome! Samen maken we politiek nieuws beter doorzoekbaar!' + '</div>');

    setTimeout(function () {
        $('#topic_container').slideUp("swing", function () {
            $(this).remove()
        })
    }, 4000)

}

/**
 * This function fills the topic contain
 */
function fillTopicContainer() {
    $('#topic_container').html(
        '    <div id="topic-content">\n' +
        '        <h4>Wat is het onderwerp van het bovenstaande artikel?</h4>\n' +
        '        <div class="input-group">\n' +
        '            <select class="js-example form-control" name="topics[]" multiple="multiple">\n' +
        '            </select>\n' +
        '            <span class="input-group-btn">\n' +
        '                <button class="btn btn-default" id="save" type="button" style="height: 34px">Opslaan</button>\n' +
        '            </span>\n' +
        '        </div>\n' +
        '    </div>\n'
    )
}



/**
 * This function sets a cookie
 * @param cookieName
 * @param cookieValue
 * @param expiryDays
 */
function setCookie(cookieName, cookieValue, expiryDays) {
    var date = new Date();
    date.setTime(date.getTime() + (expiryDays * 24 * 60 * 60 * 1000));
    var expires = "expires=" + date.toUTCString();
    document.cookie = cookieName + "=" + cookieValue + ";" + expires
}


/**
 * This function checks if a certain cooking exists and returns its value
 * @param cookieName: the name of the cookie we want to get
 * @return {string}: the value of the cookie we're searching
 */
function getCookie(cookieName) {
    var name = cookieName + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var ca = decodedCookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1)
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length)
        }
    }
    return ""
}

/**
 * This function gets the cookie ID for the current reader
 * @param cookieName
 */
function getCookieId() {
    var id = getCookie("id");
    if (id === "") {
        setCookie("id", uuidv4(), 10000);
    }
    return id
}

/**
 * This function generates a Unique User ID
 * @return UUID
 */
function uuidv4() {
    return ([1e7] + -1e3 + -4e3 + -8e3 + -1e11).replace(/[018]/g, c =>
        (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
)
}

/**
 * This function adds the unique cookie ID to any object before making an api call
 * @param object: the object to which we want to add the cookie_id
 * @return {*}
 */
function addCookieIdToObject(object) {
    let cookieId = getCookieId();
    object["cookie_id"] = cookieId;
    return object
}

/**
 * This function generates a topic response to process in the backend
 * @param initialTopics: initial topics given by politags
 * @param postedTopics: posted topics given by politags
 * @return topicResponse: response to be given back to backend
 */

function generateTopicResponse(initialTopics, postedTopics) {
    let topicResponse = [];

    for (let i = 0; i < postedTopics.length; i++) {
        topicResponse.push({
                "id": parseInt(postedTopics[i].id),
                "response": parseInt(postedTopics[i].id)
            }
        )
    }

    for (let i = 0; i < initialTopics.length; i++) {
        if (initialTopics[i].selected == true) {
            let topics = $.grep(postedTopics, function (topic) {
                return (topic.id == initialTopics[i].id)
            });
            if (topics.length == 0) {
                topicResponse.push(
                    {
                        "id": parseInt(initialTopics[i].id),
                        "response": -1
                    }
                )
            }
        }
    }
    return topicResponse
}


function deleteTopicQuestion() {
    $('#topic_container').remove()
}


/**
 * Event listeners here
 */

/**
 * This piece of code checks for a click on the responseButton class and posts the response to politags
 */
$('body').on('click', '.responseButton', function () {
        let responseId = $(this).attr("id");

        let answer = {
            "response_id": responseId
        };
        let questionId = $(this).attr("question_id");
        postEntityVerification(answer, questionId)
    }
);

/**
 * This piece of code registers a click on the submit button for topics
 */
$('body').on('click', '#save', function () {
    let postedTopics = $('.js-example').select2('data');
    if (LOGGING) {
        console.log("Topics that are sent to Politags:");
        console.dir(postedTopics);
    }

    postTopicVerification(postedTopics)
    }
);




