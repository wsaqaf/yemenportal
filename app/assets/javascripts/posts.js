class VotesController {
  constructor(document) {
    this.$document = $(document);
  }

  setup() {
    this.$document.on('click', '.js-upvote-button', (event) => {
      event.preventDefault()
      Votable.from(event.target).upvote();
    });

    this.$document.on('click', '.js-downvote-button', (event) => {
      event.preventDefault()
      Votable.from(event.target).downvote();
    });
  }
}

class Votable {
  static from(element) {
    return new this($(element).parents('.js-votable'));
  }

  constructor(votableElement) {
    this.element = votableElement;
  }

  upvote() {
    this._makeVoteRequest(this._upvoteButton())
    .then(() => {
      if (this._isDownvoted()) {
        this._increaseBy(2);
        this._markUpvoted();
      } else if (this._isUpvoted()) {
        this._increaseBy(-1);
        this._markNotUpvoted();
      } else {
        this._increaseBy(1);
        this._markUpvoted();
      }
    });
  }

  downvote() {
    this._makeVoteRequest(this._downvoteButton())
    .then(() => {
      if (this._isUpvoted()) {
        this._increaseBy(-2);
        this._markDownvoted();
      } else if (this._isDownvoted()) {
        this._increaseBy(1);
        this._markNotUpvoted();
      } else {
        this._increaseBy(-1);
        this._markDownvoted();
      }
    });
  }

  _makeVoteRequest($button){
    var request = {
      url: ($button.data().path),
      dataType: "json",
      method: "PUT",
      data: []
    };
    return new Promise((resolve, reject) => {
      $.ajax(request).done((data) => {
        resolve(data);
      });
    });
  }


  _isDownvoted() {
    return this.element.hasClass('downvoted');
  }

  _isUpvoted() {
    return this.element.hasClass('upvoted');
  }

  _downvoteButton() {
    return this.element.find('.js-downvote-button');
  }

  _upvoteButton() {
    return this.element.find('.js-upvote-button');
  }

  _increaseBy(number) {
    this._counter().text(this._currentCount() + number);
  }

  _counter() {
    return this.element.find('.vote_count');
  }

  _currentCount() {
    return parseInt(this._counter().text()) || 0;
  }

  _markUpvoted() {
    this.element.removeClass('downvoted').addClass('upvoted');
  }

  _markDownvoted() {
    this.element.removeClass('upvoted').addClass('downvoted');
  }

  _markNotUpvoted() {
    this.element.removeClass('downvoted')
    this.element.removeClass('upvoted')
  }
}

new VotesController(document).setup();

document.addEventListener("turbolinks:load", function() {
  var oppositeName = {upvote: 'downvote', downvote: 'upvote'};
  var buttonClass = {upvote: 'success', downvote: 'alert'};

  $('select.multiselect').selectize({
    plugins: ['remove_button', 'restore_on_backspace'],
    delimiter: ',',
    persist: false,
    create: function(input) {
      return {
        value: input,
        text: input
      }
    }
  });

  $('.js-post-categories').change(function(){
    var $this = $(this);

    $.ajax({
      url: ("/posts/" + $this.data().id),
      dataType: "script",
      method: "PUT",
      data: {
        category_ids: $this.val()
      }
    });

    return true;
  })



  $('.js-publication-time').each(function() {
    var $this = $(this);
    var day_ago = moment().subtract(1,'days');
    var publiction_time = moment($this.text(), "DD-MM-YYYY hh:mm");

    if (publiction_time.isAfter(day_ago)) {
      $this.text(publiction_time.fromNow());
    } else {
      $this.text(publiction_time.format('lll'));
    }
  });
});
