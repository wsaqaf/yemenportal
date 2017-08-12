class Topics::Flag::Cell < Application::Cell
  builds do |flag, _options|
    if flag.reviewed?
      Topics::Flag::Reviewed::Cell
    else
      Topics::Flag::NotReviewed::Cell
    end
  end

  private

  def flag
    model
  end

  def topic
    options[:topic]
  end

  def button_options
    {
      form_class: ["topic-flag", reviewed_by_user_class].join(" "),
      form: { style: "background-color: #{flag.color}" }
    }
  end
end
