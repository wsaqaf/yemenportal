class Posts::Flag::Reviewed::Cell < Posts::Flag::Cell
  private

  def reviewed_by_user_class
    "post-flag--flagged"
  end

  def button
    button_to(post_review_path(post, flag.review), button_options) do
      yield
    end
  end

  def button_options
    super.merge({ method: :delete })
  end
end
