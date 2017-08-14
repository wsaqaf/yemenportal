document.addEventListener('turbolinks:load', function() {
  $('.js-time').each((_index, element) => {
    let $element = $(element);
    let dayAgo = moment().subtract(1, 'days');
    let timestamp = moment($element.attr('datetime'));

    if (timestamp.isAfter(dayAgo)) {
      $element.text(timestamp.fromNow());
    }
    else {
      $element.text(timestamp.format('lll'));
    }
  });
});
