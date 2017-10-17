class Posts::Flag::Cell < Application::Cell
  builds do |flag, _options|
    if flag.read_only?
      Posts::Flag::ReadOnly::Cell
    elsif flag.reviewed?
      Posts::Flag::Reviewed::Cell
    else
      Posts::Flag::NotReviewed::Cell
    end
  end

  private

  def flag
    model
  end

  def post
    options[:post]
  end

  def button_options
    {
      form_class: ["topic-flag", reviewed_by_user_class].join(" "),
      form: { style: "background-color: #{flag.color}" }
    }
  end
end
