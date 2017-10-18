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

  property :id, :name, :number_of_reviews_for_post, :color, :review
  option :post

  def button_options
    {
      form_class: ["post-flag", reviewed_by_user_class].join(" "),
      form: { style: "background-color: #{color}" }
    }
  end
end
