class Posts::Post::ReviewFlags::Cell < Application::Cell
  private

  attr_reader :post

  def post
    model
  end

  def show_review_link?
    post.reviews.empty?
  end

  def review_path
    @_review_path ||= post_reviews_path(post)
  end

  def flags
    @_flags ||= ::Flag.reviewed_flags(post)
  end
end
