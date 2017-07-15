class FacebookApi {
  constructor() {
    this._loadSdkOnDomReady();
  }

  saveFbRootBeforeBodyChange(oldBody) {
    this.__fbRoot = oldBody.querySelector('#fb-root');
  }

  restoreFbRootAfterBodyChange(newBody) {
    if (this.__fbRoot) {
      newBody.querySelector('#fb-root').replaceWith(this.__fbRoot);
    }
  }

  parseFbML() {
    if (window.FB) {
      window.FB.XFBML.parse();
    }
  }

  _loadSdkOnDomReady() {
    this._setupAsyncInit();
    $(() => {
      let thisObj = this;
      (function(d, s, id){
         var js, fjs = d.getElementsByTagName(s)[0];
         if (d.getElementById(id)) {return;}
         js = d.createElement(s); js.id = id;
         js.src = `//connect.facebook.net/${thisObj._facebookParams().locale}/sdk.js`;
         fjs.parentNode.insertBefore(js, fjs);
       }(document, 'script', 'facebook-jssdk'));
    });
  }

  _setupAsyncInit() {
    window.fbAsyncInit = () => {
      window.FB.init(this._fbInitParams());
    };
  }

  _fbInitParams() {
    return {
      appId: this._facebookParams().appId,
      autoLogAppEvents: true,
      xfbml: true,
      version: this._facebookParams().apiVersion,
    };
  }

  _facebookParams() {
    if (!this.__facebookParams) {
      this.__facebookParams = document.querySelector('#fb-root').dataset;
    }
    return this.__facebookParams;
  }
}
