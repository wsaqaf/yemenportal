class Posts::Post::CommentsCount::Cell < Application::Cell
  private

  attr_reader :post

  def post
    model
  end

  def comments_path
    post_comments_path(post)
  end

  def post_data_url
    post_url(post, protocol: "http")
  end
end
