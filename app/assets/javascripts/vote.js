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
        this._markNotVoted();
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
        this._markNotVoted();
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

  get _upvoteClass(){
    return 'upvoted'
  }

  get _downvoteClass(){
    return 'downvoted'
  }

  _isDownvoted() {
    return this.element.hasClass(this._downvoteClass);
  }

  _isUpvoted() {
    return this.element.hasClass(this._upvoteClass);
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
    return this.element.find('.js-vote-count');
  }

  _currentCount() {
    return parseInt(this._counter().text()) || 0;
  }

  _markUpvoted() {
    this.element.removeClass(this._downvoteClass).addClass(this._upvoteClass);
  }

  _markDownvoted() {
    this.element.removeClass(this._upvoteClass).addClass(this._downvoteClass);
  }

  _markNotVoted() {
    this.element.removeClass(this._upvoteClass + ' ' + this._downvoteClass)
  }
}

new VotesController(document).setup();
