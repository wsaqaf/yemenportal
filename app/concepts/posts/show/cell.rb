class Posts::Show::Cell < Application::Cell
  private

  def post
    model
  end

  def topic
    post.topic
  end

  def post_link
    post.link
  end
end
