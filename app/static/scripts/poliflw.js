"use strict";

let article = document.getElementById("article_container");

let articleObject = {{ result |tojson|safe }};

//On opening the website we call the API to receive the question
$(getQuestion());


/**
 * Gets the question for the current article by calling the Politags API and updates html accordingly
 */
function getQuestion() {
    let apiObject = addCookieIdToObject(articleObject)
    $.ajax({
        type: "POST",
        contentType: "application/json",
        url: "http://localhost:5555/api/articles/questions",
        data: JSON.stringify(apiObject),
        success: function (response) {
            console.dir(response)

            if ($.isEmptyObject(response['error']) === true) {

                let question = response['question']
                let questionId = response['question_id']
                let possibleAnswers = response['possible_answers']
                let entityText = response['text']
                let countResponses = response['count_responses']

                highlightEntity(article, entityText, questionId)
                renderQuestion(question, questionId, possibleAnswers)
                updateCounter(countResponses)
            }
            else {
                updateCounter(response['count_responses'])
                console.log(response['error'])
            }
        },

        error: function (error) {
            console.log(error)
        }
    })
}



/**
 * Posts a response to the politags API
 * @param: response: the response to a question
 * @param: questionId: the question that response answers
 */
function postAnswer(answer, questionId) {
    answer = addCookieIdToObject(answer)

    $.ajax({
        type: "POST",
        contentType: "application/json",
        url: "/_answer/" + questionId,
        data: JSON.stringify(answer),
        success: function (response) {
            console.log(response)
            updateCounter()
            showFeedback()
        },
        error: function (error) {
            console.log(error);
        }
    })
}


// everything after this line can be copied from politags.js to make it compatible


/**
 * This piece of code checks for a click on the responseButton class and posts the response to politags
 */
$('body').on('click', '.responseButton', function () {
        let answerId = $(this).attr("id")

        let answer = {
            "answer_id": answerId
        }

        let questionId = $(this).attr("question_id");

        postAnswer(answer, questionId)
    }
);


/**
 * This function highlights an entity in a given html element and saves the question we want to ask for this entity
 * @param: element: the element in which we want to highlight the entity
 * @param: entity: the entity we want to highlight
 * @param: questionId: the questionId we want to store in the highlight so we know later on where to render the question
 */
function highlightEntity(element, entity, questionId) {
    let regexp = new RegExp(entity);
    let replace = '<mark id="' + questionId + '" style="background-color: transparent !important;\n' +
        '            background-image: linear-gradient(to bottom, rgba(189, 228, 255, 1), rgba(189, 228, 255, 1));\n' +
        '            border-radius: 5px;"><strong>' + entity + '</strong></mark>';
    element.innerHTML = element.innerHTML.replace(regexp, replace)
}


/**
 * This function renders a question in the html and presents the possible answers
 * @param: question: the question and its metadata
 * @param: questionId: the id for the question
 * @param: possibleAnswers: the possible answers for this question
 */
function renderQuestion(question, questionId, possibleAnswers) {
    let buttonsHtml = generatePolarButtons(questionId, possibleAnswers);

    $('#' + questionId).parent().after(
        '<div id = "question" class="panel panel-danger" style="margin-top: 5px; margin-bottom: 5px; padding-top: 0px; padding-bottom: 15px; border-radius: 1em; text-align: center; box-shadow: none; border-width: 3px">' +
        '   <div id="text" class="panel-body">' + question +
        '   </div>' +
        buttonsHtml +
        '</div>'
    )
}

/**
 * This function updates the counter based on the amount of recorded responses
 * @param: countResponses: the total amount of responses in the politags database
 */
function updateCounter(countResponses) {
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

/**
 * this function blinks the heart in the counter
 */
function blinkHeart() {
    $('#counter-heart').addClass("fa-heart").removeClass("fa-heart-o");

    setTimeout(function () {
        $('#counter-heart').addClass("fa-heart-o").removeClass("fa-heart")
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

    return buttonsHtml
}

/**
 * This function performs all the actions to show feedback when a question is responded to
 */
function showFeedback() {
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
 * This function sets a cookie
 * @param cookieName
 * @param cookieValue
 * @param expiryDays
 */
function setCookie(cookieName, cookieValue, expiryDays) {
    var date = new Date()
    date.setTime(date.getTime() + (expiryDays * 24 * 60 * 60 * 1000))
    var expires = "expires=" + date.toUTCString()
    document.cookie = cookieName + "=" + cookieValue + ";" + expires
}

/**
 * This function checks if a certain cooking exists and returns its value
 * @param cookieName: the name of the cookie we want to get
 * @return {string}: the value of the cookie we're searching
 */
function getCookie(cookieName) {
    var name = cookieName + "=";
    var decodedCookie = decodeURIComponent(document.cookie)
    var ca = decodedCookie.split(';')
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i]
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
    return ([1e7] + -1e3 + -4e3 + -8e3 + -1e11).replace(/[018]/g, c =
        (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
)
}

/**
 * This function adds the unique cookie ID to any object before making an api call
 * @param object: the object to which we want to add the cookie_id
 * @return {*}
 */
function addCookieIdToObject(object) {
    let cookieId = getCookieId()
    object["cookie_id"] = cookieId
    return object
}


