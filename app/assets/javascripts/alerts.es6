class Alert {
  static fromDocument() {
    $(() => {
      $(".js-alerts__queued-alert").each((_index, element) => {
        new Alert(element.dataset).show();
      });
    });
  }

  static setupCloseButtonHandler() {
    $(document).on("click", ".js-alert__close", (event) => {
      $(event.target).parent(".js-alert").remove();
    });
  }

  constructor(params) {
    this.text = params.text;
    this.type = params.type || "alert";
    this.closeIn = params.closeIn || 8;
  }

  show() {
    this._putAlertElementToDocument();
    if (this.closeIn > 0) {
      this._setTimerToCloseAlert();
    }
  }

  _putAlertElementToDocument() {
    $(".js-alerts__placeholder").after(this._alertElement());
  }

  _alertElement() {
    if (!this.__alertElement) {
      this.__alertElement = this._newlyCreatedAlertElement();
    }
    return this.__alertElement;
  }

  _newlyCreatedAlertElement() {
    return $(`<div class="alerts__alert js-alert callout ${this.type}"></div>`)
      .append(this.text)
      .append(
        $(`<button class="alerts__close-button js-alert__close">&times;</button>`)
      );
  }

  _setTimerToCloseAlert() {
    setTimeout(() => {
      this._alertElement().remove();
    }, this.closeIn * 1000);
  }
}

window.Alert = Alert;
Alert.setupCloseButtonHandler();
Alert.fromDocument();
