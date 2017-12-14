function highlightWordPositions(word) {
    var $paras = $('#article'),
        $spans;


    $paras.each(function(){
        var $article = $(this),
            regex = new RegExp(word, 'g');

        $article.html($article.text().replace(regex, '<span>' + word + '</span>'));
        $spans = $article.find('span');

        $spans.each(function(){
            var $span = $(this),
                $offset = $span.offset(),
                $overlay = $('<div class="overlay"/>');

            $overlay
                .offset($offset)
                .css({
                    width: $span.innerWidth(),
                    height: $span.innerHeight()
                });

            $(document.body).append($overlay)
        });
    });
}

$('#term').keyup(function(event){
    var term = this.value;

    if (term == '') {
        $('.overlay').remove();
        return false;
    } else if (term.indexOf(' ') != -1) {
        this.value = term.replace(' ', '');
        return false;
    }

    $('.overlay').remove();

    highlightWordPositions(term);
});
