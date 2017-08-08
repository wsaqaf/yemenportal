class Topics::Topic::Related::Cell < Application::Cell
  private

  def post
    model
  end

  def title
    post.title.presence || truncate(post.description, length: 80, separator: " ")
  end

  def path_to_post
    if post.show_internally?
      post_path(post)
    else
      post.link
    end
  end
end
