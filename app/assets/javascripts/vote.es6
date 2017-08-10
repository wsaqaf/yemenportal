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
    if (this._isUpvoted()) {
      this._makeDeleteVoteRequest().then(() => {
        this._increaseBy(-1);
        this._markNotVoted();
      });
    } else if (this._isDownvoted()) {
      this._makeUpvoteRequest().then(() => {
        this._increaseBy(2);
        this._markUpvoted();
      });
    } else {
      this._makeUpvoteRequest().then(() => {
        this._increaseBy(1);
        this._markUpvoted();
      });
    }
  }

  downvote() {
    if (this._isDownvoted()) {
      this._makeDeleteVoteRequest().then(() => {
        this._increaseBy(1);
        this._markNotVoted();
      });
    } else if (this._isUpvoted()) {
      this._makeDownvoteRequest().then(() => {
        this._increaseBy(-2);
        this._markDownvoted();
      });
    } else {
      this._makeDownvoteRequest().then(() => {
        this._increaseBy(-1);
        this._markDownvoted();
      });
    }
  }

  _makeUpvoteRequest() {
    this._disableVotingButtons();
    return new Promise((resolve, reject) => {
      $.ajax(this._upvoteRequest())
        .always(() => {
          this._enableVotingButtons();
        })
        .done((data) => {
          resolve(data);
        })
        .fail((error) => {
          new Alert({text: error.responseJSON.error}).show();
        });
    });
  }

  _upvoteRequest() {
    return {
      url: this._votePath(),
      dataType: 'json',
      method: 'PATCH',
      data: {type: 'upvote'},
    };
  }

  _makeDownvoteRequest() {
    this._disableVotingButtons();
    return new Promise((resolve, reject) => {
      $.ajax(this._downvoteRequest())
        .always(() => {
          this._enableVotingButtons();
        })
        .done((data) => {
          resolve(data);
        })
        .fail((error) => {
          new Alert({text: error.responseJSON.error}).show();
        });
    });
  }

  _downvoteRequest() {
    return {
      url: this._votePath(),
      dataType: 'json',
      method: 'PATCH',
      data: {type: 'downvote'},
    };
  }

  _makeDeleteVoteRequest() {
    this._disableVotingButtons();
    return new Promise((resolve, reject) => {
      $.ajax(this._deleteVoteRequest()).done((data) => {
        this._enableVotingButtons();
        resolve(data);
      });
    });
  }

  _deleteVoteRequest() {
    return {
      url: this._votePath(),
      dataType: 'json',
      method: 'DELETE',
    };
  }

  _votePath() {
    return this.element.data().votePath;
  }

  _disableVotingButtons() {
    this._upvoteButton().attr('disabled', 'disabled');
    this._downvoteButton().attr('disabled', 'disabled');
  }

  _enableVotingButtons() {
    this._upvoteButton().removeAttr('disabled');
    this._downvoteButton().removeAttr('disabled');
  }

  _isDownvoted() {
    return this.element.hasClass(this._downvoteClass);
  }

  _isUpvoted() {
    return this.element.hasClass(this._upvoteClass);
  }

  _downvoteButton() {
    if (!this.__downvoteButton) {
      this.__downvoteButton = this.element.find('.js-downvote-button');
    }
    return this.__downvoteButton;
  }

  _upvoteButton() {
    if (!this.__upvoteButton) {
      this.__upvoteButton = this.element.find('.js-upvote-button');
    }
    return this.__upvoteButton;
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

  get _upvoteClass(){
    return 'js-upvoted';
  }

  get _downvoteClass(){
    return 'js-downvoted';
  }

  _markNotVoted() {
    this.element.removeClass(this._upvoteClass + ' ' + this._downvoteClass)
  }
}

new VotesController(document).setup();
