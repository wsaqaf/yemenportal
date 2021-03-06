class Posts::Flag::NotReviewed::Cell < Posts::Flag::Cell
  private

  def reviewed_by_user_class
    "post-flag--unflagged"
  end

  def button
    button_to(post_reviews_path(post), button_options) do
      yield
    end
  end

  def button_options
    super.merge({ method: :post, params: { flag_id: id } })
  end
end
